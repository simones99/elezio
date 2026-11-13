"""Client unico per i passi con un modello, su un endpoint compatibile OpenAI.

Tiene in un punto solo il blocco del provider per la residenza dell'inferenza,
il conteggio dei costi e il tetto di spesa per run (docs/pipeline.md). Il tetto
vale solo dove l'endpoint restituisce il costo della chiamata: altrove si avvisa.
"""

import json
import time

from openai import OpenAI, RateLimitError


class TettoSuperato(RuntimeError):
    pass


class ClienteLLM:
    def __init__(self, cfg, modello):
        if not cfg["ELEZIO_LLM_API_KEY"]:
            raise RuntimeError("ELEZIO_LLM_API_KEY vuota: i passi con un modello non partono")
        self.cfg = cfg
        self.modello = modello
        self.client = OpenAI(base_url=cfg["ELEZIO_LLM_BASE_URL"], api_key=cfg["ELEZIO_LLM_API_KEY"])
        self.tetto = float(cfg["ELEZIO_TETTO_DOLLARI"])
        self.costo = 0.0
        self.log = []
        self.avvisato_senza_costo = False

    def _extra(self):
        extra = {"usage": {"include": True}}
        if "openrouter.ai" in self.cfg["ELEZIO_LLM_BASE_URL"] and self.cfg["ELEZIO_LLM_PROVIDER"]:
            # residenza dell'inferenza: niente instradamento su altri host
            extra["provider"] = {"order": [self.cfg["ELEZIO_LLM_PROVIDER"]],
                                 "allow_fallbacks": False, "zdr": True}
        return extra

    def _crea(self, messaggi, nome, schema):
        return self.client.chat.completions.create(
            model=self.modello,
            temperature=0,
            messages=messaggi,
            response_format={"type": "json_schema", "json_schema": {
                "name": nome, "strict": True, "schema": schema}},
            extra_body=self._extra(),
        )

    def completa(self, messaggi, nome, schema, **da_registrare):
        """Il JSON della risposta. Si ferma prima della chiamata se il tetto è raggiunto."""
        if self.costo >= self.tetto:
            raise TettoSuperato(f"tetto di {self.tetto} dollari raggiunto")
        for attesa in (15, 30, 60, None):  # il provider risponde 429 anche a metà run
            try:
                risposta = self._crea(messaggi, nome, schema)
                break
            except RateLimitError:
                if attesa is None:
                    raise
                time.sleep(attesa)
        uso = risposta.usage.model_dump() if risposta.usage else {}
        if uso.get("cost") is None and not self.avvisato_senza_costo:
            # solo OpenRouter restituisce il costo: altrove resterebbe a 0 e il tetto non scatterebbe mai
            self.avvisato_senza_costo = True
            print(f"{self.modello}: l'endpoint non restituisce il costo, il tetto di spesa non è attivo "
                  "e il costo riportato non conta queste chiamate")
        self.costo += uso.get("cost") or 0.0
        self.log.append({"modello": self.modello, **da_registrare, "usage": uso})
        # contenuto nullo (rifiuto, risposta troncata): vale come JSON rotto, i chiamanti lo gestiscono già
        return json.loads(risposta.choices[0].message.content or "")
