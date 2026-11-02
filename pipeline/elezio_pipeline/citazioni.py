"""Verifica delle citazioni: deterministica, indipendente dal modello (ADR 0005).

Una citazione deve esistere come sottostringa contigua del testo estratto, dopo
una normalizzazione fissa di entrambi i lati, nella pagina indicata o in quella
adiacente. Maiuscole e accenti restano come sono. Regole in docs/pipeline.md.
"""

import re
from dataclasses import dataclass

MARCATORE_PAGINA = re.compile(r"^=== pagina (\d+) ===$", re.M)
INTERVALLO = re.compile(r"^(\d+)-(\d+)$")
# Stessa regola di estrai._unisci: si toglie solo se la riga dopo è minuscola.
SILLABAZIONE = re.compile(r"[-­][ \t]*\r?\n\s*(?=[^\W\d_])")
VIRGOLETTE = str.maketrans({c: '"' for c in "«»“”„‟"} | {c: "'" for c in "‘’‚‛"})
TRATTINI = str.maketrans({c: "-" for c in "‐‑‒–—―−"})


@dataclass
class Esito:
    ok: bool
    pagina: int | str | None = None
    motivo: str = ""


def pagine_del_testo(testo):
    """{numero di pagina: testo} da un testo estratto con i marcatori di pagina."""
    pezzi = MARCATORE_PAGINA.split(testo)
    return {int(n): corpo for n, corpo in zip(pezzi[1::2], pezzi[2::2])}


def _togli_sillabazione(testo):
    def sostituisci(m):
        return "" if testo[m.end()].islower() else m.group(0)
    return SILLABAZIONE.sub(sostituisci, testo)


def normalizza(testo):
    testo = _togli_sillabazione(testo)
    testo = testo.translate(VIRGOLETTE).translate(TRATTINI)
    return " ".join(testo.split())


def _estremi(pagina):
    """(prima, ultima) da un intero o da un intervallo `12-13`; None se non è valida."""
    if isinstance(pagina, bool):
        return None
    if isinstance(pagina, int):
        return pagina, pagina
    m = INTERVALLO.match(str(pagina))
    if m and int(m[1]) <= int(m[2]):
        return int(m[1]), int(m[2])
    return None


def _come_pagina(prima, ultima):
    return prima if prima == ultima else f"{prima}-{ultima}"


def verifica_citazione(pagine, pagina, testo):
    """Esito con la pagina dove la citazione si trova davvero, che può correggere quella data."""
    estremi = _estremi(pagina)
    if estremi is None:
        return Esito(False, motivo=f"pagina {pagina!r} non valida")
    cercata = normalizza(testo)
    if not cercata:
        return Esito(False, motivo="citazione vuota")
    prima, ultima = estremi
    for scarto in (0, -1, 1):
        a, b = prima + scarto, ultima + scarto
        if not all(n in pagine for n in range(a, b + 1)):
            continue
        if cercata in normalizza("\n".join(pagine[n] for n in range(a, b + 1))):
            return Esito(True, _come_pagina(a, b))
    return Esito(False, motivo=f"non trovata a pagina {pagina} né nelle adiacenti")
