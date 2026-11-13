"""`pipeline bozze` su più fonti e più temi in un lancio, e la classificazione accanto alla bozza (#67)."""

import datetime
import json

from conftest import FONTE

from elezio_pipeline.__main__ import main

ALTRA = "2022-altra-programma"
SANITA = "Uno psicologo di base in ogni distretto."
FISCO = "Riforma dell'Irpef con tre aliquote."


def _dichiarata(pagina, testo, titolo="Un titolo"):
    return {"posizione": "dichiarata", "titolo": titolo, "sintesi": "Una sintesi.",
            "citazioni": [{"pagina": pagina, "testo": testo}]}


SU_SANITA = _dichiarata(2, SANITA, "Più psicologi")
SU_FISCO = _dichiarata(3, FISCO, "Tre aliquote")


def _lavoro(progetto, fonte):
    return progetto.fonti_dir / "lavoro" / fonte


def _classifica(progetto, fonte, registro=True):
    """Passaggi SALUTE a sanita, FISCO a fisco, con il registro di `pipeline classifica`."""
    percorso = _lavoro(progetto, fonte) / "passaggi.jsonl"
    passaggi = [json.loads(r) for r in percorso.read_text(encoding="utf-8").splitlines()]
    for p in passaggi:
        tema = {"SALUTE": "sanita", "FISCO": "fisco"}.get(p["sezione"])
        p["punteggi"] = {"sanita": 0, "fisco": 0} | ({tema: 0.9} if tema else {})
        p["temi"] = [tema] if tema else []
    percorso.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in passaggi), encoding="utf-8")
    if registro:
        (_lavoro(progetto, fonte) / "classificazione.json").write_text(json.dumps({
            "id": "20261113-120000", "modello": "finto/classifica", "prompt": "classificazione-v3.md",
            "soglia": 0.2, "data": "2026-11-13", "passaggi": len(passaggi), "incompleti": [],
            "copia": "classificazioni/20261113-120000.jsonl"}), encoding="utf-8")


def _due_fonti(progetto):
    progetto.aggiungi_fonte(ALTRA, ["altra"])
    _classifica(progetto, FONTE)
    _classifica(progetto, ALTRA)


def _bozze(fonte, tema, *opzioni):
    return main(["bozze", "--fonte", fonte, "--tema", tema, *opzioni])


def _riepilogo(uscita):
    return uscita[uscita.index("Riepilogo"):]


def test_piu_fonti_e_piu_temi_in_un_lancio(progetto, modello, capsys):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, SU_FISCO, SU_SANITA, SU_FISCO]
    assert not _bozze(f"{FONTE},{ALTRA}", "sanita,fisco")
    assert len(modello.richieste) == 4
    assert progetto.leggi_scheda(partito="prova", tema="fisco")[0]["titolo"] == "Tre aliquote"
    assert progetto.leggi_scheda(partito="altra", tema="sanita")[0]["titolo"] == "Più psicologi"
    riepilogo = _riepilogo(capsys.readouterr().out)
    assert "4 coppie, costo 0.0040 dollari" in riepilogo
    assert f"scritte: 4 ({FONTE}/sanita, {FONTE}/fisco, {ALTRA}/sanita, {ALTRA}/fisco)" in riepilogo
    assert "fallite: 0" in riepilogo


def test_tutte_le_fonti_e_tutti_i_temi(progetto, modello):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, SU_FISCO, SU_SANITA, SU_FISCO]
    assert not _bozze("tutte", "tutti")
    for partito in ("prova", "altra"):
        for tema in ("sanita", "fisco"):
            assert progetto.scheda(partito, tema).exists()


def test_fonte_o_tema_inesistente_si_rifiuta_prima_di_chiamare(progetto, modello, capsys):
    _due_fonti(progetto)
    assert _bozze(f"{FONTE},2022-nessuna", "sanita") == 1
    assert _bozze(FONTE, "sanita,nessuno") == 1
    assert modello.richieste == []
    uscita = capsys.readouterr().out
    assert "2022-nessuna" in uscita and "nessuno" in uscita


def test_il_tetto_vale_per_tutto_il_lancio(progetto, modello, monkeypatch, capsys):
    monkeypatch.setenv("ELEZIO_TETTO_DOLLARI", "0.0015")  # ogni chiamata costa 0,001
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, SU_FISCO]
    assert _bozze("tutte", "tutti") == 1
    assert len(modello.richieste) == 2  # per coppia il tetto non scatterebbe mai
    assert progetto.scheda("altra", "fisco").exists()  # tutte: in ordine alfabetico, ALTRA viene prima
    assert not progetto.scheda("prova", "sanita").exists()
    riepilogo = _riepilogo(capsys.readouterr().out)
    assert f"fallite: 2 ({FONTE}/sanita, {FONTE}/fisco)" in riepilogo


def test_una_coppia_fallita_non_ferma_le_altre(progetto, modello, capsys):
    _due_fonti(progetto)
    modello.risposte += ["non è json", "ancora no", SU_FISCO]
    assert _bozze(FONTE, "sanita,fisco") == 1
    assert not progetto.scheda("prova", "sanita").exists()
    assert progetto.scheda("prova", "fisco").exists()
    uscita = capsys.readouterr().out
    assert f"{FONTE}/sanita: risposta del modello non valida" in uscita
    assert f"fallite: 1 ({FONTE}/sanita)" in _riepilogo(uscita)


def test_fonte_senza_passaggi_fallisce_e_le_altre_proseguono(progetto, modello, capsys):
    _due_fonti(progetto)
    (_lavoro(progetto, ALTRA) / "passaggi.jsonl").unlink()
    modello.risposte += [SU_SANITA]
    assert _bozze("tutte", "sanita") == 1
    assert progetto.scheda("prova", "sanita").exists()
    uscita = capsys.readouterr().out
    assert "lancia prima pipeline estrai" in uscita
    assert f"fallite: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_il_riepilogo_conta_assenti_e_revisionate(progetto, modello, capsys):
    _due_fonti(progetto)
    progetto.scrivi_scheda({
        "partito": "altra", "tema": "sanita", "elezione": 2022, "posizione": "dichiarata", "titolo": "A mano",
        "citazioni": [{"fonte": ALTRA, "pagina": 2, "testo": SANITA}], "stato": "verificata",
        "verificata_il": datetime.date(2026, 11, 2), "revisore": "revisore", "aggiornata_il": datetime.date(2026, 11, 2),
    })
    modello.risposte += [{"posizione": "assente", "titolo": "", "sintesi": "", "citazioni": []}]
    assert not _bozze("tutte", "sanita")
    riepilogo = _riepilogo(capsys.readouterr().out)
    assert f"assenti: 1 ({FONTE}/sanita)" in riepilogo
    assert f"saltate perché già revisionate: 1 ({ALTRA}/sanita)" in riepilogo


def test_rilanciare_non_rigenera_le_coppie_gia_scritte(progetto, modello, capsys):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, SU_FISCO]
    assert not _bozze(FONTE, "tutti")
    capsys.readouterr()
    assert not _bozze(FONTE, "tutti")
    assert len(modello.richieste) == 2
    riepilogo = _riepilogo(capsys.readouterr().out)
    assert f"saltate perché già scritte (--rigenera per rifarle): 2 ({FONTE}/sanita, {FONTE}/fisco)" in riepilogo
    assert "costo 0.0000 dollari" in riepilogo


def test_ripresa_dopo_un_interruzione_fa_solo_le_coppie_mancanti(progetto, modello):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, "non è json", "ancora no"]
    assert _bozze(FONTE, "tutti") == 1
    modello.risposte += [SU_FISCO]
    assert not _bozze(FONTE, "tutti")
    assert len(modello.richieste) == 4
    assert "Irpef" in json.dumps(modello.richieste[-1]["messages"], ensure_ascii=False)


def test_rigenera_rifa_le_bozze_ma_non_le_schede_revisionate(progetto, modello):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA]
    assert not _bozze(FONTE, "sanita")
    fronte, corpo = progetto.leggi_scheda(partito="prova", tema="sanita")
    fronte |= {"stato": "contestata", "verificata_il": datetime.date(2026, 11, 2), "revisore": "revisore"}
    progetto.scrivi_scheda(fronte, corpo)
    modello.risposte += [SU_SANITA]
    assert not _bozze("tutte", "sanita", "--rigenera")
    assert len(modello.richieste) == 2  # solo altra/sanita
    assert progetto.leggi_scheda(partito="prova", tema="sanita")[0]["stato"] == "contestata"


def test_la_bozza_salva_la_classificazione_da_cui_nasce(progetto, modello):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA]
    assert not _bozze(FONTE, "sanita")
    salvata = json.loads((_lavoro(progetto, FONTE) / "bozze" / "sanita.json").read_text(encoding="utf-8"))
    assert salvata["classificazione"]["modello"] == "finto/classifica"
    assert salvata["classificazione"]["prompt"] == "classificazione-v3.md"
    assert salvata["classificazione"]["soglia"] == 0.2
    assert salvata["classificazione"]["copia"] == "classificazioni/20261113-120000.jsonl"
    assert salvata["bozza_da"] == {"modello": "finto/sintesi", "prompt": "bozza-v1.md"}
    assert salvata["risposta"] == SU_SANITA


def test_anche_l_assenza_senza_modello_salva_la_classificazione(progetto, modello):
    _due_fonti(progetto)
    percorso = _lavoro(progetto, FONTE) / "passaggi.jsonl"
    passaggi = [json.loads(r) for r in percorso.read_text(encoding="utf-8").splitlines()]
    for p in passaggi:
        p["punteggi"], p["temi"] = {"sanita": 0, "fisco": 0}, []
    percorso.write_text("".join(json.dumps(p) + "\n" for p in passaggi), encoding="utf-8")
    assert not _bozze(FONTE, "sanita")
    assert modello.richieste == []
    salvata = json.loads((_lavoro(progetto, FONTE) / "bozze" / "sanita.json").read_text(encoding="utf-8"))
    assert salvata["classificazione"]["soglia"] == 0.2
    assert salvata["bozza_da"] is None and salvata["risposta"] is None


def test_senza_registro_della_classificazione_la_coppia_fallisce(progetto, modello, capsys):
    progetto.aggiungi_fonte(ALTRA, ["altra"])
    _classifica(progetto, FONTE)
    _classifica(progetto, ALTRA, registro=False)
    modello.risposte += [SU_SANITA]
    assert _bozze("tutte", "sanita") == 1
    assert not progetto.scheda("altra", "sanita").exists()
    uscita = capsys.readouterr().out
    assert "rilancia pipeline classifica" in uscita
    assert f"fallite: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_un_log_per_coppia(progetto, modello):
    _due_fonti(progetto)
    modello.risposte += [SU_SANITA, SU_FISCO]
    assert not _bozze(FONTE, "tutti")
    log = sorted(p.name for p in (progetto.fonti_dir / "lavoro" / "log").glob("*.jsonl"))
    assert len(log) == 2
    assert log[0].endswith(f"bozze-{FONTE}-fisco.jsonl") or log[1].endswith(f"bozze-{FONTE}-fisco.jsonl")


# File rotti: falliscono solo le loro coppie

def _scrivi_scheda_grezza(progetto, partito, tema, testo):
    p = progetto.scheda(partito, tema)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


def test_scheda_con_yaml_rotto_fa_fallire_solo_la_sua_coppia(progetto, modello, capsys):
    _due_fonti(progetto)
    _scrivi_scheda_grezza(progetto, "altra", "sanita", "---\npartito: [altra\n---\n\nTesto.\n")
    modello.risposte += [SU_SANITA, SU_FISCO, SU_SANITA]
    assert _bozze("tutte", "tutti") == 1
    assert progetto.scheda("prova", "fisco").exists()
    assert progetto.scheda("altra", "sanita").read_text(encoding="utf-8").startswith("---\npartito: [altra")
    uscita = capsys.readouterr().out
    assert "scheda altra/sanita illeggibile" in uscita
    assert f"fallite: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_scheda_con_frontmatter_vuoto_fa_fallire_solo_la_sua_coppia(progetto, modello, capsys):
    _due_fonti(progetto)
    _scrivi_scheda_grezza(progetto, "altra", "sanita", "---\n\n---\n\nTesto.\n")
    modello.risposte += [SU_SANITA]
    assert _bozze("tutte", "sanita") == 1
    assert progetto.scheda("prova", "sanita").exists()
    uscita = capsys.readouterr().out
    assert "frontmatter vuoto" in uscita
    assert f"fallite: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_fonte_senza_un_campo_fa_fallire_solo_le_sue_coppie(progetto, modello, capsys):
    _due_fonti(progetto)
    percorso = progetto.contenuti / "fonti" / f"{ALTRA}.yaml"
    percorso.write_text("".join(r for r in percorso.read_text(encoding="utf-8").splitlines(keepends=True)
                                if not r.startswith("elezione:")), encoding="utf-8")
    modello.risposte += [SU_SANITA]
    assert _bozze("tutte", "sanita") == 1
    assert progetto.scheda("prova", "sanita").exists()
    uscita = capsys.readouterr().out
    assert "YAML della fonte senza elezione" in uscita
    assert f"fallite: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_fonte_con_yaml_rotto_fa_fallire_solo_le_sue_coppie(progetto, modello, capsys):
    _due_fonti(progetto)
    (progetto.contenuti / "fonti" / f"{ALTRA}.yaml").write_text("id: [rotto\n", encoding="utf-8")
    modello.risposte += [SU_SANITA]
    assert _bozze("tutte", "sanita") == 1
    assert progetto.scheda("prova", "sanita").exists()
    assert "YAML della fonte illeggibile" in capsys.readouterr().out


def test_verifica_segnala_il_frontmatter_vuoto_senza_fermarsi(progetto, modello, capsys):
    _scrivi_scheda_grezza(progetto, "prova", "sanita", "---\n\n---\n\nTesto.\n")
    assert main(["verifica"]) == 1
    assert "frontmatter vuoto" in capsys.readouterr().out


# Fonte condivisa con solo alcune schede scritte

def _condivisa(progetto):
    progetto.aggiungi_fonte(ALTRA, ["altra", "terza"])
    _classifica(progetto, ALTRA)
    progetto.scrivi_scheda({
        "partito": "altra", "tema": "sanita", "elezione": 2022, "posizione": "dichiarata",
        "titolo": "Corretta a mano", "citazioni": [{"fonte": ALTRA, "pagina": 2, "testo": SANITA}],
        "stato": "bozza", "aggiornata_il": datetime.date(2026, 11, 2)})


def test_fonte_condivisa_scrive_solo_le_schede_mancanti(progetto, modello, capsys):
    _condivisa(progetto)
    modello.risposte += [SU_SANITA]
    assert not _bozze(ALTRA, "sanita")
    assert progetto.leggi_scheda(partito="altra")[0]["titolo"] == "Corretta a mano"
    assert progetto.leggi_scheda(partito="terza")[0]["titolo"] == "Più psicologi"
    uscita = capsys.readouterr().out
    assert "altra/sanita: bozza già scritta, non la tocco" in uscita
    assert f"scritte: 1 ({ALTRA}/sanita)" in _riepilogo(uscita)


def test_fonte_condivisa_con_rigenera_riscrive_anche_le_bozze(progetto, modello):
    _condivisa(progetto)
    modello.risposte += [SU_SANITA]
    assert not _bozze(ALTRA, "sanita", "--rigenera")
    assert progetto.leggi_scheda(partito="altra")[0]["titolo"] == "Più psicologi"
    assert progetto.leggi_scheda(partito="terza")[0]["titolo"] == "Più psicologi"


def test_fonte_condivisa_con_una_verificata_e_una_bozza_non_genera_nulla(progetto, modello, capsys):
    _condivisa(progetto)
    progetto.scrivi_scheda({
        "partito": "terza", "tema": "sanita", "elezione": 2022, "posizione": "dichiarata", "titolo": "A mano",
        "citazioni": [{"fonte": ALTRA, "pagina": 2, "testo": SANITA}], "stato": "verificata",
        "verificata_il": datetime.date(2026, 11, 2), "revisore": "revisore", "aggiornata_il": datetime.date(2026, 11, 2),
    })
    assert not _bozze(ALTRA, "sanita")
    assert modello.richieste == []
    assert "saltate perché già scritte" in capsys.readouterr().out


# `pipeline classifica`: registro e copia di ogni classificazione

def _risposta_classifica(fonte):
    return {"passaggi": [{"id": f"{fonte}-{i:04d}", "punteggi": {"sanita": 0.9 if i in (2, 3) else 0, "fisco": 0}}
                         for i in range(1, 5)]}


def test_classifica_scrive_registro_e_copia(progetto, modello):
    modello.risposte.append(_risposta_classifica(FONTE))
    assert not main(["classifica", "--fonte", FONTE])
    lavoro = _lavoro(progetto, FONTE)
    registro = json.loads((lavoro / "classificazione.json").read_text(encoding="utf-8"))
    assert registro["modello"] == "finto/classifica"
    assert registro["prompt"] == "classificazione-v3.md"
    assert registro["soglia"] == 0.2
    assert registro["incompleti"] == []
    copia = lavoro / registro["copia"]
    assert copia.read_text(encoding="utf-8") == (lavoro / "passaggi.jsonl").read_text(encoding="utf-8")


def test_riclassificare_non_cancella_la_classificazione_di_una_bozza(progetto, modello):
    modello.risposte.append(_risposta_classifica(FONTE))
    assert not main(["classifica", "--fonte", FONTE])
    modello.risposte.append(SU_SANITA)
    assert not _bozze(FONTE, "sanita")
    lavoro = _lavoro(progetto, FONTE)
    nata_da = json.loads((lavoro / "bozze" / "sanita.json").read_text(encoding="utf-8"))["classificazione"]
    prima = (lavoro / nata_da["copia"]).read_text(encoding="utf-8")
    modello.risposte.append({"passaggi": [{"id": f"{FONTE}-{i:04d}", "punteggi": {"sanita": 0, "fisco": 0.9}}
                                          for i in range(1, 5)]})
    assert not main(["classifica", "--fonte", FONTE])
    assert (lavoro / nata_da["copia"]).read_text(encoding="utf-8") == prima
    assert '"temi": ["sanita"]' in prima
    assert '"temi": ["sanita"]' not in (lavoro / "passaggi.jsonl").read_text(encoding="utf-8")
    assert json.loads((lavoro / "classificazione.json").read_text(encoding="utf-8"))["id"] != nata_da["id"]


def test_classificazione_senza_registro_si_conserva_prima_di_riscriverla(progetto, modello):
    _classifica(progetto, FONTE, registro=False)
    vecchia = (_lavoro(progetto, FONTE) / "passaggi.jsonl").read_text(encoding="utf-8")
    modello.risposte.append(_risposta_classifica(FONTE))
    assert not main(["classifica", "--fonte", FONTE])
    conservate = list((_lavoro(progetto, FONTE) / "classificazioni").glob("*-senza-registro.jsonl"))
    assert len(conservate) == 1
    assert conservate[0].read_text(encoding="utf-8") == vecchia
