"""Passo 5 della pipeline: classificazione dei passaggi nei temi di v1.

Vedi docs/pipeline.md. Backend `llm`: 20 passaggi per chiamata, prompt con
definizione, sotto-questioni ed esempi dentro/altrove di ogni tema, uscita
JSON strutturata con un punteggio per tema. Il backend `jev` non c'è ancora.
"""

import json
import time

import yaml
from openai import OpenAI, RateLimitError

from .config import PIPELINE, RADICE

PASSAGGI_PER_CHIAMATA = 20
PROMPT = "classificazione-v2.md"


class TettoSuperato(RuntimeError):
    pass


def carica_temi(percorso=RADICE / "contenuti" / "temi.yaml"):
    return yaml.safe_load(percorso.read_text(encoding="utf-8"))


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
        if not cfg["ELEZIO_LLM_API_KEY"]:
            raise RuntimeError("ELEZIO_LLM_API_KEY vuota: la classificazione non parte")
        self.cfg = cfg
        self.modello = modello or cfg["ELEZIO_MODELLO_CLASSIFICAZIONE"]
        self.temi = temi or carica_temi()
        self.sistema = prompt_di_sistema(self.temi)
        self.client = OpenAI(base_url=cfg["ELEZIO_LLM_BASE_URL"], api_key=cfg["ELEZIO_LLM_API_KEY"])
        self.tetto = float(cfg["ELEZIO_TETTO_DOLLARI"])
        self.costo = 0.0
        self.log = []

    def _extra(self):
        extra = {"usage": {"include": True}}
        if "openrouter.ai" in self.cfg["ELEZIO_LLM_BASE_URL"] and self.cfg["ELEZIO_LLM_PROVIDER"]:
            # residenza dell'inferenza: niente instradamento su altri host
            extra["provider"] = {"order": [self.cfg["ELEZIO_LLM_PROVIDER"]],
                                 "allow_fallbacks": False, "zdr": True}
        return extra

    def _chiama(self, gruppo):
        utente = "\n\n".join(f"[{p['id']}] {p['testo']}" for p in gruppo)
        for attesa in (15, None):
            try:
                risposta = self._completa(utente)
                break
            except RateLimitError:
                if attesa is None:
                    raise
                time.sleep(attesa)
        uso = risposta.usage.model_dump() if risposta.usage else {}
        self.costo += uso.get("cost") or 0.0
        self.log.append({"modello": self.modello, "passaggi": len(gruppo), "usage": uso})
        return json.loads(risposta.choices[0].message.content)["passaggi"]

    def _completa(self, utente):
        return self.client.chat.completions.create(
            model=self.modello,
            temperature=0,
            messages=[{"role": "system", "content": self.sistema},
                      {"role": "user", "content": utente}],
            response_format={"type": "json_schema", "json_schema": {
                "name": "classificazione", "strict": True, "schema": _schema(self.temi)}},
            extra_body=self._extra(),
        )

    def classifica(self, passaggi):
        """{id passaggio: {tema: punteggio}} per tutti i passaggi."""
        esito = {}
        for i in range(0, len(passaggi), PASSAGGI_PER_CHIAMATA):
            if self.costo >= self.tetto:
                raise TettoSuperato(f"tetto di {self.tetto} dollari raggiunto")
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
