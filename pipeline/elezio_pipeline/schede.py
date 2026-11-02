"""File delle schede e loro controlli (docs/schema-scheda.md).

Percorso: `contenuti/schede/<elezione>/<partito>/<tema>.md`. Qui stanno i vincoli
che chiedono il testo estratto o l'incrocio tra file; quelli sul singolo file
tornano negli schemi zod del sito.
"""

import datetime

import yaml

from . import config
from .citazioni import pagine_del_testo, verifica_citazione

MAX_PAROLE_CITAZIONI = 300
POSIZIONI = {"dichiarata", "assente"}
STATI = {"bozza", "verificata", "contestata"}
OBBLIGATORI = ["partito", "tema", "elezione", "posizione", "citazioni", "stato", "aggiornata_il"]
FACOLTATIVI = ["titolo", "verificata_il", "revisore", "bozza_da", "note"]


def cartella():
    return config.contenuti() / "schede"


def percorso(elezione, partito, tema):
    return cartella() / str(elezione) / partito / f"{tema}.md"


def leggi(p):
    """(frontmatter, corpo) di un file scheda. ValueError se il frontmatter non c'è."""
    testo = p.read_text(encoding="utf-8")
    if not testo.startswith("---\n") or "\n---\n" not in testo:
        raise ValueError("frontmatter mancante")
    fronte, corpo = testo[4:].split("\n---\n", 1)
    return yaml.safe_load(fronte), corpo.strip()


def scrivi(p, fronte, corpo):
    p.parent.mkdir(parents=True, exist_ok=True)
    testo = yaml.safe_dump(fronte, sort_keys=False, allow_unicode=True, width=1000)
    p.write_bytes(f"---\n{testo}---\n\n{corpo}\n".encode("utf-8"))


def _errori_campi(f, corpo):
    e = [f"manca {k}" for k in OBBLIGATORI if k not in f]
    e += [f"campo sconosciuto {k}" for k in f if k not in OBBLIGATORI and k not in FACOLTATIVI]
    if f.get("posizione") not in POSIZIONI:
        e.append(f"posizione {f.get('posizione')} non ammessa")
    if f.get("stato") not in STATI:
        e.append(f"stato {f.get('stato')} non ammesso")
    if "aggiornata_il" in f and not isinstance(f["aggiornata_il"], datetime.date):
        e.append("aggiornata_il non è una data")
    if f.get("stato") in ("verificata", "contestata"):
        if not isinstance(f.get("verificata_il"), datetime.date):
            e.append("verificata_il manca o non è una data")
        if not f.get("revisore"):
            e.append("manca revisore")
    if f.get("posizione") == "dichiarata":
        if not f.get("titolo"):
            e.append("posizione dichiarata senza titolo")
        if not f.get("citazioni"):
            e.append("posizione dichiarata senza citazioni")
    if f.get("posizione") == "assente":
        if f.get("titolo"):
            e.append("posizione assente con titolo")
        if f.get("citazioni"):
            e.append("posizione assente con citazioni")
    if not corpo:
        e.append("manca la sintesi nel corpo")
    return e


def _errori_percorso(f, p, temi):
    elezione, partito, tema = p.parent.parent.name, p.parent.name, p.stem
    e = []
    if f.get("partito") != partito:
        e.append(f"partito {f.get('partito')} diverso dalla cartella {partito}")
    if f.get("tema") != tema:
        e.append(f"tema {f.get('tema')} diverso dal nome del file {tema}")
    if str(f.get("elezione")) != elezione:
        e.append(f"elezione {f.get('elezione')} diversa dalla cartella {elezione}")
    if tema not in temi:
        e.append(f"tema {tema} inesistente")
    return e


def _errori_citazioni(f, fonti_yaml, testi):
    e = []
    parole = 0
    visti = set()
    for c in f.get("citazioni") or []:
        id_ = c.get("id")
        if id_ is not None:
            if id_ in visti:
                e.append(f"id di citazione duplicato: {id_}")
            visti.add(id_)
        for k in ("fonte", "pagina", "testo"):
            if k not in c:
                e.append(f"citazione senza {k}")
        testo = str(c.get("testo") or "")
        parole += len(testo.split())
        y = fonti_yaml.get(c.get("fonte"))
        if y is None:
            e.append(f"fonte {c.get('fonte')} inesistente")
            continue
        if f.get("partito") not in y["partiti"]:
            e.append(f"la fonte {y['id']} non include il partito {f.get('partito')}")
        if f.get("elezione") != y["elezione"]:
            e.append(f"la fonte {y['id']} è dell'elezione {y['elezione']}, la scheda della {f.get('elezione')}")
        pagine = testi(y)
        if pagine is not None and "pagina" in c:
            esito = verifica_citazione(pagine, c["pagina"], testo)
            if not esito.ok:
                e.append(f"citazione {esito.motivo}: «{testo}»")
    if parole > MAX_PAROLE_CITAZIONI:
        e.append(f"le citazioni fanno {parole} parole, il massimo è {MAX_PAROLE_CITAZIONI}")
    return e


def verifica(temi, fonti_yaml, fonti_dir):
    """Errori delle schede, {percorso relativo: [errori]}; vuoto se va tutto bene.

    Senza il repo privato (`fonti_dir` None) non controlla il testo delle citazioni.
    """
    base = cartella()
    cache = {}

    def testi(y):
        if fonti_dir is None:
            return None
        if y["id"] not in cache:
            testo = fonti_dir / y["testo_estratto"]
            cache[y["id"]] = pagine_del_testo(testo.read_text(encoding="utf-8")) if testo.exists() else {}
        return cache[y["id"]]

    esito = {}
    for p in sorted(base.glob("*/*/*.md")):
        try:
            f, corpo = leggi(p)
        except (ValueError, yaml.YAMLError) as ex:
            esito[p.relative_to(base).as_posix()] = [str(ex)]
            continue
        e = _errori_campi(f, corpo) + _errori_percorso(f, p, temi) + _errori_citazioni(f, fonti_yaml, testi)
        if e:
            esito[p.relative_to(base).as_posix()] = e
    return esito
