"""Passi 6-7 della pipeline: dai passaggi di un tema alla scheda in bozza.

Il modello restituisce JSON e la pipeline scrive i file (ADR 0005). Una citazione
che non passa la verifica non entra mai in una scheda: si scarta, il modello
riprova una volta e se fallisce ancora il problema finisce nelle note.
"""

import datetime
import json

from . import classifica, fonti, schede
from .citazioni import pagine_del_testo, verifica_citazione
from .config import PIPELINE
from .llm import ClienteLLM

PROMPT = "bozza-v1.md"
CORPO_ASSENTE = "Il documento fonte di questo partito non tratta il tema."
SCHEMA = {
    "type": "object",
    "properties": {
        "posizione": {"type": "string", "enum": ["dichiarata", "assente"]},
        "titolo": {"type": "string"},
        "sintesi": {"type": "string"},
        "citazioni": {"type": "array", "items": {
            "type": "object",
            "properties": {"pagina": {"type": "integer"}, "testo": {"type": "string"}},
            "required": ["pagina", "testo"],
            "additionalProperties": False,
        }},
    },
    "required": ["posizione", "titolo", "sintesi", "citazioni"],
    "additionalProperties": False,
}


class BozzaImpossibile(RuntimeError):
    pass


def _descrivi_tema(t):
    righe = [f"{t['id']}: {t['nome']}", t["definizione"],
             "Sotto-questioni, in ordine:", *[f"- {s}" for s in t["sotto_questioni"]],
             "Esempi dentro il tema:", *[f"- {x}" for x in t["dentro"]],
             "Esempi che stanno altrove:", *[f"- {x}" for x in t["altrove"]]]
    return "\n".join(righe)


def _messaggi(tema, passaggi):
    sistema = (PIPELINE / "prompts" / PROMPT).read_text(encoding="utf-8").replace("{tema}", _descrivi_tema(tema))
    blocchi = []
    for p in passaggi:
        sezione = f", sezione: {p['sezione']}" if p.get("sezione") else ""
        blocchi.append(f"[pagina {p['pagina']}{sezione}]\n{p['testo']}")
    return [{"role": "system", "content": sistema}, {"role": "user", "content": "\n\n".join(blocchi)}]


def _difetto_struttura(r):
    """Cosa rende inservibile la risposta anche senza guardare le citazioni, o None."""
    if not isinstance(r, dict) or r.get("posizione") not in ("dichiarata", "assente"):
        return "la risposta non ha una posizione valida"
    if r["posizione"] == "assente":
        return None
    if not str(r.get("titolo") or "").strip() or not str(r.get("sintesi") or "").strip():
        return "una posizione dichiarata deve avere titolo e sintesi"
    return None


def _controlla_citazioni(risposta, pagine):
    """(citazioni valide con la pagina corretta, problemi)."""
    valide, problemi = [], []
    for c in risposta.get("citazioni") or []:
        esito = verifica_citazione(pagine, c.get("pagina"), str(c.get("testo") or ""))
        if esito.ok:
            valide.append({"pagina": esito.pagina, "testo": c["testo"]})
        else:
            problemi.append(f"citazione scartata, {esito.motivo}: «{c.get('testo')}»")
    parole = sum(len(c["testo"].split()) for c in valide)
    if parole > schede.MAX_PAROLE_CITAZIONI:
        problemi.append(f"le citazioni fanno {parole} parole, il massimo è {schede.MAX_PAROLE_CITAZIONI}")
    if not valide and not problemi:
        problemi.append("una posizione dichiarata deve avere almeno una citazione")
    return valide, problemi


def _chiedi(llm, messaggi):
    """La risposta del modello; None se non è JSON."""
    try:
        return llm.completa(messaggi, "bozza", SCHEMA)
    except json.JSONDecodeError:
        return None


def _correzione(risposta, difetti):
    testo = "La risposta non va bene:\n" + "\n".join(f"- {d}" for d in difetti)
    testo += "\nRiscrivi tutta la risposta. Ogni citazione va copiata alla lettera da un solo passaggio ricevuto."
    return [{"role": "assistant", "content": json.dumps(risposta, ensure_ascii=False)},
            {"role": "user", "content": testo}]


def _esamina(risposta, pagine):
    """(difetti, citazioni valide). I difetti sono quelli da far correggere al modello."""
    difetto = "la risposta non è JSON valido" if risposta is None else _difetto_struttura(risposta)
    if difetto:
        return [difetto], []
    if risposta["posizione"] == "assente":
        return [], []
    valide, problemi = _controlla_citazioni(risposta, pagine)
    return problemi, valide


def _genera(llm, tema, passaggi, pagine):
    """(risposta finale, citazioni valide, note): con un solo nuovo tentativo."""
    messaggi = _messaggi(tema, passaggi)
    risposta = _chiedi(llm, messaggi)
    difetti, valide = _esamina(risposta, pagine)
    if not difetti:
        return risposta, valide, []
    risposta = _chiedi(llm, messaggi + _correzione(risposta, difetti))
    difetti, valide = _esamina(risposta, pagine)
    if risposta is None or _difetto_struttura(risposta):
        raise BozzaImpossibile(f"risposta del modello non valida anche al secondo tentativo: {difetti[0]}")
    note = list(difetti)
    if risposta["posizione"] == "assente":
        note.append("assente solo al secondo tentativo, dopo una risposta scartata: "
                    "controllare che la posizione non sia in realtà dichiarata")
    return risposta, valide, note


def _fronte(partito, tema, y, posizione, titolo, citazioni, note, bozza_da):
    f = {"partito": partito, "tema": tema["id"], "elezione": y["elezione"], "posizione": posizione}
    if posizione == "dichiarata":
        f["titolo"] = titolo
    f["citazioni"] = [{"fonte": y["id"], "pagina": c["pagina"], "testo": c["testo"]} for c in citazioni]
    f["stato"] = "bozza"
    f["aggiornata_il"] = datetime.date.today()
    if bozza_da:
        f["bozza_da"] = bozza_da
    if note:
        f["note"] = "; ".join(note)
    return f


def _stati(y, tema_id):
    """{partito: stato della scheda già scritta, o None se la scheda non c'è}."""
    stati = {}
    for partito in y["partiti"]:
        p = schede.percorso(y["elezione"], partito, tema_id)
        stati[partito] = schede.leggi(p)[0].get("stato") if p.exists() else None
    return stati


def gia_fatta(fonte, tema_id):
    """"revisionata" se tutte le schede della coppia sono passate dal revisore, "scritta" se
    esistono tutte, None se ne manca almeno una: allora la coppia si genera."""
    stati = _stati(fonti.leggi(fonte), tema_id)
    if all(s not in (None, "bozza") for s in stati.values()):
        _annuncia(stati, tema_id)
        return "revisionata"
    if all(s is not None for s in stati.values()):
        return "scritta"
    return None


def _annuncia(stati, tema_id):
    for p, stato in stati.items():
        if stato not in (None, "bozza"):
            print(f"{p}/{tema_id}: scheda in stato {stato}, non la tocco")


class Lancio:
    """Un lancio di `pipeline bozze`: un solo client, quindi un solo tetto di spesa per
    tutte le coppie, creato alla prima coppia che chiama il modello."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.log = []
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = ClienteLLM(self.cfg, self.cfg["ELEZIO_MODELLO_SINTESI"])
            self._llm.log = self.log
        return self._llm

    @property
    def costo(self):
        return self._llm.costo if self._llm else 0.0


def _salva(base, fonte, tema_id, reg, risposta, bozza_da):
    """Accanto alla bozza, nel repo privato: la risposta del modello e la classificazione da cui nasce."""
    salvata = base / "lavoro" / fonte / "bozze" / f"{tema_id}.json"
    salvata.parent.mkdir(parents=True, exist_ok=True)
    dati = {"bozza_da": bozza_da, "classificazione": reg, "risposta": risposta}
    salvata.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def genera(lancio, fonte, tema_id, passaggi):
    """Scrive le schede del tema per i partiti della fonte e restituisce l'esito:
    "dichiarata", "assente" o "revisionata" se nessuna scheda era da scrivere.

    Le chiamate finiscono in `lancio.log`, anche se il passo si ferma a metà. Senza passaggi
    del tema la posizione è assente e il modello non viene chiamato, a meno che qualche
    passaggio non abbia il punteggio del tema: allora l'assenza non è dimostrata e il
    passo si ferma con BozzaImpossibile. Senza il registro della classificazione si ferma
    anche: la bozza non saprebbe da quale classificazione è nata.
    """
    tema = next((t for t in classifica.carica_temi() if t["id"] == tema_id), None)
    if tema is None:
        raise BozzaImpossibile(f"tema {tema_id} inesistente")
    if any("temi" not in p for p in passaggi):
        raise BozzaImpossibile(f"{fonte}: passaggi non classificati, lancia prima pipeline classifica")
    y = fonti.leggi(fonte)
    stati = _stati(y, tema_id)
    _annuncia(stati, tema_id)
    partiti = [p for p, s in stati.items() if s in (None, "bozza")]
    if not partiti:
        return "revisionata"
    base = fonti.cartella_fonti(lancio.cfg)
    reg = classifica.registro(base / "lavoro" / fonte)
    if reg is None:
        raise BozzaImpossibile(f"{fonte}: la classificazione non dice modello, prompt e soglia, "
                               "rilancia pipeline classifica")
    del_tema = [p for p in passaggi if tema_id in p["temi"]]
    id_senza_punteggio = [p["id"] for p in passaggi if classifica.temi_mancanti(p.get("punteggi", {}), [tema])]
    if not del_tema:
        if id_senza_punteggio:  # l'assenza non è dimostrata: la scheda direbbe più di quello che si sa
            raise BozzaImpossibile("nessun passaggio assegnato, ma questi non hanno il punteggio del tema: "
                                   + ", ".join(id_senza_punteggio)
                                   + "; scheda non scritta, rilancia pipeline classifica")
        _salva(base, fonte, tema_id, reg, None, None)
        for partito in partiti:
            schede.scrivi(schede.percorso(y["elezione"], partito, tema_id),
                          _fronte(partito, tema, y, "assente", "", [],
                                  ["il classificatore non ha assegnato al tema nessun passaggio"], None),
                          CORPO_ASSENTE)
        return "assente"
    pagine = pagine_del_testo((base / y["testo_estratto"]).read_text(encoding="utf-8"))
    llm = lancio.llm
    risposta, valide, note = _genera(llm, tema, del_tema, pagine)
    if id_senza_punteggio:
        note.append("passaggi senza il punteggio del tema, da controllare: " + ", ".join(id_senza_punteggio))
    bozza_da = {"modello": llm.modello, "prompt": PROMPT}
    _salva(base, fonte, tema_id, reg, risposta, bozza_da)
    assente = risposta["posizione"] == "assente"
    for partito in partiti:
        schede.scrivi(schede.percorso(y["elezione"], partito, tema_id),
                      _fronte(partito, tema, y, risposta["posizione"], risposta.get("titolo"), valide, note, bozza_da),
                      CORPO_ASSENTE if assente else risposta["sintesi"].strip())
    return risposta["posizione"]
