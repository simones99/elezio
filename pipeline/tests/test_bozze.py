"""`pipeline bozze`: dal JSON del modello al file scheda (docs/pipeline.md, ADR 0005)."""

import datetime
import json

from conftest import FONTE

from elezio_pipeline.__main__ import main

CITAZIONE_VERA = "Uno psicologo di base in ogni distretto."
CITAZIONE_VERA_2 = "AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO"
INVENTATA = "Uno psichiatra in ogni condominio."


def _classificati(progetto):
    passaggi = progetto.passaggi()
    for p in passaggi:
        tema = "sanita" if p["sezione"] == "SALUTE" else "fisco" if p["sezione"] else None
        p["punteggi"] = {tema: 0.9} if tema else {}
        p["temi"] = [tema] if tema else []
    progetto.scrivi_passaggi(passaggi)


def _dichiarata(*citazioni, sintesi="Il partito propone più psicologi nei distretti."):
    return {"posizione": "dichiarata", "titolo": "Più psicologi nei distretti", "sintesi": sintesi,
            "citazioni": [{"pagina": p, "testo": t} for p, t in citazioni]}


ASSENTE = {"posizione": "assente", "titolo": "", "sintesi": "", "citazioni": []}


def _bozze():
    return main(["bozze", "--fonte", FONTE, "--tema", "sanita"])


def test_bozza_scrive_la_scheda_con_citazioni_verificate(progetto, modello):
    _classificati(progetto)
    modello.risposte.append(_dichiarata((2, CITAZIONE_VERA)))
    assert not _bozze()
    fronte, corpo = progetto.leggi_scheda()
    assert fronte["partito"] == "prova"
    assert fronte["tema"] == "sanita"
    assert fronte["elezione"] == 2022
    assert fronte["posizione"] == "dichiarata"
    assert fronte["titolo"] == "Più psicologi nei distretti"
    assert fronte["stato"] == "bozza"
    assert fronte["citazioni"] == [{"fonte": FONTE, "pagina": 2, "testo": CITAZIONE_VERA}]
    assert fronte["aggiornata_il"] == datetime.date.today()
    assert fronte["bozza_da"] == {"modello": "finto/sintesi", "prompt": "bozza-v1.md"}
    assert "note" not in fronte
    assert corpo == "Il partito propone più psicologi nei distretti."


def test_al_modello_arrivano_solo_i_passaggi_del_tema_con_la_pagina(progetto, modello):
    _classificati(progetto)
    modello.risposte.append(_dichiarata((2, CITAZIONE_VERA)))
    assert not _bozze()
    richiesta = modello.richieste[0]
    assert richiesta["model"] == "finto/sintesi"
    testo = json.dumps(richiesta["messages"], ensure_ascii=False)
    assert CITAZIONE_VERA in testo
    assert "Riforma dell'Irpef con tre aliquote" not in testo
    assert "pagina 2" in testo
    assert "Salute mentale" in testo


def test_salva_il_json_della_bozza_e_il_log_nel_repo_privato(progetto, modello):
    _classificati(progetto)
    risposta = _dichiarata((2, CITAZIONE_VERA))
    modello.risposte.append(risposta)
    assert not _bozze()
    salvato = progetto.fonti_dir / "lavoro" / FONTE / "bozze" / "sanita.json"
    assert json.loads(salvato.read_text(encoding="utf-8")) == risposta
    log = list((progetto.fonti_dir / "lavoro" / "log").glob("*bozze*.jsonl"))
    assert len(log) == 1
    assert json.loads(log[0].read_text(encoding="utf-8").splitlines()[0])["usage"]["cost"] == 0.001


def test_pagina_adiacente_viene_corretta_nella_scheda(progetto, modello):
    _classificati(progetto)
    modello.risposte.append(_dichiarata((3, CITAZIONE_VERA)))
    assert not _bozze()
    fronte, _ = progetto.leggi_scheda()
    assert fronte["citazioni"][0]["pagina"] == 2


def test_citazione_falsa_si_scarta_e_il_modello_riprova_una_volta(progetto, modello):
    _classificati(progetto)
    modello.risposte += [_dichiarata((2, CITAZIONE_VERA), (2, INVENTATA)),
                         _dichiarata((2, CITAZIONE_VERA), (2, CITAZIONE_VERA_2))]
    assert not _bozze()
    assert len(modello.richieste) == 2
    secondo = json.dumps(modello.richieste[1]["messages"], ensure_ascii=False)
    assert INVENTATA in secondo
    fronte, _ = progetto.leggi_scheda()
    assert [c["testo"] for c in fronte["citazioni"]] == [CITAZIONE_VERA, CITAZIONE_VERA_2]
    assert "note" not in fronte


def test_se_fallisce_ancora_resta_bozza_senza_la_citazione_e_con_la_nota(progetto, modello):
    _classificati(progetto)
    modello.risposte += [_dichiarata((2, CITAZIONE_VERA), (2, INVENTATA))] * 2
    assert not _bozze()
    assert len(modello.richieste) == 2
    fronte, _ = progetto.leggi_scheda()
    assert fronte["stato"] == "bozza"
    assert [c["testo"] for c in fronte["citazioni"]] == [CITAZIONE_VERA]
    assert INVENTATA in fronte["note"]


def test_se_non_resta_nessuna_citazione_la_posizione_non_diventa_assente(progetto, modello, capsys):
    _classificati(progetto)
    modello.risposte += [_dichiarata((2, INVENTATA))] * 2
    assert not _bozze()
    fronte, _ = progetto.leggi_scheda()
    assert fronte["posizione"] == "dichiarata"
    assert fronte["citazioni"] == []
    assert INVENTATA in fronte["note"]
    capsys.readouterr()
    assert main(["verifica"]) == 1
    assert "senza citazioni" in capsys.readouterr().out


def test_il_modello_dice_assente(progetto, modello):
    _classificati(progetto)
    modello.risposte.append(ASSENTE)
    assert not _bozze()
    fronte, corpo = progetto.leggi_scheda()
    assert fronte["posizione"] == "assente"
    assert fronte["citazioni"] == []
    assert "titolo" not in fronte
    assert "non tratta" in corpo


def test_nessun_passaggio_del_tema_assente_senza_chiamare_il_modello(progetto, modello):
    passaggi = progetto.passaggi()
    for p in passaggi:
        p["punteggi"], p["temi"] = {}, []
    progetto.scrivi_passaggi(passaggi)
    assert not _bozze()
    assert modello.richieste == []
    fronte, _ = progetto.leggi_scheda()
    assert fronte["posizione"] == "assente"
    assert "classificatore" in fronte["note"]
    assert "bozza_da" not in fronte


def test_assente_dopo_una_citazione_falsa_lo_segnala_al_revisore(progetto, modello):
    _classificati(progetto)
    modello.risposte += [_dichiarata((2, INVENTATA)), ASSENTE]
    assert not _bozze()
    fronte, _ = progetto.leggi_scheda()
    assert fronte["posizione"] == "assente"
    assert "dichiarata" in fronte["note"]


def test_dichiarata_senza_titolo_o_sintesi_si_ritenta(progetto, modello):
    _classificati(progetto)
    modello.risposte += [dict(_dichiarata((2, CITAZIONE_VERA)), titolo=""), _dichiarata((2, CITAZIONE_VERA))]
    assert not _bozze()
    assert len(modello.richieste) == 2
    assert progetto.leggi_scheda()[0]["titolo"] == "Più psicologi nei distretti"


def test_risposta_non_json_si_ritenta_e_poi_nessun_file(progetto, modello, capsys):
    _classificati(progetto)
    modello.risposte += ["non è json", "ancora no"]
    assert _bozze() == 1
    assert not progetto.scheda().exists()
    assert "non valida" in capsys.readouterr().out


def test_fonte_condivisa_scrive_la_stessa_bozza_per_ogni_partito(progetto, modello):
    percorso = progetto.contenuti / "fonti" / f"{FONTE}.yaml"
    percorso.write_text(percorso.read_text(encoding="utf-8").replace("- prova", "- prova\n- altro"), encoding="utf-8")
    _classificati(progetto)
    modello.risposte.append(_dichiarata((2, CITAZIONE_VERA)))
    assert not _bozze()
    assert len(modello.richieste) == 1
    a, b = progetto.leggi_scheda(partito="prova"), progetto.leggi_scheda(partito="altro")
    assert a[0]["partito"] == "prova" and b[0]["partito"] == "altro"
    assert a[0]["citazioni"] == b[0]["citazioni"] and a[1] == b[1]


def test_una_scheda_gia_verificata_non_si_sovrascrive(progetto, modello, capsys):
    _classificati(progetto)
    progetto.scrivi_scheda({
        "partito": "prova", "tema": "sanita", "elezione": 2022, "posizione": "dichiarata", "titolo": "A mano",
        "citazioni": [{"fonte": FONTE, "pagina": 2, "testo": CITAZIONE_VERA}], "stato": "verificata",
        "verificata_il": datetime.date(2026, 11, 2), "revisore": "revisore", "aggiornata_il": datetime.date(2026, 11, 2),
    })
    assert not _bozze()
    assert modello.richieste == []
    assert progetto.leggi_scheda()[0]["titolo"] == "A mano"
    assert "verificata" in capsys.readouterr().out


def test_il_tetto_ferma_il_nuovo_tentativo_e_non_scrive_niente(progetto, modello, monkeypatch):
    monkeypatch.setenv("ELEZIO_TETTO_DOLLARI", "0.0000001")
    _classificati(progetto)
    modello.risposte.append(_dichiarata((2, INVENTATA)))
    assert _bozze() == 1
    assert len(modello.richieste) == 1
    assert not progetto.scheda().exists()


def test_senza_classificazione_lo_dice_senza_chiamare_il_modello(progetto, modello, capsys):
    assert _bozze() == 1
    assert modello.richieste == []
    assert "classifica" in capsys.readouterr().out


def test_tema_sconosciuto_si_rifiuta(progetto, modello, capsys):
    _classificati(progetto)
    assert main(["bozze", "--fonte", FONTE, "--tema", "inesistente"]) == 1
    assert modello.richieste == []
    assert "inesistente" in capsys.readouterr().out
