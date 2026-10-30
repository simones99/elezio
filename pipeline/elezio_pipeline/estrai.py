"""Passi 2 e 4 della pipeline: estrazione del testo e segmentazione in passaggi.

Vedi docs/pipeline.md. Un passaggio è un paragrafo con la sua pagina, spezzato
se supera circa 200 parole. Due ingressi:

- PDF con testo nativo: i confini dei paragrafi si ricavano dalla geometria
  delle righe, perché le copie depositate non marcano i paragrafi;
- scansioni passate da Mistral OCR: il Markdown dell'OCR dà già titoli,
  paragrafi e voci di elenco, e viene tolto dal testo estratto.
"""

import html
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field

import pdfplumber

MAX_PAROLE = 200
# Una riga che finisce prima di questo margine dal bordo destro del testo è
# corta: se chiude anche una frase, chiude il paragrafo.
MARGINE_RIGA_CORTA = 40
# Una riga più grande del corpo del testo di questo fattore è un titolo, se il
# documento marca così i titoli: almeno RIGHE_TITOLO_A_CORPO_MAGGIORE righe
# fuori dalla copertina. Altrimenti i titoli sono le righe in maiuscolo a corpo
# testo.
FATTORE_CORPO_TITOLO = 1.15
RIGHE_TITOLO_A_CORPO_MAGGIORE = 3
# Nei documenti con i titoli a corpo maggiore, uno spazio verticale oltre questo
# multiplo dell'interlinea tipica chiude il paragrafo. Negli altri lo spazio
# separa anche i sottotitoli dal loro paragrafo, e lì non si usa.
FATTORE_STACCO = 1.6

PUNTO_ELENCO = re.compile(r"^(?:o|-|–|—)\s+")
TITOLETTO = "•"  # nei programmi depositati il pallino apre un titoletto
FINE_FRASE = re.compile(r"[.:;!?»”)]$")
NUMERO_PAGINA = re.compile(r"^\d{1,3}$")
SOLO_SIMBOLI = re.compile(r"^[\W_]+$")


@dataclass
class Riga:
    pagina: int
    testo: str
    x1: float
    top: float
    corpo: float  # dimensione mediana dei caratteri


@dataclass
class Passaggio:
    id: str
    pagina: int
    pagina_fine: int
    sezione: str
    testo: str
    righe: list = field(default_factory=list, repr=False)


def leggi_righe(percorso_pdf):
    """Righe del PDF con pagina e bordo destro, senza numeri di pagina e rumore."""
    righe = []
    with pdfplumber.open(percorso_pdf) as pdf:
        for n, pagina in enumerate(pdf.pages, 1):
            for r in pagina.extract_text_lines():
                testo = r["text"].strip()
                if not testo or NUMERO_PAGINA.match(testo) or SOLO_SIMBOLI.match(testo):
                    continue
                corpi = [c["size"] for c in r["chars"] if c["text"].strip()]
                righe.append(Riga(n, testo, r["x1"], r["top"], statistics.median(corpi)))
    return righe


def testo_con_pagine(righe):
    """Testo estratto con i marcatori di pagina, come lo vuole la verifica delle citazioni."""
    out, pagina = [], None
    for r in righe:
        if r.pagina != pagina:
            pagina = r.pagina
            out.append(f"\n=== pagina {pagina} ===")
        out.append(r.testo)
    return "\n".join(out).lstrip() + "\n"


def _bordo_destro(righe):
    """Bordo destro tipico del testo pieno, per pagina."""
    per_pagina = {}
    for r in righe:
        per_pagina.setdefault(r.pagina, []).append(r.x1)
    return {p: sorted(xs)[int(len(xs) * 0.9)] for p, xs in per_pagina.items()}


def _unisci(a, b):
    # trattino di sillabazione a fine riga
    if a.endswith("-") and b[:1].islower():
        return a[:-1] + b
    return a + " " + b


def _spezza(testo):
    """Spezza un paragrafo troppo lungo a fine frase, in pezzi da circa MAX_PAROLE."""
    frasi = re.split(r"(?<=[.;!?])\s+(?=[A-ZÀ-Ý«“\"])", testo)
    pezzi, corrente = [], ""
    for f in frasi:
        if corrente and len((corrente + " " + f).split()) > MAX_PAROLE:
            pezzi.append(corrente)
            corrente = f
        else:
            corrente = f"{corrente} {f}".strip()
    if corrente:
        pezzi.append(corrente)
    return pezzi


def _e_titolo_maiuscolo(testo):
    parole = [p for p in re.findall(r"[^\W\d_]+", testo) if len(p) >= 3]
    return testo.isupper() and len(parole) >= 2 and len(testo.split()) <= 12


def _corpo_testo(righe):
    """Il corpo più usato, pesato sui caratteri."""
    pesi = Counter()
    for r in righe:
        pesi[r.corpo] += len(r.testo)
    return pesi.most_common(1)[0][0]


def _interlinea(righe, corpo):
    """Distanza tipica tra due righe consecutive di testo nella stessa pagina."""
    salti = [b.top - a.top for a, b in zip(righe, righe[1:])
             if a.pagina == b.pagina and a.corpo == b.corpo == corpo and b.top > a.top]
    return statistics.median(salti) if salti else None


def _senza_intestazioni(righe):
    """Toglie intestazioni e piè di pagina: righe identiche su almeno metà delle pagine."""
    pagine_per_testo = {}
    for r in righe:
        pagine_per_testo.setdefault(r.testo, set()).add(r.pagina)
    soglia = max(2, len({r.pagina for r in righe}) / 2)
    return [r for r in righe if len(pagine_per_testo[r.testo]) < soglia]


def segmenta(righe, fonte):
    righe = _senza_intestazioni(righe)
    bordo = _bordo_destro(righe)
    corpo = _corpo_testo(righe)
    soglia_titolo = corpo * FATTORE_CORPO_TITOLO
    titoli_a_corpo_maggiore = (sum(1 for r in righe if r.pagina > 1 and r.corpo > soglia_titolo)
                               >= RIGHE_TITOLO_A_CORPO_MAGGIORE)
    interlinea = _interlinea(righe, corpo) if titoli_a_corpo_maggiore else None

    def e_titolo(r):
        if titoli_a_corpo_maggiore:
            return r.corpo > soglia_titolo
        return _e_titolo_maiuscolo(r.testo)

    paragrafi = []  # (pagina, pagina_fine, sezione, testo)
    sezione, corrente = "", None

    def chiudi():
        nonlocal corrente
        if corrente:
            paragrafi.append(corrente)
        corrente = None

    titolo_aperto = False  # un titolo può andare su più righe
    precedente = None
    for r in righe:
        testo = r.testo
        corta = r.x1 < bordo[r.pagina] - MARGINE_RIGA_CORTA
        # nei documenti con i titoli a corpo maggiore un blocco non attraversa
        # la pagina: il cambio pagina vale come stacco
        cambio_pagina = interlinea and precedente and precedente.pagina != r.pagina
        stacco = cambio_pagina or (interlinea and precedente
                                   and r.top - precedente.top > interlinea * FATTORE_STACCO)
        precedente = r
        if cambio_pagina:
            titolo_aperto = False
        if e_titolo(r) or (titolo_aperto and not titoli_a_corpo_maggiore and testo.isupper()):
            chiudi()
            sezione = f"{sezione} {testo}" if titolo_aperto else testo
            titolo_aperto = True
            continue
        titolo_aperto = False
        if stacco:
            chiudi()
        if testo.startswith(TITOLETTO):
            chiudi()
            testo = testo.lstrip(TITOLETTO).strip()
            # pallino su una riga corta e breve: titoletto; altrimenti voce di elenco
            if corta and len(testo.split()) <= 12 and not testo.endswith(";"):
                sezione = testo.rstrip(".:")
                continue
        elif PUNTO_ELENCO.match(testo):
            chiudi()
            testo = PUNTO_ELENCO.sub("", testo)
        if corrente is None:
            corrente = [r.pagina, r.pagina, sezione, testo]
        else:
            corrente[1] = r.pagina
            corrente[3] = _unisci(corrente[3], testo)
        if corta and FINE_FRASE.search(testo):
            chiudi()
    chiudi()

    passaggi = []
    for pagina, pagina_fine, sez, testo in paragrafi:
        for pezzo in _spezza(testo):
            n = len(passaggi) + 1
            passaggi.append(Passaggio(f"{fonte}-{n:04d}", pagina, pagina_fine, sez, pezzo))
    return passaggi


# --- Markdown di Mistral OCR ---------------------------------------------------

TITOLO_MD = re.compile(r"^#{1,6}\s+(.*)$")
VOCE_MD = re.compile(r"^(?:[-*+]|o|\d{1,2}[.)])\s+")
ATTACCO_ELENCO = re.compile(r"(?i)\bproponiamo\b|\b(?:che|per|quindi)\s*:?$")


def togli_markdown(testo):
    """Testo pulito da una riga di Markdown: enfasi, immagini, tabelle, link."""
    testo = html.unescape(testo)
    testo = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", testo)
    testo = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", testo)
    testo = re.sub(r"\*\*|__|(?<!\w)[*_](?=\S)|(?<=\S)[*_](?!\w)", "", testo)
    testo = testo.replace("|", " ")
    return re.sub(r"\s+", " ", testo).strip()


def blocchi_markdown(pagine):
    """Blocchi (pagina, tipo, testo) dal Markdown per pagina; tipo è titolo, voce o paragrafo."""
    blocchi = []
    for n in sorted(pagine):
        md = re.sub(r"</?file[^>]*>", "", pagine[n])
        for blocco in re.split(r"\n\s*\n", md):
            righe = [r.strip() for r in blocco.strip().splitlines() if r.strip()]
            if not righe:
                continue
            # le voci di elenco consecutive senza riga vuota restano voci distinte
            corrente = None
            for r in righe:
                m = TITOLO_MD.match(r)
                if m:
                    if corrente:
                        blocchi.append(corrente)
                    blocchi.append((n, "titolo", togli_markdown(m.group(1))))
                    corrente = None
                elif VOCE_MD.match(r):
                    if corrente:
                        blocchi.append(corrente)
                    corrente = (n, "voce", togli_markdown(VOCE_MD.sub("", r)))
                elif corrente:
                    corrente = (corrente[0], corrente[1], _unisci(corrente[2], togli_markdown(r)))
                else:
                    corrente = (n, "paragrafo", togli_markdown(r))
            if corrente:
                blocchi.append(corrente)
    return [b for b in blocchi if b[2] and not NUMERO_PAGINA.match(b[2]) and not SOLO_SIMBOLI.match(b[2])]


def testo_con_pagine_md(pagine):
    """Testo estratto dal Markdown, senza markup, con i marcatori di pagina."""
    out, pagina = [], None
    for n, _, testo in blocchi_markdown(pagine):
        if n != pagina:
            pagina = n
            out.append(f"\n=== pagina {n} ===")
        out.append(testo)
    return "\n\n".join(out).lstrip() + "\n"


def segmenta_markdown(pagine, fonte):
    """Passaggi dal Markdown per pagina ({numero: markdown})."""
    paragrafi = []  # [pagina, pagina_fine, sezione, testo]
    sezione = ""
    for n, tipo, testo in blocchi_markdown(pagine):
        if tipo == "titolo":
            # "Per questo proponiamo", "Proponiamo che": attacchi di un elenco
            # che l'OCR marca come titolo; la sezione resta quella di prima
            if not ATTACCO_ELENCO.search(testo):
                sezione = testo.rstrip(".:")
            continue
        precedente = paragrafi[-1] if paragrafi else None
        # paragrafo spezzato dal cambio pagina: la pagina finisce a metà frase
        # e la successiva riprende in minuscolo
        if (precedente and n == precedente[1] + 1 and tipo == "paragrafo"
                and testo[:1].islower() and not FINE_FRASE.search(precedente[3])):
            precedente[1] = n
            precedente[3] = _unisci(precedente[3], testo)
            continue
        paragrafi.append([n, n, sezione, testo])

    passaggi = []
    for pagina, pagina_fine, sez, testo in paragrafi:
        for pezzo in _spezza(testo):
            k = len(passaggi) + 1
            passaggi.append(Passaggio(f"{fonte}-{k:04d}", pagina, pagina_fine, sez, pezzo))
    return passaggi
