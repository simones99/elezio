"""`pipeline estrai` su una fonte già classificata non perde la classificazione (#78)."""

import json

import pytest
from conftest import FONTE

from elezio_pipeline import estrai
from elezio_pipeline.__main__ import main
from elezio_pipeline.estrai import Riga


@pytest.fixture(autouse=True)
def pdf_finto(monkeypatch):
    """Il PDF di prova non è un PDF: le righe arrivano già lette."""
    monkeypatch.setattr(estrai, "leggi_righe", lambda _: [
        Riga(1, "Introduzione generale al programma.", 400, 100, 10),
        Riga(2, "Uno psicologo di base in ogni distretto.", 400, 100, 10),
    ])


def _lavoro(progetto):
    return progetto.fonti_dir / "lavoro" / FONTE


def _classifica(progetto):
    progetto.scrivi_passaggi([dict(p, punteggi={"sanita": 0.9, "fisco": 0}, temi=["sanita"])
                              for p in progetto.passaggi()])
    return progetto.percorso_passaggi.read_text(encoding="utf-8")


def test_classificata_con_registro_resta_la_copia_e_il_registro_si_toglie(progetto, capsys):
    classificata = _classifica(progetto)
    registro = progetto.registra_classificazione()
    copia = _lavoro(progetto) / registro["copia"]
    copia.parent.mkdir()
    copia.write_text(classificata, encoding="utf-8")
    assert not main(["estrai", "--fonte", FONTE])
    assert copia.read_text(encoding="utf-8") == classificata
    assert not (_lavoro(progetto) / "classificazione.json").exists()
    assert all("temi" not in p for p in progetto.passaggi())
    assert "rilancia pipeline classifica" in capsys.readouterr().out


def test_copia_indicata_dal_registro_mancante_si_ricrea(progetto):
    classificata = _classifica(progetto)
    registro = progetto.registra_classificazione()
    assert not main(["estrai", "--fonte", FONTE])
    assert (_lavoro(progetto) / registro["copia"]).read_text(encoding="utf-8") == classificata


def test_classificata_senza_registro_si_conserva(progetto):
    classificata = _classifica(progetto)
    assert not main(["estrai", "--fonte", FONTE])
    conservate = list((_lavoro(progetto) / "classificazioni").glob("*-senza-registro.jsonl"))
    assert [c.read_text(encoding="utf-8") for c in conservate] == [classificata]


def test_non_classificata_non_cambia_nulla(progetto, capsys):
    assert not main(["estrai", "--fonte", FONTE])
    assert not (_lavoro(progetto) / "classificazioni").exists()
    assert not (_lavoro(progetto) / "classificazione.json").exists()
    assert " ".join(p["testo"] for p in progetto.passaggi()) == (
        "Introduzione generale al programma. Uno psicologo di base in ogni distretto.")
    assert "classificazione precedente" not in capsys.readouterr().out


def test_dopo_estrai_le_bozze_chiedono_di_classificare(progetto, capsys):
    _classifica(progetto)
    progetto.registra_classificazione()
    assert not main(["estrai", "--fonte", FONTE])
    capsys.readouterr()
    assert main(["bozze", "--fonte", FONTE, "--tema", "sanita"])
    assert "lancia prima pipeline classifica" in capsys.readouterr().out
    assert not progetto.scheda().exists()


def test_riclassificare_dopo_estrai_scrive_un_registro_nuovo(progetto, modello):
    _classifica(progetto)
    vecchio = progetto.registra_classificazione()
    assert not main(["estrai", "--fonte", FONTE])
    modello.risposte.append({"passaggi": [{"id": p["id"], "punteggi": {"sanita": 0.9, "fisco": 0}}
                                          for p in progetto.passaggi()]})
    assert not main(["classifica", "--fonte", FONTE])
    nuovo = json.loads((_lavoro(progetto) / "classificazione.json").read_text(encoding="utf-8"))
    assert nuovo["id"] != vecchio["id"]
    assert (_lavoro(progetto) / vecchio["copia"]).exists()
