"""Riga di comando della pipeline: `python -m elezio_pipeline <comando>` da pipeline/."""

import argparse
import datetime
import json
import sys
from pathlib import Path

import yaml

from . import bozze, classifica, config, estrai, fonti, ocr, schede, valuta
from .llm import TettoSuperato


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


def _percorso_passaggi(cfg, fonte):
    return fonti.cartella_fonti(cfg) / "lavoro" / fonte / "passaggi.jsonl"


def _leggi_passaggi(percorso):
    with open(percorso, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def _registra(cfg, nome, log):
    """Uso e costo di ogni chiamata in lavoro/log/<run>.jsonl (docs/pipeline.md)."""
    if not log:
        return
    cartella = fonti.cartella_fonti(cfg) / "lavoro" / "log"
    cartella.mkdir(parents=True, exist_ok=True)
    momento = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(cartella / f"{momento}-{nome}.jsonl", "a", encoding="utf-8") as f:
        for voce in log:
            f.write(json.dumps(voce) + "\n")


def _classifica(args, cfg):
    percorso = _percorso_passaggi(cfg, args.fonte)
    passaggi = _leggi_passaggi(percorso)
    c = classifica.ClassificatoreLLM(cfg)
    try:
        previsti = c.classifica(passaggi)
    except TettoSuperato as e:
        print(f"{args.fonte}: {e}, passaggi non modificati")
        return 1
    finally:
        _registra(cfg, f"classifica-{args.fonte}", c.log)
    soglia = float(cfg["ELEZIO_SOGLIA_CLASSIFICAZIONE"])
    with open(percorso, "w", encoding="utf-8") as f:
        for p in passaggi:
            punteggi = previsti.get(p["id"], {})
            f.write(json.dumps(dict(p, punteggi=punteggi,
                                    temi=[t for t, s in punteggi.items() if s >= soglia]),
                               ensure_ascii=False) + "\n")
    print(f"{len(passaggi)} passaggi classificati con {c.modello}, costo {c.costo:.4f} dollari")
    return 0


def _punteggio(s):
    return f"{s:.2f}".replace(".", ",")


def _riga_passaggio(p, punteggio=None):
    voto = f"  {_punteggio(punteggio)}" if punteggio is not None else ""
    sezione = f"  [{p['sezione']}]" if p.get("sezione") else ""
    return f"  {p['id']}  pagina {p['pagina']}{voto}{sezione}\n    {p['testo']}"


def _passaggi(args, cfg):
    """Per il revisore: cosa il classificatore ha dato al tema e cosa potrebbe aver perso."""
    passaggi = _leggi_passaggi(_percorso_passaggi(cfg, args.fonte))
    if any("temi" not in p for p in passaggi):
        print(f"{args.fonte}: passaggi non classificati, lancia prima pipeline classifica")
        return 1
    t = args.tema
    assegnati = [p for p in passaggi if t in p["temi"]]
    scartati = [p for p in passaggi if t not in p["temi"] and t in p["punteggi"]]
    senza = [p for p in passaggi if not p["temi"]]
    print(f"Assegnati a {t} ({len(assegnati)})")
    for p in assegnati:
        print(_riga_passaggio(p, p["punteggi"][t]))
    print(f"\nScartati con punteggio basso ({len(scartati)})")
    for p in scartati:
        print(_riga_passaggio(p, p["punteggi"][t]))
    print(f"\nSenza temi ({len(senza)})")
    for p in senza:
        print(_riga_passaggio(p))
    return 0


def _bozze(args, cfg):
    passaggi = _leggi_passaggi(_percorso_passaggi(cfg, args.fonte))
    log = []
    try:
        costo = bozze.genera(cfg, args.fonte, args.tema, passaggi, log)
    except (bozze.BozzaImpossibile, TettoSuperato) as e:
        print(f"{args.fonte}/{args.tema}: {e}")
        return 1
    finally:
        _registra(cfg, f"bozze-{args.fonte}-{args.tema}", log)
    print(f"{args.fonte}/{args.tema}: {len(log)} chiamate, costo {costo:.4f} dollari")
    return 0


def _acquisisci(args, cfg):
    percorso = fonti.acquisisci(cfg, args.url, args.fonte, args.partiti.split(","),
                                args.elezione, args.tipo, args.copia_di)
    print(f"{percorso.name}: scaricato; YAML in contenuti/fonti/{args.copia_di or args.fonte}.yaml")


def _estrai(args, cfg):
    y = fonti.leggi(args.fonte)
    base = fonti.cartella_fonti(cfg)
    pdf = base / "pdf" / f"{args.fonte}.pdf"
    lavoro = base / "lavoro" / args.fonte
    if y.get("ocr"):
        cartella = lavoro / "ocr"
        o = ocr.ocr_pdf(pdf, cartella, cfg, y["ocr"])
        if getattr(o, "versione", None) and y.get("ocr_versione") != o.versione:
            print(f"versione dell'OCR: {o.versione}; registrala in ocr_versione del YAML")
        pagine = ocr.leggi_pagine(cartella)
        testo = estrai.testo_con_pagine_md(pagine)
        passaggi = estrai.segmenta_markdown(pagine, args.fonte)
        if o.log:
            with open(lavoro / "ocr-log.jsonl", "a", encoding="utf-8") as f:
                for voce in o.log:
                    f.write(json.dumps(voce) + "\n")
        print(f"OCR {len(o.log)} pagine nuove, costo {o.costo:.4f} dollari")
    else:
        righe = estrai.leggi_righe(pdf)
        testo = estrai.testo_con_pagine(righe)
        passaggi = estrai.segmenta(righe, args.fonte)
    uscita = base / y["testo_estratto"]
    uscita.parent.mkdir(parents=True, exist_ok=True)
    uscita.write_text(testo, encoding="utf-8")
    lavoro.mkdir(parents=True, exist_ok=True)
    with open(lavoro / "passaggi.jsonl", "w", encoding="utf-8") as f:
        for p in passaggi:
            f.write(json.dumps({"id": p.id, "pagina": p.pagina, "pagina_fine": p.pagina_fine,
                                "sezione": p.sezione, "testo": p.testo}, ensure_ascii=False) + "\n")
    print(f"{y['testo_estratto']}: {len(testo.split())} parole, {len(passaggi)} passaggi")


def _verifica(args, cfg):
    esito, fonti_dir = fonti.verifica(cfg)
    for nome, errori in esito.items():
        for e in errori:
            print(f"{nome}: {e}")
    controllo = f"con elezio-fonti in {fonti_dir}" if fonti_dir else "senza elezio-fonti (solo schema)"
    print(f"fonti: {'errori' if esito else 'ok'}, {controllo}")
    temi = {t["id"] for t in classifica.carica_temi()}
    tutte = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(fonti.contenuti_fonti().glob("*.yaml"))}
    errori_schede = schede.verifica(temi, tutte, fonti_dir)
    for nome, errori in errori_schede.items():
        for e in errori:
            print(f"{nome}: {e}")
    print(f"schede: {'errori' if errori_schede else 'ok'}, {controllo}")
    return 1 if esito or errori_schede else 0


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")  # i testi dei programmi non stanno nella codepage di Windows
    p = argparse.ArgumentParser(prog="pipeline")
    sub = p.add_subparsers(dest="comando", required=True)
    a = sub.add_parser("acquisisci", help="passo 1: PDF, hash, copia Wayback, YAML della fonte in bozza")
    a.add_argument("--url", required=True)
    a.add_argument("--fonte", required=True, help="slug della fonte, es. 2022-pd-programma")
    a.add_argument("--partiti", required=True, help="slug separati da virgola")
    a.add_argument("--elezione", type=int, required=True)
    a.add_argument("--tipo", default="programma", choices=sorted(fonti.TIPI))
    a.add_argument("--copia-di", help="fonte di cui questo PDF è un'altra copia depositata")
    e = sub.add_parser("estrai", help="passi 2-4: testo estratto con pagine e passaggi")
    e.add_argument("--fonte", required=True)
    sub.add_parser("verifica", help="passo 9: YAML delle fonti, schede e citazioni")
    v = sub.add_parser("valuta-classificatore", help="precisione e richiamo sul campione d'oro")
    v.add_argument("--modelli", help="id separati da virgola (default: ELEZIO_MODELLO_CLASSIFICAZIONE)")
    v.add_argument("--campione", type=Path, default=valuta.CAMPIONE)
    v.add_argument("--uscita", type=Path, help="cartella dove salvare previsioni e usage")
    c = sub.add_parser("classifica", help="passo 5: temi e punteggi nei passaggi della fonte")
    c.add_argument("--fonte", required=True)
    w = sub.add_parser("passaggi", help="per il revisore: passaggi assegnati a un tema e possibili perdite")
    w.add_argument("--fonte", required=True)
    w.add_argument("--tema", required=True)
    b = sub.add_parser("bozze", help="passi 6-7: scheda in bozza con le citazioni verificate")
    b.add_argument("--fonte", required=True)
    b.add_argument("--tema", required=True)
    args = p.parse_args(argv)
    cfg = config.carica()
    comandi = {"valuta-classificatore": _valuta_classificatore, "classifica": _classifica,
               "acquisisci": _acquisisci, "estrai": _estrai, "verifica": _verifica,
               "passaggi": _passaggi, "bozze": _bozze}
    return comandi[args.comando](args, cfg)


if __name__ == "__main__":
    sys.exit(main())
