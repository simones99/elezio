"""Configurazione della pipeline: pipeline.toml, sovrascritto da pipeline/.env e
dalle variabili d'ambiente (in quest'ordine di precedenza). Vedi docs/pipeline.md."""

import os
import tomllib
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
RADICE = PIPELINE.parent

# chiave di pipeline.toml -> variabile
CHIAVI_TOML = {
    "base_url": "ELEZIO_LLM_BASE_URL",
    "provider": "ELEZIO_LLM_PROVIDER",
    "modello_sintesi": "ELEZIO_MODELLO_SINTESI",
    "modello_classificazione": "ELEZIO_MODELLO_CLASSIFICAZIONE",
    "ocr": "ELEZIO_OCR",
    "classificatore": "ELEZIO_CLASSIFICATORE",
    "tetto_dollari_per_run": "ELEZIO_TETTO_DOLLARI",
    "soglia_classificazione": "ELEZIO_SOGLIA_CLASSIFICAZIONE",
    "fonti": "ELEZIO_FONTI",
    "contenuti": "ELEZIO_CONTENUTI",
}
# solo da .env o dall'ambiente, mai nel file versionato
SEGRETI = ("ELEZIO_LLM_API_KEY", "ELEZIO_JEV_API_KEY")
PERCORSI = ("ELEZIO_FONTI", "ELEZIO_CONTENUTI")


def _leggi_toml(percorso):
    with open(percorso, "rb") as f:
        valori = tomllib.load(f)
    return {CHIAVI_TOML[k]: str(v) for k, v in valori.items()}


def _leggi_env(percorso):
    valori = {}
    if not percorso.exists():
        return valori
    for riga in percorso.read_text(encoding="utf-8").splitlines():
        riga = riga.strip()
        if riga and not riga.startswith("#") and "=" in riga:
            k, v = riga.split("=", 1)
            valori[k.strip()] = v.strip().strip("\"'")
    return valori


def carica():
    """Valori di configurazione; una variabile vuota vale come assente."""
    cfg = dict.fromkeys(SEGRETI, "") | _leggi_toml(PIPELINE / "pipeline.toml")
    for sorgente in (_leggi_env(PIPELINE / ".env"), os.environ):
        cfg.update({k: v for k, v in sorgente.items() if k in cfg and v})
    for k in PERCORSI:
        cfg[k] = str((RADICE / cfg[k]).resolve())  # un percorso assoluto resta com'è
    return cfg


def contenuti():
    """Cartella dei contenuti pubblici: temi, fonti, schede."""
    return Path(carica()["ELEZIO_CONTENUTI"])
