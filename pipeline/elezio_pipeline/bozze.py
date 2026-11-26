"""Passi 6-7 della pipeline: dai passaggi di un tema alla scheda in bozza.

Il modello restituisce JSON e la pipeline scrive i file (ADR 0005). Una citazione
che non passa la verifica non entra mai in una scheda: si scarta, il modello
riprova una volta e se fallisce ancora il problema finisce nelle note.
"""

import datetime
import json

import yaml

from . import classifica, fonti, schede
from .citazioni import pagine_del_testo, verifica_citazione
from .config import PIPELINE
from .llm import ClienteLLM

PROMPT = "bozza-v2.md"
CORPO_ASSENTE = "Il documento fonte di questo partito non tratta il tema."
# Il valore che il modello usa per una citazione fuori dalle sotto-questioni del tema: l'output
# strutturato vuole tutti i campi, nella scheda diventa campo assente (riga "Altro nel tema").
ALTRO = "altro"


def _schema(tema):
    """Lo schema JSON della risposta, con le sotto-questioni del tema come valori ammessi."""
    return {
        "type": "object",
        "properties": {
            "posizione": {"type": "string", "enum": ["dichiarata", "assente"]},
            "titolo": {"type": "string"},
            "sintesi": {"type": "string"},
            "citazioni": {"type": "array", "items": {
                "type": "object",
                "properties": {"pagina": {"type": "integer"},
                               "sotto_questione": {"type": "string", "enum": [*tema["sotto_questioni"], ALTRO]},
                               "testo": {"type": "string"}},
                "required": ["pagina", "sotto_questione", "testo"],
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
            valide.append({"pagina": esito.pagina, "sotto_questione": c.get("sotto_questione"), "testo": c["testo"]})
        else:
            problemi.append(f"citazione scartata, {esito.motivo}: «{c.get('testo')}»")
    parole = sum(len(c["testo"].split()) for c in valide)
    if parole > schede.MAX_PAROLE_CITAZIONI:
        problemi.append(f"le citazioni fanno {parole} parole, il massimo è {schede.MAX_PAROLE_CITAZIONI}")
    if not valide and not problemi:
        problemi.append("una posizione dichiarata deve avere almeno una citazione")
    return valide, problemi


def _chiedi(llm, messaggi, tema):
    """La risposta del modello; None se non è JSON."""
    try:
        return llm.completa(messaggi, "bozza", _schema(tema))
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
    risposta = _chiedi(llm, messaggi, tema)
    difetti, valide = _esamina(risposta, pagine)
    if not difetti:
        return risposta, valide, []
    risposta = _chiedi(llm, messaggi + _correzione(risposta, difetti), tema)
    difetti, valide = _esamina(risposta, pagine)
    if risposta is None or _difetto_struttura(risposta):
        raise BozzaImpossibile(f"risposta del modello non valida anche al secondo tentativo: {difetti[0]}")
    note = list(difetti)
    if risposta["posizione"] == "assente":
        note.append("assente solo al secondo tentativo, dopo una risposta scartata: "
                    "controllare che la posizione non sia in realtà dichiarata")
    return risposta, valide, note


def _sotto_questioni(citazioni, tema):
    """(citazioni con la sotto-questione solo se è del tema, note sui valori scartati).

    "altro" e un valore mancante lasciano la citazione senza sotto-questione; un valore che
    il tema non ha si toglie e lo si dice al revisore, senza far riprovare il modello."""
    pulite, note = [], []
    for c in citazioni:
        sq = c.get("sotto_questione")
        if sq not in (None, ALTRO) and sq not in tema["sotto_questioni"]:
            note.append(f"sotto-questione «{sq}» non è del tema, tolta dalla citazione: «{c['testo']}»")
        pulite.append({k: v for k, v in c.items()
                       if k != "sotto_questione" or v in tema["sotto_questioni"]})
    return pulite, note


def _citazione(y, c):
    """La citazione della scheda, nell'ordine dei campi di docs/schema-scheda.md."""
    d = {"fonte": y["id"], "pagina": c["pagina"]}
    if c.get("sotto_questione"):
        d["sotto_questione"] = c["sotto_questione"]
    d["testo"] = c["testo"]
    return d


def _fronte(partito, tema, y, posizione, titolo, citazioni, note, bozza_da):
    f = {"partito": partito, "tema": tema["id"], "elezione": y["elezione"], "posizione": posizione}
    if posizione == "dichiarata":
        f["titolo"] = titolo
    f["citazioni"] = [_citazione(y, c) for c in citazioni]
    f["stato"] = "bozza"
    f["aggiornata_il"] = datetime.date.today()
    if bozza_da:
        f["bozza_da"] = bozza_da
    if note:
        f["note"] = "; ".join(note)
    return f


CAMPI_FONTE = ("id", "elezione", "partiti", "testo_estratto")


def _leggi_fonte(fonte):
    """Il YAML della fonte, con i campi che servono alle bozze; BozzaImpossibile se non si legge."""
    try:
        y = fonti.leggi(fonte)
    except (OSError, yaml.YAMLError) as e:
        raise BozzaImpossibile(f"{fonte}: YAML della fonte illeggibile: {e}") from e
    if not isinstance(y, dict):
        raise BozzaImpossibile(f"{fonte}: YAML della fonte vuoto")
    mancanti = [k for k in CAMPI_FONTE if not y.get(k)]
    if mancanti or not isinstance(y["partiti"], list):
        raise BozzaImpossibile(f"{fonte}: YAML della fonte senza " + ", ".join(mancanti or ["un elenco di partiti"]))
    return y


def _stati(y, tema_id):
    """{partito: stato della scheda già scritta, o None se la scheda non c'è}."""
    stati = {}
    for partito in y["partiti"]:
        p = schede.percorso(y["elezione"], partito, tema_id)
        if not p.exists():
            stati[partito] = None
            continue
        try:
            stati[partito] = schede.leggi(p)[0].get("stato")
        except (ValueError, yaml.YAMLError) as e:  # una scheda rotta non si sovrascrive senza guardarla
            raise BozzaImpossibile(f"scheda {partito}/{tema_id} illeggibile, correggila a mano: {e}") from e
    return stati


def gia_fatta(fonte, tema_id):
    """"revisionata" se tutte le schede della coppia sono passate dal revisore, "scritta" se
    esistono tutte, None se ne manca almeno una: allora la coppia si genera."""
    stati = _stati(_leggi_fonte(fonte), tema_id)
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


def _scrivi(base, fonte, y, tema_id, partito, fronte, corpo, record):
    """Scrive la scheda del partito e subito dopo, nel repo privato, il suo record: risposta
    del modello, `bozza_da` e registro della classificazione da cui nasce.

    Il record è uno per partito, in `lavoro/<fonte>/bozze/<tema>/<partito>.json`: su una fonte
    condivisa la scheda di un partito generata dopo non tocca il record di quelle già
    scritte, e un errore a metà dei partiti non lascia record di schede non scritte (#77).
    """
    schede.scrivi(schede.percorso(y["elezione"], partito, tema_id), fronte, corpo)
    salvato = base / "lavoro" / fonte / "bozze" / tema_id / f"{partito}.json"
    salvato.parent.mkdir(parents=True, exist_ok=True)
    salvato.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def genera(lancio, fonte, tema_id, passaggi, rigenera=False):
    """Scrive le schede del tema per i partiti della fonte e restituisce l'esito:
    "dichiarata", "assente", oppure "revisionata" o "scritta" se nessuna scheda era da scrivere.

    Scrive solo le schede che mancano; con `rigenera` riscrive anche quelle in bozza. Le
    schede verificate e contestate non si toccano mai. Su una fonte condivisa quindi una
    bozza già scritta di un partito resta com'è anche se si genera quella di un altro.

    Sotto la soglia `ELEZIO_DOCUMENTO_INTERO_SOTTO_PAROLE` del testo estratto il modello riceve
    tutti i passaggi della fonte e decide lui se il tema c'è (#42); il record lo dice in `ingresso`.

    Le chiamate finiscono in `lancio.log`, anche se il passo si ferma a metà. Sopra la soglia,
    senza passaggi del tema la posizione è assente e il modello non viene chiamato, a meno che qualche
    passaggio non abbia il punteggio del tema: allora l'assenza non è dimostrata e il
    passo si ferma con BozzaImpossibile. Senza il registro della classificazione si ferma
    anche: la bozza non saprebbe da quale classificazione è nata.
    """
    tema = next((t for t in classifica.carica_temi() if t["id"] == tema_id), None)
    if tema is None:
        raise BozzaImpossibile(f"tema {tema_id} inesistente")
    if any("temi" not in p for p in passaggi):
        raise BozzaImpossibile(f"{fonte}: passaggi non classificati, lancia prima pipeline classifica")
    y = _leggi_fonte(fonte)
    stati = _stati(y, tema_id)
    _annuncia(stati, tema_id)
    da_scrivere = (None, "bozza") if rigenera else (None,)
    partiti = [p for p, s in stati.items() if s in da_scrivere]
    for p, s in stati.items():
        if s == "bozza" and not rigenera:
            print(f"{p}/{tema_id}: bozza già scritta, non la tocco (--rigenera per rifarla)")
    if not partiti:
        return "scritta" if "bozza" in stati.values() else "revisionata"
    base = fonti.cartella_fonti(lancio.cfg)
    reg = classifica.registro(base / "lavoro" / fonte)
    if reg is None:
        raise BozzaImpossibile(f"{fonte}: la classificazione non dice modello, prompt e soglia, "
                               "rilancia pipeline classifica")
    testo = (base / y["testo_estratto"]).read_text(encoding="utf-8")
    if len(testo.split()) < int(lancio.cfg["ELEZIO_DOCUMENTO_INTERO_SOTTO_PAROLE"]):
        # documento breve: il modello legge tutto, una classificazione persa non fa un'assenza falsa
        ingresso, inviati, id_senza_punteggio = "documento_intero", passaggi, []
    else:
        ingresso = "passaggi_classificati"
        inviati = [p for p in passaggi if tema_id in p["temi"]]
        id_senza_punteggio = [p["id"] for p in passaggi
                              if classifica.temi_mancanti(p.get("punteggi", {}), [tema])]
    if not inviati:
        if id_senza_punteggio:  # l'assenza non è dimostrata: la scheda direbbe più di quello che si sa
            raise BozzaImpossibile("nessun passaggio assegnato, ma questi non hanno il punteggio del tema: "
                                   + ", ".join(id_senza_punteggio)
                                   + "; scheda non scritta, rilancia pipeline classifica")
        record = {"bozza_da": None, "ingresso": ingresso, "classificazione": reg, "risposta": None}
        for partito in partiti:
            _scrivi(base, fonte, y, tema_id, partito,
                    _fronte(partito, tema, y, "assente", "", [],
                            ["il classificatore non ha assegnato al tema nessun passaggio"], None),
                    CORPO_ASSENTE, record)
        return "assente"
    pagine = pagine_del_testo(testo)
    llm = lancio.llm
    risposta, valide, note = _genera(llm, tema, inviati, pagine)
    valide, note_sq = _sotto_questioni(valide, tema)
    note += note_sq
    if id_senza_punteggio:
        note.append("passaggi senza il punteggio del tema, da controllare: " + ", ".join(id_senza_punteggio))
    bozza_da = {"modello": llm.modello, "prompt": PROMPT}
    record = {"bozza_da": bozza_da, "ingresso": ingresso, "classificazione": reg, "risposta": risposta}
    assente = risposta["posizione"] == "assente"
    for partito in partiti:
        _scrivi(base, fonte, y, tema_id, partito,
                _fronte(partito, tema, y, risposta["posizione"], risposta.get("titolo"), valide, note, bozza_da),
                CORPO_ASSENTE if assente else risposta["sintesi"].strip(), record)
    return risposta["posizione"]
