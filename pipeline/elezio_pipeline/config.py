"""Configurazione della pipeline: default di docs/pipeline.md, sovrascritti da
pipeline/.env e dalle variabili d'ambiente (in quest'ordine di precedenza)."""

import os
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
RADICE = PIPELINE.parent

DEFAULT = {
    "ELEZIO_LLM_BASE_URL": "https://openrouter.ai/api/v1",
    "ELEZIO_LLM_API_KEY": "",
    "ELEZIO_LLM_PROVIDER": "mistral",
    "ELEZIO_MODELLO_SINTESI": "mistralai/mistral-large-4-0",
    "ELEZIO_MODELLO_CLASSIFICAZIONE": "mistralai/ministral-14b-2512",
    "ELEZIO_MODELLO_OCR": "mistralai/mistral-medium-3-5",
    "ELEZIO_CLASSIFICATORE": "llm",
    "ELEZIO_JEV_API_KEY": "",
    "ELEZIO_TETTO_DOLLARI": "30",
    "ELEZIO_SOGLIA_CLASSIFICAZIONE": "0.5",
}


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
    cfg = dict(DEFAULT)
    for sorgente in (_leggi_env(PIPELINE / ".env"), os.environ):
        cfg.update({k: v for k, v in sorgente.items() if k in DEFAULT and v})
    return cfg
