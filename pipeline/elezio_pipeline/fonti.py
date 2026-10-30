"""Passo 1 della pipeline e verifica dei documenti fonte.

Vedi docs/pipeline.md e docs/schema-scheda.md. L'acquisizione scarica il PDF
nel repo privato `elezio-fonti`, ne calcola SHA-256 e pagine, cerca su Wayback
una copia identica al byte e scrive il YAML della fonte in bozza, che il
maintainer conferma a mano (titolo, tipo, partiti, copia canonica).
"""

import base64
import datetime
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pdfplumber
import yaml

from .config import RADICE

CONTENUTI_FONTI = RADICE / "contenuti" / "fonti"
TIPI = {"programma", "programma_esteso", "accordo_coalizione", "documento_programmatico"}
OCR = {"mistral-ocr", "tesseract"}
OBBLIGATORI = ["id", "titolo", "tipo", "elezione", "partiti", "url", "hash", "acquisito_il", "pagine", "testo_estratto"]
FACOLTATIVI = ["archivio", "data_documento", "copie_equivalenti", "ocr", "ocr_versione"]
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AGENTE = "elezio-pipeline/0.1 (+https://github.com/simones99/elezio)"


def cartella_fonti(cfg):
    return Path(cfg["ELEZIO_FONTI"])


def sha256(dati):
    return hashlib.sha256(dati).hexdigest()


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def ha_testo_nativo(percorso_pdf):
    """Vero se il PDF ha un livello di testo che non è uno strato OCR su una scansione.

    Una pagina con un'immagine che copre quasi tutta la pagina è una scansione,
    anche se sopra c'è del testo (strato OCR incorporato, AVS 2022).
    """
    with pdfplumber.open(percorso_pdf) as pdf:
        scansioni = 0
        parole = 0
        for p in pdf.pages:
            area = p.width * p.height
            if any((i["x1"] - i["x0"]) * (i["bottom"] - i["top"]) > 0.8 * area for i in p.images):
                scansioni += 1
            parole += len((p.extract_text() or "").split())
        n = len(pdf.pages)
    return scansioni <= n // 4 and parole / n >= 50


def copia_wayback(url, dati):
    """Prima copia su Wayback identica al byte (digest SHA-1), oppure None."""
    sha1 = base64.b32encode(hashlib.sha1(dati).digest()).decode()
    q = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode({
        "url": url, "output": "json", "filter": "statuscode:200",
        "fl": "timestamp,original,digest", "limit": "3000"})
    for attesa in (15, 30, None):
        try:
            req = urllib.request.Request(q, headers={"User-Agent": AGENTE})
            righe = json.load(urllib.request.urlopen(req, timeout=90))[1:]
            break
        except OSError:
            if attesa is None:
                raise
            time.sleep(attesa)
    uguali = sorted(r for r in righe if r[2] == sha1)
    return f"https://web.archive.org/web/{uguali[0][0]}/{uguali[0][1]}" if uguali else None


def acquisisci(cfg, url, fonte, partiti, elezione, tipo, copia_di=None):
    """Scarica il PDF e scrive (o aggiorna) il YAML della fonte in bozza.

    Con `copia_di` il PDF è un'altra copia depositata dello stesso documento:
    finisce in pdf/<fonte>--<partito>.pdf e in `copie_equivalenti`.
    """
    dati = scarica(url)
    pdf_dir = cartella_fonti(cfg) / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    nome = f"{copia_di}--{partiti[0]}" if copia_di else fonte
    percorso = pdf_dir / f"{nome}.pdf"
    percorso.write_bytes(dati)
    voce = {"hash": sha256(dati), "archivio": copia_wayback(url, dati)}
    if copia_di:
        y = leggi(copia_di)
        copie = [c for c in y.get("copie_equivalenti", []) if c["partito"] != partiti[0]]
        copie.append({"url": url, "hash": voce["hash"], "partito": partiti[0]})
        y["copie_equivalenti"] = copie
        scrivi(y)
        return percorso
    with pdfplumber.open(percorso) as pdf:
        pagine = len(pdf.pages)
    y = {
        "id": fonte,
        "titolo": "DA CONFERMARE",
        "tipo": tipo,
        "elezione": elezione,
        "partiti": partiti,
        "url": url,
        "hash": voce["hash"],
        "acquisito_il": datetime.date.today(),
        "archivio": voce["archivio"],
        "pagine": pagine,
        "testo_estratto": f"testo/{fonte}.txt",
    }
    if not ha_testo_nativo(percorso):
        # senza chiave Mistral OCR non parte: la fonte nasce con il ripiego
        y["ocr"] = cfg["ELEZIO_OCR"] if cfg["ELEZIO_LLM_API_KEY"] else "tesseract"
    scrivi({k: v for k, v in y.items() if v is not None})
    return percorso


def leggi(fonte):
    return yaml.safe_load((CONTENUTI_FONTI / f"{fonte}.yaml").read_text(encoding="utf-8"))


def scrivi(y):
    CONTENUTI_FONTI.mkdir(parents=True, exist_ok=True)
    ordine = OBBLIGATORI + FACOLTATIVI
    y = {k: y[k] for k in sorted(y, key=lambda k: ordine.index(k) if k in ordine else len(ordine))}
    testo = yaml.safe_dump(y, sort_keys=False, allow_unicode=True, width=1000)
    (CONTENUTI_FONTI / f"{y['id']}.yaml").write_text(testo, encoding="utf-8")


def _errori(percorso, y, fonti_dir):
    e = []
    for k in OBBLIGATORI:
        if k not in y:
            e.append(f"manca {k}")
    for k in y:
        if k not in OBBLIGATORI and k not in FACOLTATIVI:
            e.append(f"campo sconosciuto {k}")
    if e:
        return e
    if y["id"] != percorso.stem or not SLUG.match(y["id"]):
        e.append("id diverso dal nome del file o non è uno slug")
    if y["tipo"] not in TIPI:
        e.append(f"tipo {y['tipo']} non ammesso")
    if not isinstance(y["elezione"], int):
        e.append("elezione non è un anno")
    if not y["partiti"] or not all(isinstance(p, str) and SLUG.match(p) for p in y["partiti"]):
        e.append("partiti vuoto o con slug non validi")
    if not str(y["url"]).startswith("https://"):
        e.append("url non https")
    if not re.fullmatch(r"[0-9a-f]{64}", str(y["hash"])):
        e.append("hash non è uno SHA-256")
    if not isinstance(y["acquisito_il"], datetime.date):
        e.append("acquisito_il non è una data")
    if not isinstance(y["pagine"], int) or y["pagine"] < 1:
        e.append("pagine non valide")
    if y.get("ocr") is not None and y["ocr"] not in OCR:
        e.append(f"ocr {y['ocr']} non ammesso")
    if "ocr_versione" in y and "ocr" not in y:
        e.append("ocr_versione senza ocr")
    if "archivio" in y and not str(y["archivio"]).startswith("https://web.archive.org/web/"):
        e.append("archivio non è una copia Wayback")
    for c in y.get("copie_equivalenti", []):
        if set(c) != {"url", "hash", "partito"} or c["partito"] not in y["partiti"]:
            e.append(f"copia equivalente non valida: {c}")
    if fonti_dir is None:
        return e
    # con il repo privato a disposizione: PDF, testo estratto e pagine
    pdf = fonti_dir / "pdf" / f"{y['id']}.pdf"
    if not pdf.exists():
        e.append(f"manca {pdf.name} in elezio-fonti")
    elif sha256(pdf.read_bytes()) != y["hash"]:
        e.append("hash diverso dal PDF in elezio-fonti")
    testo = fonti_dir / y["testo_estratto"]
    if not testo.exists():
        e.append(f"manca {y['testo_estratto']} in elezio-fonti")
    else:
        marcate = {int(n) for n in re.findall(r"^=== pagina (\d+) ===$", testo.read_text(encoding="utf-8"), re.M)}
        if not marcate or max(marcate) > y["pagine"]:
            e.append("marcatori di pagina oltre il numero di pagine")
    return e


def verifica(cfg):
    """Errori dei YAML delle fonti, {nome file: [errori]}; vuoto se va tutto bene."""
    fonti_dir = cartella_fonti(cfg)
    fonti_dir = fonti_dir if fonti_dir.exists() else None
    esito = {}
    for p in sorted(CONTENUTI_FONTI.glob("*.yaml")):
        e = _errori(p, yaml.safe_load(p.read_text(encoding="utf-8")), fonti_dir)
        if e:
            esito[p.name] = e
    return esito, fonti_dir
