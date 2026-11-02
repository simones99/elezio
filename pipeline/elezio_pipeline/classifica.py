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
PROMPT = "classificazione-v3.md"


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
    ids = [t["id"] for t in temi]
    return {
        "type": "object",
        "properties": {"passaggi": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "punteggi": {
                    "type": "object",
                    "properties": {i: {"type": "number"} for i in ids},
                    "required": ids,
                    "additionalProperties": False,
                },
            },
            "required": ["id", "punteggi"],
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
        self.incompleti = []

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

    def _completo(self, punteggi):
        return len(punteggi) == len(self.temi)

    def _raccogli(self, gruppo, esito):
        """Chiama il modello sul gruppo; per ogni passaggio tiene la risposta con più temi."""
        attesi = {p["id"] for p in gruppo}
        validi = {t["id"] for t in self.temi}
        for voce in self._chiama(gruppo):
            if voce["id"] in attesi:
                punteggi = {t: s for t, s in voce["punteggi"].items() if t in validi}
                if len(punteggi) >= len(esito.get(voce["id"], {})):
                    esito[voce["id"]] = punteggi

    def classifica(self, passaggi):
        """{id passaggio: {tema: punteggio}}. Lo schema chiede tutti i temi, ma non tutti gli
        endpoint lo rispettano: chi resta senza dopo un nuovo tentativo finisce in `incompleti`."""
        esito = {}
        for i in range(0, len(passaggi), PASSAGGI_PER_CHIAMATA):
            gruppo = passaggi[i:i + PASSAGGI_PER_CHIAMATA]
            self._raccogli(gruppo, esito)
            da_ripetere = [p for p in gruppo if not self._completo(esito.get(p["id"], {}))]
            if da_ripetere:
                self._raccogli(da_ripetere, esito)
        self.incompleti = [p["id"] for p in passaggi if not self._completo(esito.get(p["id"], {}))]
        return esito
