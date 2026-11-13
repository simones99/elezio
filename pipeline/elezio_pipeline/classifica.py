"""Passo 5 della pipeline: classificazione dei passaggi nei temi di v1.

Vedi docs/pipeline.md. Backend `llm`: 20 passaggi per chiamata, prompt con
definizione, sotto-questioni ed esempi dentro/altrove di ogni tema, uscita
JSON strutturata con un punteggio per tema. Il backend `jev` non c'è ancora.
"""

import datetime
import json
import shutil

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


REGISTRO = "classificazione.json"
ARCHIVIO = "classificazioni"


def registro(lavoro):
    """Modello, prompt e soglia della classificazione in `passaggi.jsonl`, o None se non registrati."""
    p = lavoro / REGISTRO
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def salva(lavoro, righe, modello, soglia, incompleti):
    """Scrive i passaggi classificati e il loro registro, con una copia in `classificazioni/`.

    La copia non si cancella mai: una bozza nata da questa classificazione la ritrova
    anche dopo un nuovo `pipeline classifica` (docs/pipeline.md, sezione Bozza).
    """
    passaggi = lavoro / "passaggi.jsonl"
    archivio = lavoro / ARCHIVIO
    archivio.mkdir(parents=True, exist_ok=True)
    if registro(lavoro) is None and passaggi.exists() and '"temi"' in passaggi.read_text(encoding="utf-8"):
        # classificazione precedente al registro: si conserva comunque, una bozza può venire da lì
        momento = datetime.datetime.fromtimestamp(passaggi.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
        shutil.copyfile(passaggi, archivio / f"{momento}-senza-registro.jsonl")
    momento = base = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    n = 1
    while (archivio / f"{momento}.jsonl").exists():  # due classificazioni nello stesso secondo
        n += 1
        momento = f"{base}-{n}"
    reg = {"id": momento, "modello": modello, "prompt": PROMPT, "soglia": soglia,
           "data": datetime.date.today().isoformat(), "passaggi": len(righe),
           "incompleti": incompleti, "copia": f"{ARCHIVIO}/{momento}.jsonl"}
    (archivio / f"{momento}.jsonl").write_text("".join(righe), encoding="utf-8")
    with open(passaggi, "w", encoding="utf-8") as f:
        f.writelines(righe)
    (lavoro / REGISTRO).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return reg


def _punteggio_valido(s):
    return isinstance(s, (int, float)) and not isinstance(s, bool) and 0 <= s <= 1


def temi_mancanti(punteggi, temi):
    """I temi senza punteggio: se ce ne sono, il passaggio è incompleto."""
    return {t["id"] for t in temi} - punteggi.keys()


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
        """Le voci della risposta; una risposta rotta vale come nessuna voce."""
        utente = "\n\n".join(f"[{p['id']}] {p['testo']}" for p in gruppo)
        messaggi = [{"role": "system", "content": self.sistema}, {"role": "user", "content": utente}]
        try:
            risposta = self.llm.completa(messaggi, "classificazione", _schema(self.temi), passaggi=len(gruppo))
        except json.JSONDecodeError:
            return []
        voci = risposta.get("passaggi") if isinstance(risposta, dict) else None
        return [v for v in voci if isinstance(v, dict)] if isinstance(voci, list) else []

    def _punteggi_validi(self, punteggi):
        validi = {t["id"] for t in self.temi}
        return {t: s for t, s in punteggi.items() if t in validi and _punteggio_valido(s)}

    def _aggiungi_risposte(self, gruppo, esito):
        """Per ogni passaggio del gruppo tiene la risposta con più punteggi validi."""
        attesi = {p["id"] for p in gruppo}
        for voce in self._chiama(gruppo):
            id_passaggio, punteggi = voce.get("id"), voce.get("punteggi")
            if isinstance(id_passaggio, str) and id_passaggio in attesi and isinstance(punteggi, dict):
                validi = self._punteggi_validi(punteggi)
                if len(validi) >= len(esito.get(id_passaggio, {})):
                    esito[id_passaggio] = validi

    def _incompleti_in(self, passaggi, esito):
        return [p for p in passaggi if temi_mancanti(esito.get(p["id"], {}), self.temi)]

    def classifica(self, passaggi):
        """{id passaggio: {tema: punteggio}}. Lo schema chiede tutti i temi, ma non tutti gli
        endpoint lo rispettano: chi resta senza dopo un nuovo tentativo finisce in `incompleti`."""
        esito = {}
        for i in range(0, len(passaggi), PASSAGGI_PER_CHIAMATA):
            gruppo = passaggi[i:i + PASSAGGI_PER_CHIAMATA]
            self._aggiungi_risposte(gruppo, esito)
            da_ripetere = self._incompleti_in(gruppo, esito)
            if da_ripetere:
                self._aggiungi_risposte(da_ripetere, esito)
        self.incompleti = [p["id"] for p in self._incompleti_in(passaggi, esito)]
        return esito
