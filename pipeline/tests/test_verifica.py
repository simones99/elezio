"""`pipeline verifica` sulle schede: i vincoli di docs/schema-scheda.md controllabili fuori dal sito."""

import datetime

import pytest
from conftest import FONTE

from elezio_pipeline.__main__ import main

CITAZIONE = "Uno psicologo di base in ogni distretto."
OGGI = datetime.date(2026, 11, 2)


def scheda(**cambi):
    base = {
        "partito": "prova", "tema": "sanita", "elezione": 2022, "posizione": "dichiarata",
        "titolo": "Più psicologi", "citazioni": [{"fonte": FONTE, "pagina": 2, "testo": CITAZIONE}],
        "stato": "bozza", "aggiornata_il": OGGI,
    }
    return {k: v for k, v in (base | cambi).items() if v is not None}


def _verifica(capsys):
    capsys.readouterr()
    codice = main(["verifica"])
    return codice, capsys.readouterr().out


def test_scheda_corretta_passa(progetto, capsys):
    progetto.scrivi_scheda(scheda())
    codice, uscita = _verifica(capsys)
    assert codice == 0, uscita
    assert "schede: ok" in uscita


def test_senza_schede_passa(progetto, capsys):
    assert _verifica(capsys)[0] == 0


def test_citazione_alterata_a_mano_fa_fallire(progetto, capsys):
    progetto.scrivi_scheda(scheda(citazioni=[{"fonte": FONTE, "pagina": 2, "testo": "Uno psicologo in ogni condominio."}]))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "2022/prova/sanita.md" in uscita
    assert "non trovata" in uscita


def test_citazione_oltre_la_pagina_adiacente_fa_fallire(progetto, capsys):
    pagine = progetto.fonti_dir / "testo" / f"{FONTE}.txt"
    pagine.write_text(pagine.read_text(encoding="utf-8") + "\n=== pagina 4 ===\nAltro.\n", encoding="utf-8")
    progetto.scrivi_scheda(scheda(citazioni=[{"fonte": FONTE, "pagina": 4, "testo": CITAZIONE}]))
    assert _verifica(capsys)[0] == 1


@pytest.mark.parametrize("cambi, errore", [
    ({"citazioni": []}, "senza citazioni"),
    ({"titolo": None}, "titolo"),
    ({"posizione": "assente", "titolo": None}, "assente"),
    ({"posizione": "assente", "titolo": "Un titolo", "citazioni": []}, "titolo"),
    ({"posizione": "inferita"}, "posizione"),
    ({"stato": "pubblicata"}, "stato"),
    ({"aggiornata_il": None}, "aggiornata_il"),
    ({"stato": "verificata"}, "verificata_il"),
    ({"stato": "verificata", "verificata_il": OGGI}, "revisore"),
    ({"tema": "fisco"}, "tema"),
    ({"partito": "altro"}, "partito"),
    ({"elezione": 2027}, "elezione"),
    ({"citazioni": [{"fonte": "2022-inesistente", "pagina": 2, "testo": CITAZIONE}]}, "2022-inesistente"),
    ({"citazioni": [{"fonte": FONTE, "testo": CITAZIONE}]}, "pagina"),
    ({"campo_nuovo": 1}, "campo_nuovo"),
])
def test_scheda_non_valida_fa_fallire(progetto, capsys, cambi, errore):
    progetto.scrivi_scheda(scheda(**cambi), partito="prova", tema="sanita", elezione=2022)
    codice, uscita = _verifica(capsys)
    assert codice == 1, uscita
    assert errore in uscita


def test_fonte_che_non_include_il_partito_fa_fallire(progetto, capsys):
    progetto.scrivi_scheda(scheda(partito="altro"))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "non include" in uscita


def test_fonte_di_un_altra_elezione_fa_fallire(progetto, capsys):
    progetto.scrivi_scheda(scheda(elezione=2027))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "elezione" in uscita


def test_tema_che_non_esiste_fa_fallire(progetto, capsys):
    progetto.scrivi_scheda(scheda(tema="inesistente"))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "inesistente" in uscita


def test_oltre_300_parole_di_citazioni_fa_fallire(progetto, capsys):
    lunga = " ".join(["parola"] * 301)
    pagine = progetto.fonti_dir / "testo" / f"{FONTE}.txt"
    pagine.write_text(pagine.read_text(encoding="utf-8") + f"\n{lunga}\n", encoding="utf-8")
    progetto.scrivi_scheda(scheda(citazioni=[{"fonte": FONTE, "pagina": 3, "testo": lunga}]))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "300" in uscita


def test_file_senza_frontmatter_fa_fallire(progetto, capsys):
    p = progetto.scheda()
    p.parent.mkdir(parents=True)
    p.write_text("solo testo\n", encoding="utf-8")
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "frontmatter" in uscita


def test_id_di_citazione_duplicato_fa_fallire(progetto, capsys):
    c = {"id": "uno", "fonte": FONTE, "pagina": 2, "testo": CITAZIONE}
    progetto.scrivi_scheda(scheda(citazioni=[c, c]))
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "uno" in uscita


def test_corpo_vuoto_fa_fallire(progetto, capsys):
    progetto.scrivi_scheda(scheda(), corpo="")
    codice, uscita = _verifica(capsys)
    assert codice == 1
    assert "sintesi" in uscita


def test_senza_il_repo_privato_controlla_lo_schema_e_lo_dice(progetto, capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("ELEZIO_FONTI", str(tmp_path / "non-esiste"))
    progetto.scrivi_scheda(scheda(citazioni=[{"fonte": FONTE, "pagina": 2, "testo": "Non controllabile qui."}]))
    codice, uscita = _verifica(capsys)
    assert codice == 0, uscita
    assert "senza elezio-fonti" in uscita
    progetto.scrivi_scheda(scheda(citazioni=[]))
    assert _verifica(capsys)[0] == 1
