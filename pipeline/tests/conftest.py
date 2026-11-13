"""Cartelle di prova e modello finto: un vero server HTTP locale, così i test
passano dal client vero e dalla riga di comando vera, senza toccare gli interni."""

import hashlib
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import yaml

FONTE = "2022-prova-programma"
SENZA_CONTENUTO = object()  # in coda alle risposte: il modello risponde con `content` nullo

TEMI = [
    {"id": "sanita", "nome": "Sanità", "definizione": "Servizio sanitario nazionale.",
     "sotto_questioni": ["Personale sanitario", "Salute mentale"],
     "dentro": ["Psicologo di base"], "altrove": ["Fine vita (giustizia)"]},
    {"id": "fisco", "nome": "Fisco", "definizione": "Tasse e imposte.",
     "sotto_questioni": ["Imposte sul reddito"],
     "dentro": ["Riforma dell'Irpef"], "altrove": ["Salario minimo (lavoro)"]},
]

TESTO_ESTRATTO = """=== pagina 1 ===
Introduzione generale al programma.

=== pagina 2 ===
AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO
Uno psicologo di base in ogni distretto.

=== pagina 3 ===
Riforma dell'Irpef con tre aliquote.
"""

PASSAGGI = [
    {"id": f"{FONTE}-0001", "pagina": 1, "pagina_fine": 1, "sezione": None,
     "testo": "Introduzione generale al programma."},
    {"id": f"{FONTE}-0002", "pagina": 2, "pagina_fine": 2, "sezione": "SALUTE",
     "testo": "AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO"},
    {"id": f"{FONTE}-0003", "pagina": 2, "pagina_fine": 2, "sezione": "SALUTE",
     "testo": "Uno psicologo di base in ogni distretto."},
    {"id": f"{FONTE}-0004", "pagina": 3, "pagina_fine": 3, "sezione": "FISCO",
     "testo": "Riforma dell'Irpef con tre aliquote."},
]


class ModelloFinto:
    """Risponde alle chiamate con le risposte in coda e ricorda le richieste."""

    def __init__(self):
        self.risposte = []
        self.richieste = []
        self.costo = 0.001
        finto = self

        class Gestore(BaseHTTPRequestHandler):
            def do_POST(self):
                corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                finto.richieste.append(corpo)
                contenuto = finto.risposte.pop(0)
                if contenuto is SENZA_CONTENUTO:
                    contenuto = None
                elif not isinstance(contenuto, str):
                    contenuto = json.dumps(contenuto, ensure_ascii=False)
                uso = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
                if finto.costo is not None:  # None: un endpoint che non dice il costo, come api.mistral.ai
                    uso["cost"] = finto.costo
                dati = json.dumps({
                    "id": "finta", "object": "chat.completion", "created": 0, "model": corpo["model"],
                    "choices": [{"index": 0, "finish_reason": "stop",
                                 "message": {"role": "assistant", "content": contenuto}}],
                    "usage": uso,
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(dati)))
                self.end_headers()
                self.wfile.write(dati)

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Gestore)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_port}/v1"

    def chiudi(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def modello():
    finto = ModelloFinto()
    yield finto
    finto.chiudi()


class Progetto:
    def __init__(self, contenuti, fonti_dir):
        self.contenuti = contenuti
        self.fonti_dir = fonti_dir

    @property
    def percorso_passaggi(self):
        return self.fonti_dir / "lavoro" / FONTE / "passaggi.jsonl"

    def passaggi(self):
        return [json.loads(r) for r in self.percorso_passaggi.read_text(encoding="utf-8").splitlines()]

    def scrivi_passaggi(self, passaggi):
        self.percorso_passaggi.write_text(
            "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in passaggi), encoding="utf-8")

    def scheda(self, partito="prova", tema="sanita", elezione=2022):
        return self.contenuti / "schede" / str(elezione) / partito / f"{tema}.md"

    def leggi_scheda(self, **kw):
        _, fronte, corpo = self.scheda(**kw).read_text(encoding="utf-8").split("---\n", 2)
        return yaml.safe_load(fronte), corpo.strip()

    def scrivi_scheda(self, fronte, corpo="Una sintesi.", partito=None, tema=None, elezione=None):
        p = self.scheda(partito or fronte["partito"], tema or fronte["tema"], elezione or fronte["elezione"])
        p.parent.mkdir(parents=True, exist_ok=True)
        testo = yaml.safe_dump(fronte, sort_keys=False, allow_unicode=True)
        p.write_text(f"---\n{testo}---\n\n{corpo}\n", encoding="utf-8")


@pytest.fixture
def progetto(tmp_path, monkeypatch, modello):
    """Contenuti e repo privato di prova, con la configurazione che punta lì."""
    contenuti, fonti_dir = tmp_path / "contenuti", tmp_path / "elezio-fonti"
    (contenuti / "fonti").mkdir(parents=True)
    (contenuti / "temi.yaml").write_text(yaml.safe_dump(TEMI, allow_unicode=True), encoding="utf-8")
    pdf = b"%PDF finto"
    for cartella in ("pdf", "testo", f"lavoro/{FONTE}"):
        (fonti_dir / cartella).mkdir(parents=True)
    (fonti_dir / "pdf" / f"{FONTE}.pdf").write_bytes(pdf)
    (fonti_dir / "testo" / f"{FONTE}.txt").write_text(TESTO_ESTRATTO, encoding="utf-8")
    (contenuti / "fonti" / f"{FONTE}.yaml").write_text(yaml.safe_dump({
        "id": FONTE, "titolo": "Programma di prova", "tipo": "programma", "elezione": 2022,
        "partiti": ["prova"], "url": "https://esempio.invalid/programma.pdf",
        "hash": hashlib.sha256(pdf).hexdigest(), "acquisito_il": "2026-10-30", "pagine": 3,
        "testo_estratto": f"testo/{FONTE}.txt",
    }).replace("acquisito_il: '2026-10-30'", "acquisito_il: 2026-10-30"), encoding="utf-8")
    p = Progetto(contenuti, fonti_dir)
    p.scrivi_passaggi(PASSAGGI)
    for k, v in {
        "ELEZIO_CONTENUTI": str(contenuti), "ELEZIO_FONTI": str(fonti_dir),
        "ELEZIO_LLM_BASE_URL": modello.url, "ELEZIO_LLM_API_KEY": "finta",
        "ELEZIO_MODELLO_CLASSIFICAZIONE": "finto/classifica", "ELEZIO_MODELLO_SINTESI": "finto/sintesi",
        "ELEZIO_TETTO_DOLLARI": "30", "ELEZIO_SOGLIA_CLASSIFICAZIONE": "0.2",
        "NO_PROXY": "127.0.0.1",
    }.items():
        monkeypatch.setenv(k, v)
    return p
