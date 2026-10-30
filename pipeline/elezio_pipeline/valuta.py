"""`pipeline valuta-classificatore`: precisione e richiamo per tema sul campione d'oro.

Vedi docs/pipeline.md. Il backend con il richiamo migliore diventa il default;
sotto il 90 percento di richiamo nessun backend passa senza revisione umana.
"""

import json

from .config import PIPELINE

CAMPIONE = PIPELINE / "campione" / "avs-2022.jsonl"
SOGLIA_RICHIAMO = 0.9


def carica_campione(percorso=CAMPIONE):
    with open(percorso, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def _rapporto(num, den):
    return num / den if den else None


def misura(campione, previsti, temi, soglia):
    """Conteggi e metriche per tema e complessive (micro), a una soglia di punteggio."""
    per_tema = {t: {"vp": 0, "fp": 0, "fn": 0} for t in temi}
    for p in campione:
        veri = set(p["temi"])
        presi = {t for t, s in previsti.get(p["id"], {}).items() if s >= soglia}
        for t in temi:
            c = per_tema[t]
            c["vp"] += t in veri and t in presi
            c["fp"] += t not in veri and t in presi
            c["fn"] += t in veri and t not in presi
    for c in per_tema.values():
        c["precisione"] = _rapporto(c["vp"], c["vp"] + c["fp"])
        c["richiamo"] = _rapporto(c["vp"], c["vp"] + c["fn"])
    tot = {k: sum(c[k] for c in per_tema.values()) for k in ("vp", "fp", "fn")}
    tot["precisione"] = _rapporto(tot["vp"], tot["vp"] + tot["fp"])
    tot["richiamo"] = _rapporto(tot["vp"], tot["vp"] + tot["fn"])
    return per_tema, tot


def _pct(x):
    return "  n.d." if x is None else f"{x * 100:5.1f}%"


def stampa(nome, per_tema, tot):
    print(f"\n{nome}")
    print(f"  {'tema':<14}{'veri':>5}{'presi':>6}  {'precisione':>10}  {'richiamo':>8}")
    for t, c in per_tema.items():
        print(f"  {t:<14}{c['vp'] + c['fn']:>5}{c['vp'] + c['fp']:>6}  "
              f"{_pct(c['precisione']):>10}  {_pct(c['richiamo']):>8}")
    print(f"  {'totale':<14}{tot['vp'] + tot['fn']:>5}{tot['vp'] + tot['fp']:>6}  "
          f"{_pct(tot['precisione']):>10}  {_pct(tot['richiamo']):>8}")
    esito = "passa" if tot["richiamo"] is not None and tot["richiamo"] >= SOGLIA_RICHIAMO else "non passa"
    print(f"  richiamo complessivo {_pct(tot['richiamo']).strip()}: {esito} la soglia del 90%")
