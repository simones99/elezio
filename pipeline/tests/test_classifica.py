"""`pipeline classifica --fonte` e la vista per il revisore (docs/pipeline.md)."""

import json

from conftest import FONTE

from elezio_pipeline.__main__ import main


def _risposta(*voci):
    return {"passaggi": [{"id": f"{FONTE}-{i:04d}", "temi": [{"tema": t, "punteggio": s} for t, s in temi]}
                         for i, temi in voci]}


def _classifica_prova(modello):
    modello.risposte.append(_risposta(
        (1, []), (2, [("sanita", 0.9)]), (3, [("sanita", 0.15), ("fisco", 0.3)]), (4, [("fisco", 0.95)])))
    assert not main(["classifica", "--fonte", FONTE])


def test_classifica_salva_punteggi_e_temi_sopra_la_soglia_nei_passaggi(progetto, modello):
    _classifica_prova(modello)
    passaggi = {p["id"][-4:]: p for p in progetto.passaggi()}
    assert passaggi["0002"]["temi"] == ["sanita"]
    assert passaggi["0002"]["punteggi"] == {"sanita": 0.9}
    assert passaggi["0003"]["temi"] == ["fisco"]
    assert passaggi["0003"]["punteggi"] == {"sanita": 0.15, "fisco": 0.3}
    assert passaggi["0001"]["temi"] == []
    assert passaggi["0002"]["testo"] == "AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO"


def test_classifica_registra_uso_e_costo_del_modello(progetto, modello):
    _classifica_prova(modello)
    log = list((progetto.fonti_dir / "lavoro" / "log").glob("*.jsonl"))
    assert len(log) == 1
    voce = json.loads(log[0].read_text(encoding="utf-8").splitlines()[0])
    assert voce["modello"] == "finto/classifica"
    assert voce["usage"]["cost"] == 0.001


def test_classifica_si_ferma_al_tetto_e_non_tocca_i_passaggi(progetto, modello, monkeypatch):
    monkeypatch.setenv("ELEZIO_TETTO_DOLLARI", "0.0000001")
    molti = [dict(progetto.passaggi()[0], id=f"{FONTE}-{i:04d}") for i in range(1, 26)]
    progetto.scrivi_passaggi(molti)
    modello.risposte.append(_risposta(*[(i, []) for i in range(1, 21)]))
    assert main(["classifica", "--fonte", FONTE]) == 1
    assert len(modello.richieste) == 1
    assert "temi" not in progetto.passaggi()[0]


def test_vista_del_revisore_divide_assegnati_scartati_e_senza_temi(progetto, modello, capsys):
    _classifica_prova(modello)
    capsys.readouterr()
    assert not main(["passaggi", "--fonte", FONTE, "--tema", "sanita"])
    uscita = capsys.readouterr().out
    assegnati, resto = uscita.split("Scartati con punteggio basso", 1)
    scartati, senza = resto.split("Senza temi", 1)
    assert "-0002" in assegnati and "0,90" in assegnati and "pagina 2" in assegnati
    assert "-0003" in scartati and "0,15" in scartati
    assert "-0001" in senza
    assert "-0004" not in uscita


def test_vista_del_revisore_toglie_gli_zeri_e_ordina_gli_scartati_dal_piu_alto(progetto, modello, capsys):
    modello.risposte.append(_risposta(
        (1, [("sanita", 0)]), (2, [("sanita", 0.05)]), (3, [("sanita", 0.15)]), (4, [("sanita", 0.1)])))
    assert not main(["classifica", "--fonte", FONTE])
    capsys.readouterr()
    assert not main(["passaggi", "--fonte", FONTE, "--tema", "sanita"])
    uscita = capsys.readouterr().out
    scartati = uscita.split("Scartati con punteggio basso", 1)[1].split("Senza temi", 1)[0]
    assert "(3)" in scartati and "-0001" not in scartati
    assert scartati.index("-0003") < scartati.index("-0004") < scartati.index("-0002")


def test_vista_del_revisore_senza_classificazione_lo_dice(progetto, capsys):
    assert main(["passaggi", "--fonte", FONTE, "--tema", "sanita"]) == 1
    assert "classifica" in capsys.readouterr().out
