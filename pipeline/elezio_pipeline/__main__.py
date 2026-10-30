"""Riga di comando della pipeline: `python -m elezio_pipeline <comando>` da pipeline/."""

import argparse
import json
import sys
from pathlib import Path

from . import classifica, config, valuta


def _valuta_classificatore(args, cfg):
    campione = valuta.carica_campione(args.campione)
    temi = classifica.carica_temi()
    soglia = float(cfg["ELEZIO_SOGLIA_CLASSIFICAZIONE"])
    modelli = args.modelli.split(",") if args.modelli else [cfg["ELEZIO_MODELLO_CLASSIFICAZIONE"]]
    print(f"campione {args.campione.name}: {len(campione)} passaggi, soglia {soglia}, prompt {classifica.PROMPT}")
    for modello in modelli:
        c = classifica.ClassificatoreLLM(cfg, modello, temi)
        previsti = c.classifica(campione)
        per_tema, tot = valuta.misura(campione, previsti, [t["id"] for t in temi], soglia)
        valuta.stampa(f"llm {modello} (costo {c.costo:.4f} dollari)", per_tema, tot)
        if args.uscita:
            args.uscita.mkdir(parents=True, exist_ok=True)
            nome = modello.replace("/", "_")
            with open(args.uscita / f"{nome}.jsonl", "w", encoding="utf-8") as f:
                for p in campione:
                    f.write(json.dumps({"id": p["id"], "veri": p["temi"],
                                        "previsti": previsti.get(p["id"], {})}, ensure_ascii=False) + "\n")
            with open(args.uscita / f"{nome}.log.jsonl", "w", encoding="utf-8") as f:
                for voce in c.log:
                    f.write(json.dumps(voce) + "\n")


def _classifica(args, cfg):
    passaggi = [json.loads(r) for r in open(args.passaggi, encoding="utf-8") if r.strip()]
    c = classifica.ClassificatoreLLM(cfg)
    previsti = c.classifica(passaggi)
    soglia = float(cfg["ELEZIO_SOGLIA_CLASSIFICAZIONE"])
    with open(args.uscita, "w", encoding="utf-8") as f:
        for p in passaggi:
            punteggi = previsti.get(p["id"], {})
            f.write(json.dumps(dict(p, punteggi=punteggi,
                                    temi=[t for t, s in punteggi.items() if s >= soglia]),
                               ensure_ascii=False) + "\n")
    print(f"{len(passaggi)} passaggi classificati con {c.modello}, costo {c.costo:.4f} dollari")


def main(argv=None):
    p = argparse.ArgumentParser(prog="pipeline")
    sub = p.add_subparsers(dest="comando", required=True)
    v = sub.add_parser("valuta-classificatore", help="precisione e richiamo sul campione d'oro")
    v.add_argument("--modelli", help="id separati da virgola (default: ELEZIO_MODELLO_CLASSIFICAZIONE)")
    v.add_argument("--campione", type=Path, default=valuta.CAMPIONE)
    v.add_argument("--uscita", type=Path, help="cartella dove salvare previsioni e usage")
    c = sub.add_parser("classifica", help="passo 5 su un file di passaggi JSONL")
    c.add_argument("passaggi", type=Path)
    c.add_argument("uscita", type=Path)
    args = p.parse_args(argv)
    cfg = config.carica()
    {"valuta-classificatore": _valuta_classificatore, "classifica": _classifica}[args.comando](args, cfg)


if __name__ == "__main__":
    sys.exit(main())
