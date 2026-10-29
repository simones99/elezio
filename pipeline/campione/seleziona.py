"""Selezione del campione d'oro AVS 2022 (vedi docs/pipeline.md, ticket #28).

Ingresso: i passaggi segmentati da Mistral OCR (`segmenta_markdown`), un JSON
per riga, dal repo privato. Popolazione: i passaggi con almeno 6 parole.

- Lotto 1 (60): 48 passaggi stratificati per sezione, quota proporzionale e
  almeno 1 per le sezioni con 5 passaggi o più, più 12 casi limite, uno per
  confine di temi.yaml. Seme 28.
- Lotto 2 (60): un secondo caso limite per confine, quando il programma ne ha
  un altro; poi stratificati fino a 120, con le quote ricalcolate sul totale
  degli stratificati e tolto quanto già preso nel lotto 1. Seme 29.

Uso: python seleziona.py <passaggi.jsonl> <uscita.json>
"""

import collections
import json
import math
import random
import re
import sys

SEME = 28
TOTALE = 120
STRATIFICATI_LOTTO_1 = 48

CONFINI = [
    ("bonus edilizi ed efficienza: fisco, ambiente o casa", r"(?i)superbonus|bonus edilizi|ecobonus|detrazion\w* .*efficien|efficientamento"),
    ("caro energia e tetto al prezzo: ambiente o fisco", r"(?is)^(?!.*extraprofitt).*(bollett|tetto al prezzo|caro energia|povert\w* energetic)"),
    ("extraprofitti energetici: fisco o ambiente", r"(?i)extraprofitt"),
    ("agricoltura: imprese o ambiente", r"(?i)agricol|canapa"),
    ("sostegno al reddito: famiglia o lavoro", r"(?i)reddito di cittadinanza|reddito minimo|sostegno al reddito"),
    ("non autosufficienza: famiglia o sanità", r"(?i)non autosufficien|assistenza domiciliare|\bRSA\b"),
    ("psicologo a scuola: sanità o scuola", r"(?i)psicolog\w* .*scuol|scuol\w* .*psicolog"),
    ("autonomia differenziata: istituzioni o scuola", r"(?i)autonomia differenziata"),
    ("trasporto pubblico: casa o ambiente", r"(?i)trasporto pubblico|ferrovi|pendolar"),
    ("ecomafie e reati ambientali: giustizia o ambiente", r"(?i)ecomafi|reati ambientali|ecocidio"),
    ("migranti e regole UE: immigrazione o europa", r"(?i)dublino|redistribuz\w* .*migran|frontex|libia"),
    ("benessere animale: fuori da v1", r"(?i)benessere animale|animali d.affezione|\bcaccia\b|randagi"),
]


def quote(per_sez, n_pop, n):
    """Quote proporzionali per sezione che sommano a n (metodo dei resti più alti)."""
    quota = {s: n * len(v) / n_pop for s, v in per_sez.items()}
    alloc = {s: max(1 if len(per_sez[s]) >= 5 else 0, math.floor(q)) for s, q in quota.items()}
    resto = sorted(per_sez, key=lambda s: quota[s] - math.floor(quota[s]), reverse=True)
    i = 0
    while sum(alloc.values()) < n:
        s = resto[i % len(resto)]
        if alloc[s] < len(per_sez[s]):
            alloc[s] += 1
        i += 1
    while sum(alloc.values()) > n:  # troppi minimi: togli dalle sezioni più sopra quota
        s = max(alloc, key=lambda s: alloc[s] - quota[s])
        alloc[s] -= 1
    return alloc


def casi_limite(pop, rng, presi):
    out = []
    for nome, rx in CONFINI:
        cand = [p for p in pop if re.search(rx, p["testo"]) and p["id"] not in presi]
        if not cand:
            print("nessun candidato:", nome, file=sys.stderr)
            continue
        p = rng.choice(cand)
        presi.add(p["id"])
        out.append((nome, p))
    return out


def seleziona(passaggi):
    pop = [p for p in passaggi if len(p["testo"].split()) >= 6]
    per_sez = collections.defaultdict(list)
    for p in pop:
        per_sez[p["sezione"]].append(p)

    rng = random.Random(SEME)
    a = quote(per_sez, len(pop), STRATIFICATI_LOTTO_1)
    strat1 = []
    for s in sorted(per_sez):
        strat1 += rng.sample(per_sez[s], a[s])
    presi = {p["id"] for p in strat1}
    lim1 = casi_limite(pop, rng, presi)

    rng2 = random.Random(SEME + 1)
    lim2 = casi_limite(pop, rng2, presi)
    n_strat = TOTALE - len(lim1) - len(lim2)
    a = quote(per_sez, len(pop), n_strat)
    gia = collections.Counter(p["sezione"] for p in strat1)
    mancanti = {s: max(0, a[s] - gia[s]) for s in per_sez}
    eccesso = sum(mancanti.values()) - (n_strat - len(strat1))
    while eccesso > 0:  # sezioni già sopra quota nel lotto 1: togli dalle più grandi
        s = max(mancanti, key=lambda s: (mancanti[s], len(per_sez[s])))
        mancanti[s] -= 1
        eccesso -= 1
    strat2 = []
    for s in sorted(per_sez):
        liberi = [p for p in per_sez[s] if p["id"] not in presi]
        strat2 += rng2.sample(liberi, min(mancanti[s], len(liberi)))

    def voce(p, lotto, confine=None):
        v = {k: p[k] for k in ("id", "pagina", "pagina_fine", "sezione", "testo")}
        v["origine"] = "caso limite" if confine else "stratificato"
        if confine:
            v["confine"] = confine
        v["lotto"] = lotto
        return v

    scelti = ([voce(p, 1) for p in strat1] + [voce(p, 1, n) for n, p in lim1]
              + [voce(p, 2) for p in strat2] + [voce(p, 2, n) for n, p in lim2])
    return sorted(scelti, key=lambda v: v["id"])


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        passaggi = [json.loads(r) for r in f if r.strip()]
    scelti = seleziona(passaggi)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(scelti, f, ensure_ascii=False, indent=1)
    conta = collections.Counter((v["lotto"], v["origine"]) for v in scelti)
    print(len(scelti), "passaggi:", dict(sorted(conta.items())))
