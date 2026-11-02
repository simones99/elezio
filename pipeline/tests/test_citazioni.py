"""Verifica delle citazioni contro il testo estratto (docs/pipeline.md, ADR 0005)."""

from elezio_pipeline.citazioni import pagine_del_testo, verifica_citazione

TESTO_ESTRATTO = """=== pagina 5 ===
Fine della sezione sulla scuola, con più insegnanti.

=== pagina 6 ===
AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO
Riforma del Titolo V per riportare la salute
alla gestione diretta dello Stato.

=== pagina 7 ===
Più risorse per i pronto soccorso.
"""

PAGINE = pagine_del_testo(TESTO_ESTRATTO)


def test_citazione_presente_alla_pagina_indicata_passa():
    esito = verifica_citazione(PAGINE, 6, "AUMENTO DELLE RETRIBUZIONI PER IL PERSONALE SANITARIO")
    assert esito.ok
    assert esito.pagina == 6


def test_citazione_alterata_non_passa():
    esito = verifica_citazione(PAGINE, 6, "AUMENTO DEGLI STIPENDI PER IL PERSONALE SANITARIO")
    assert not esito.ok
    assert esito.motivo


def test_a_capo_e_spazi_multipli_non_contano():
    assert verifica_citazione(PAGINE, 6, "per riportare la salute alla   gestione diretta").ok


def test_virgolette_apostrofi_e_trattini_tipografici_si_equivalgono():
    pagine = pagine_del_testo("=== pagina 1 ===\nL’accesso «universale» – “subito”\n")
    assert verifica_citazione(pagine, 1, "L'accesso \"universale\" - \"subito\"").ok


def test_sillabazione_a_fine_riga_si_toglie():
    pagine = pagine_del_testo("=== pagina 1 ===\nil personale sani-\ntario pubblico\n")
    assert verifica_citazione(pagine, 1, "il personale sanitario pubblico").ok


def test_maiuscole_e_accenti_contano():
    pagine = pagine_del_testo("=== pagina 1 ===\nPiù risorse\n")
    assert not verifica_citazione(pagine, 1, "piu risorse").ok
    assert not verifica_citazione(pagine, 1, "Piu risorse").ok
    assert not verifica_citazione(pagine, 1, "più risorse").ok


def test_due_pezzi_non_contigui_non_passano():
    assert not verifica_citazione(PAGINE, 6, "Riforma del Titolo V [...] alla gestione diretta").ok
    assert not verifica_citazione(PAGINE, 6, "Riforma del Titolo V alla gestione diretta").ok


def test_citazione_vuota_non_passa():
    assert not verifica_citazione(PAGINE, 6, "").ok
    assert not verifica_citazione(PAGINE, 6, "  \n ").ok


def test_pagina_adiacente_passa_e_corregge_il_numero():
    assert verifica_citazione(PAGINE, 5, "Riforma del Titolo V").pagina == 6
    assert verifica_citazione(PAGINE, 7, "Riforma del Titolo V").pagina == 6


def test_oltre_una_pagina_di_scarto_non_passa():
    esito = verifica_citazione(PAGINE, 7, "Fine della sezione sulla scuola")
    assert not esito.ok


def test_la_pagina_indicata_vince_sulle_adiacenti():
    pagine = pagine_del_testo("=== pagina 1 ===\nstessa frase\n=== pagina 2 ===\nstessa frase\n")
    assert verifica_citazione(pagine, 2, "stessa frase").pagina == 2


def test_intervallo_cerca_a_cavallo_delle_pagine():
    pagine = pagine_del_testo("=== pagina 12 ===\nuna frase che\n=== pagina 13 ===\ncontinua dopo\n")
    assert verifica_citazione(pagine, "12-13", "una frase che continua dopo").pagina == "12-13"
    assert not verifica_citazione(pagine, 12, "una frase che continua dopo").ok


def test_pagina_che_non_esiste_non_passa():
    assert not verifica_citazione(PAGINE, 99, "Riforma del Titolo V").ok
    assert not verifica_citazione(PAGINE, "non-numero", "Riforma del Titolo V").ok
