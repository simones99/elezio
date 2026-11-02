"""Passo 5 della pipeline: classificazione dei passaggi nei temi di v1.

Vedi docs/pipeline.md. Backend `llm`: 20 passaggi per chiamata, prompt con
definizione, sotto-questioni ed esempi dentro/altrove di ogni tema, uscita
JSON strutturata con un punteggio per tema. Il backend `jev` non c'è ancora.
"""

import yaml

from . import config
from .config import PIPELINE
from .llm import ClienteLLM, TettoSuperato  # noqa: F401  (TettoSuperato lo usa anche ocr)

PASSAGGI_PER_CHIAMATA = 20
PROMPT = "classificazione-v2.md"


def carica_temi():
    return yaml.safe_load((config.contenuti() / "temi.yaml").read_text(encoding="utf-8"))


def _descrivi_temi(temi):
    parti = []
    for t in temi:
        righe = [f"## {t['id']}: {t['nome']}", t["definizione"]]
        righe.append("Sotto-questioni: " + "; ".join(t["sotto_questioni"]) + ".")
        righe += [f"- dentro: {x}" for x in t["dentro"]]
        righe += [f"- altrove: {x}" for x in t["altrove"]]
        parti.append("\n".join(righe))
    return "\n\n".join(parti)


def prompt_di_sistema(temi, nome=PROMPT):
    modello = (PIPELINE / "prompts" / nome).read_text(encoding="utf-8")
    return modello.replace("{temi}", _descrivi_temi(temi))


def _schema(temi):
    return {
        "type": "object",
        "properties": {"passaggi": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "temi": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "tema": {"type": "string", "enum": [t["id"] for t in temi]},
                        "punteggio": {"type": "number"},
                    },
                    "required": ["tema", "punteggio"],
                    "additionalProperties": False,
                }},
            },
            "required": ["id", "temi"],
            "additionalProperties": False,
        }}},
        "required": ["passaggi"],
        "additionalProperties": False,
    }


class ClassificatoreLLM:
    """Classificatore su un endpoint compatibile OpenAI (OpenRouter, Ollama, ...)."""

    def __init__(self, cfg, modello=None, temi=None):
        self.llm = ClienteLLM(cfg, modello or cfg["ELEZIO_MODELLO_CLASSIFICAZIONE"])
        self.temi = temi or carica_temi()
        self.sistema = prompt_di_sistema(self.temi)

    @property
    def modello(self):
        return self.llm.modello

    @property
    def costo(self):
        return self.llm.costo

    @property
    def log(self):
        return self.llm.log

    def _chiama(self, gruppo):
        utente = "\n\n".join(f"[{p['id']}] {p['testo']}" for p in gruppo)
        messaggi = [{"role": "system", "content": self.sistema}, {"role": "user", "content": utente}]
        return self.llm.completa(messaggi, "classificazione", _schema(self.temi), passaggi=len(gruppo))["passaggi"]

    def classifica(self, passaggi):
        """{id passaggio: {tema: punteggio}} per tutti i passaggi."""
        esito = {}
        for i in range(0, len(passaggi), PASSAGGI_PER_CHIAMATA):
            gruppo = passaggi[i:i + PASSAGGI_PER_CHIAMATA]
            attesi = {p["id"] for p in gruppo}
            for voce in self._chiama(gruppo):
                if voce["id"] in attesi:
                    esito[voce["id"]] = {t["tema"]: t["punteggio"] for t in voce["temi"]}
            mancanti = attesi - esito.keys()
            if mancanti:  # un secondo giro solo per i passaggi saltati
                for voce in self._chiama([p for p in gruppo if p["id"] in mancanti]):
                    if voce["id"] in mancanti:
                        esito[voce["id"]] = {t["tema"]: t["punteggio"] for t in voce["temi"]}
        return esito
