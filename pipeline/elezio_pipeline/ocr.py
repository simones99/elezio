"""Passo 3 della pipeline: OCR delle scansioni, una pagina per chiamata.

Vedi docs/pipeline.md, sezione OCR. Default Mistral OCR via OpenRouter: plugin
`file-parser` con `engine: mistral-ocr`, un PDF di una pagina per chiamata,
testo letto dalle `annotations` della risposta. Il modello della chiamata non
genera nulla (`max_tokens` 1): si paga il plugin. Il ripiego Tesseract senza
chiave non è ancora collegato qui; l'immagine è in pipeline/docker/tesseract.
"""

import base64
import io
import time

from openai import OpenAI, RateLimitError
from pypdf import PdfReader, PdfWriter

from .classifica import TettoSuperato

# il plugin fa l'OCR, il modello serve solo a portare la richiesta
MODELLO_VEICOLO = "mistralai/ministral-3b-2512"


def pdf_di_una_pagina(lettore, n):
    w = PdfWriter()
    w.add_page(lettore.pages[n - 1])
    b = io.BytesIO()
    w.write(b)
    return b.getvalue()


class MistralOCR:
    def __init__(self, cfg):
        if not cfg["ELEZIO_LLM_API_KEY"]:
            raise RuntimeError("ELEZIO_LLM_API_KEY vuota: Mistral OCR non parte")
        if "openrouter.ai" not in cfg["ELEZIO_LLM_BASE_URL"]:
            raise RuntimeError("Mistral OCR passa dal plugin file-parser di OpenRouter")
        self.cfg = cfg
        self.client = OpenAI(base_url=cfg["ELEZIO_LLM_BASE_URL"], api_key=cfg["ELEZIO_LLM_API_KEY"])
        self.tetto = float(cfg["ELEZIO_TETTO_DOLLARI"])
        self.costo = 0.0
        self.log = []

    def _richiesta(self, nome, dati):
        url = "data:application/pdf;base64," + base64.b64encode(dati).decode()
        # risposta grezza: le annotations del plugin non sono nei tipi dell'SDK
        return self.client.chat.completions.with_raw_response.create(
            model=MODELLO_VEICOLO,
            max_tokens=1,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "ok"},
                {"type": "file", "file": {"filename": nome, "file_data": url}}]}],
            extra_body={
                "plugins": [{"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}],
                "provider": {"order": [self.cfg["ELEZIO_LLM_PROVIDER"]], "allow_fallbacks": False, "zdr": True},
                "usage": {"include": True},
            },
        ).http_response.json()

    def pagina(self, nome, dati):
        """Markdown di Mistral OCR per un PDF di una pagina."""
        if self.costo >= self.tetto:
            raise TettoSuperato(f"tetto di {self.tetto} dollari raggiunto")
        for attesa in (15, None):
            try:
                r = self._richiesta(nome, dati)
                break
            except RateLimitError:
                if attesa is None:
                    raise
                time.sleep(attesa)
        uso = r.get("usage") or {}
        self.costo += uso.get("cost") or 0.0
        self.log.append({"file": nome, "provider": r.get("provider"), "usage": uso})
        parti = []
        for a in r["choices"][0]["message"].get("annotations") or []:
            for c in a.get("file", {}).get("content", []):
                if c.get("type") == "text":
                    parti.append(c["text"])
        return "\n\n".join(parti)


def ocr_pdf(percorso_pdf, cartella, cfg, ocr=None):
    """Una pagina alla volta in <cartella>/pNNN.md; le pagine già fatte si saltano."""
    if cfg["ELEZIO_OCR"] != "mistral-ocr":
        raise RuntimeError(f"OCR {cfg['ELEZIO_OCR']}: per ora solo mistral-ocr")
    ocr = ocr or MistralOCR(cfg)
    cartella.mkdir(parents=True, exist_ok=True)
    lettore = PdfReader(percorso_pdf)
    for n in range(1, len(lettore.pages) + 1):
        uscita = cartella / f"p{n:03d}.md"
        if uscita.exists():
            continue
        md = ocr.pagina(f"{percorso_pdf.stem}-p{n:03d}.pdf", pdf_di_una_pagina(lettore, n))
        uscita.write_text(md, encoding="utf-8")
    return ocr


def leggi_pagine(cartella):
    """{numero: markdown} dalle pagine OCR salvate."""
    return {int(p.stem[1:]): p.read_text(encoding="utf-8") for p in sorted(cartella.glob("p*.md"))}
