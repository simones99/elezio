"""Segmentazione dei PDF con testo nativo (issue #33)."""

from elezio_pipeline.estrai import Riga, segmenta

# Pagina 11 del programma M5S 2022 depositato, righe come le dà pdfplumber,
# seguita dall'intestazione e dal piè di pagina della 12. I titoli di sezione
# hanno corpo 21-26, le proposte sono in maiuscolo a corpo testo (12) e sono
# separate da un'interlinea doppia.
M5S_PAGINA_11 = [
    Riga(11, "PROGRAMMA ELETTORALE 2022", x1=191, top=19, corpo=12.1),
    Riga(11, "CUORE E CORAGGIO", x1=217, top=37, corpo=22.3),
    Riga(11, "PER L’ITALIA DI DOMANI", x1=260, top=57, corpo=22.3),
    Riga(11, "DALLA PARTE DEGLI ANIMALI:", x1=415, top=136, corpo=26.0),
    Riga(11, "CONTRO CACCIA, BRACCONAGGIO", x1=378, top=163, corpo=21.0),
    Riga(11, "E VIOLENZE", x1=174, top=186, corpo=21.0),
    Riga(11, "PROGRESSIVA ABOLIZIONE DELLA CACCIA A PARTIRE DAL DIVIETO DI ACCESSO AI TERRENI", x1=549, top=233, corpo=12.0),
    Riga(11, "PRIVATI, CONTRASTO AL BRACCONAGGIO", x1=284, top=248, corpo=12.0),
    Riga(11, "PENE SEVERE PER CHI COMMETTE VIOLENZE O MALTRATTAMENTI CONTRO GLI ANIMALI", x1=531, top=276, corpo=12.0),
    Riga(11, "CASHBACK VETERINARIO per ottenere direttamente su conto corrente le detrazioni connesse", x1=553, top=305, corpo=12.0),
    Riga(11, "alle spese veterinarie e per farmaci effettuate con strumenti di pagamento elettronici", x1=508, top=319, corpo=12.0),
    Riga(11, "DALLA PARTE DELLE NUOVE TECNOLOGIE:", x1=557, top=383, corpo=26.0),
    Riga(11, "PER UN PAESE DIGITALE E MODERNO", x1=404, top=410, corpo=21.0),
    Riga(11, "STESURA DELLA CARTA DEI DIRITTI DIGITALI", x1=303, top=455, corpo=12.0),
    Riga(11, "Riconoscimento dell’accesso alla rete quale diritto costituzionale e copertura nazionale con", x1=540, top=469, corpo=12.0),
    Riga(11, "banda ultralarga", x1=149, top=483, corpo=12.0),
    Riga(11, "CAPO DELLA FORZA POLITICA GIUSEPPE CONTE", x1=208, top=824, corpo=7.0),
    Riga(12, "PROGRAMMA ELETTORALE 2022", x1=191, top=19, corpo=12.1),
    Riga(12, "CUORE E CORAGGIO", x1=217, top=37, corpo=22.3),
    Riga(12, "PER L’ITALIA DI DOMANI", x1=260, top=57, corpo=22.3),
    Riga(12, "CAPO DELLA FORZA POLITICA GIUSEPPE CONTE", x1=208, top=824, corpo=7.0),
]

SEZIONE_ANIMALI = "DALLA PARTE DEGLI ANIMALI: CONTRO CACCIA, BRACCONAGGIO E VIOLENZE"


def test_le_proposte_in_maiuscolo_a_corpo_testo_restano_nel_testo():
    passaggi = segmenta(M5S_PAGINA_11, "m5s")

    animali = [(p.sezione, p.testo) for p in passaggi if p.sezione == SEZIONE_ANIMALI]
    assert animali == [
        (SEZIONE_ANIMALI, "PROGRESSIVA ABOLIZIONE DELLA CACCIA A PARTIRE DAL DIVIETO DI ACCESSO AI "
                          "TERRENI PRIVATI, CONTRASTO AL BRACCONAGGIO"),
        (SEZIONE_ANIMALI, "PENE SEVERE PER CHI COMMETTE VIOLENZE O MALTRATTAMENTI CONTRO GLI ANIMALI"),
        (SEZIONE_ANIMALI, "CASHBACK VETERINARIO per ottenere direttamente su conto corrente le detrazioni "
                          "connesse alle spese veterinarie e per farmaci effettuate con strumenti di "
                          "pagamento elettronici"),
    ]


def test_intestazione_e_pie_di_pagina_ripetuti_non_finiscono_nei_passaggi():
    passaggi = segmenta(M5S_PAGINA_11, "m5s")

    for ripetuta in ("PROGRAMMA ELETTORALE 2022", "CUORE E CORAGGIO", "CAPO DELLA FORZA POLITICA"):
        assert not [p.id for p in passaggi if ripetuta in p.sezione or ripetuta in p.testo]


# Futuro Nazionale, p106: titoli in maiuscolo allo stesso corpo del testo.
FN_PAGINA_106 = [
    Riga(106, "B.I.P. - Base Ideologica e Programmatica Futuro Nazionale", x1=511, top=14, corpo=11.0),
    Riga(106, "governo non ha mai voluto affidare lo sviluppo delle iniziative agro energetiche a società", x1=511, top=260, corpo=12.0),
    Riga(106, "agricole, lasciando invece spazio a generiche “associazioni in partecipazione”.", x1=426, top=276, corpo=12.0),
    Riga(106, "PESCA E ACQUACOLTURA", x1=207, top=322, corpo=12.0),
    Riga(106, "Il comparto ittico deve essere parte integrante della strategia nazionale di sovranità alimentare.", x1=510, top=346, corpo=12.0),
    Riga(106, "La nostra visione prevede che le competenze siano accentrate in un unico dipartimento dedicato", x1=510, top=362, corpo=12.0),
    Riga(106, "presso il Ministero dell’Agricoltura e del Cibo, per garantire una regia unica capace di tutelare le", x1=510, top=377, corpo=12.0),
    Riga(106, "imprese dalle imposizioni comunitarie ideologiche.", x1=296, top=393, corpo=12.0),
    Riga(107, "B.I.P. - Base Ideologica e Programmatica Futuro Nazionale", x1=511, top=14, corpo=11.0),
]


def test_con_i_titoli_a_corpo_testo_il_maiuscolo_resta_un_titolo():
    passaggi = segmenta(FN_PAGINA_106, "fn")

    assert [(p.sezione, p.testo) for p in passaggi] == [
        ("", "governo non ha mai voluto affidare lo sviluppo delle iniziative agro energetiche a società "
             "agricole, lasciando invece spazio a generiche “associazioni in partecipazione”."),
        ("PESCA E ACQUACOLTURA",
         "Il comparto ittico deve essere parte integrante della strategia nazionale di sovranità alimentare. "
         "La nostra visione prevede che le competenze siano accentrate in un unico dipartimento dedicato "
         "presso il Ministero dell’Agricoltura e del Cibo, per garantire una regia unica capace di tutelare le "
         "imprese dalle imposizioni comunitarie ideologiche."),
    ]


# Futuro Nazionale, p11: un sottotitolo in minuscolo staccato dal paragrafo che introduce.
FN_PAGINA_11 = [
    Riga(11, "favorire investimenti nell’economia reale nazionale.", x1=300, top=629, corpo=12.0),
    Riga(11, "Una proposta per il rafforzamento della sovranità economica: la moneta fiscale", x1=429, top=669, corpo=12.0),
    Riga(11, "Futuro Nazionale propone di valutare l’introduzione della moneta fiscale quale strumento", x1=510, top=707, corpo=12.0),
    Riga(11, "complementare di politica economica, fondato sulla circolazione volontaria di crediti fiscali e", x1=510, top=721, corpo=12.0),
    Riga(11, "diritti di compensazione tra Stato e contribuenti, senza configurare una moneta alternativa. La", x1=511, top=735, corpo=12.0),
    Riga(11, "formulazione deve essere tecnica e prudente: non uno strumento di rottura, ma un meccanismo", x1=510, top=749, corpo=12.0),
    Riga(11, "ordinato di liquidità fiscale e compensazione.", x1=267, top=763, corpo=12.0),
]


def test_con_i_titoli_a_corpo_testo_un_sottotitolo_resta_attaccato_al_suo_paragrafo():
    passaggi = segmenta(FN_PAGINA_11, "fn")

    assert [p.testo for p in passaggi][-1].startswith(
        "Una proposta per il rafforzamento della sovranità economica: la moneta fiscale "
        "Futuro Nazionale propone di valutare")


# M5S, pagine 1-3: la copertina, l'inizio della pagina 2 e il passaggio dalla 2 alla 3.
M5S_PAGINE_1_3 = [
    Riga(1, "CUORE E", x1=272, top=457, corpo=42.7),
    Riga(1, "CORAGGIO", x1=471, top=445, corpo=42.7),
    Riga(1, "PER", x1=153, top=501, corpo=42.6),
    Riga(1, "L’ITALIA DI", x1=360, top=489, corpo=42.6),
    Riga(1, "DOMANI", x1=515, top=479, corpo=42.7),
    Riga(2, "DALLA PARTE DEI CITTADINI:", x1=401, top=137, corpo=26.0),
    Riga(2, "UN FISCO SEMPLICE E PIÙ LEGGERO", x1=394, top=164, corpo=21.0),
    Riga(2, "CASHBACK FISCALE", x1=172, top=207, corpo=12.0),
    Riga(2, "Introduzione di un meccanismo che permetta l’immediato accredito su conto corrente delle", x1=538, top=222, corpo=12.0),
    Riga(2, "spese detraibili sostenute con strumenti elettronici.", x1=553, top=236, corpo=12.0),
    Riga(2, "DALLA PARTE DEI LAVORATORI E DEL WELFARE:", x1=589, top=504, corpo=25.5),
    Riga(2, "PER UNA VITA DEGNA E SENZA PRECARIETÀ", x1=475, top=530, corpo=21.0),
    Riga(2, "STABILIZZAZIONE DI ‘DECONTRIBUZIONE SUD’ per proteggere e creare nuovi posti di lavoro", x1=540, top=763, corpo=12.0),
    Riga(2, "nel Mezzogiorno", x1=148, top=778, corpo=12.0),
    Riga(3, "UN NUOVO STATUTO DEI LAVORI, DELLE LAVORATRICI E DEI LAVORATORI PER GARANTIRE A", x1=551, top=123, corpo=12.0),
    Riga(3, "DIPENDENTI E AUTONOMI GLI STESSI DIRITTI E LE STESSE TUTELE", x1=415, top=138, corpo=12.0),
    Riga(3, "RIFORMA DEGLI AMMORTIZZATORI SOCIALI IN SENSO UNIVERSALE", x1=416, top=166, corpo=12.0),
    Riga(3, "Anche per autonomi, partite Iva, liberi professionisti e per le nuove tipologie di lavoro", x1=504, top=180, corpo=12.0),
]


def test_con_i_titoli_a_corpo_maggiore_il_cambio_pagina_chiude_paragrafo_e_titolo():
    passaggi = segmenta(M5S_PAGINE_1_3, "m5s")

    lavoratori = "DALLA PARTE DEI LAVORATORI E DEL WELFARE: PER UNA VITA DEGNA E SENZA PRECARIETÀ"
    assert [(p.sezione, p.testo) for p in passaggi] == [
        ("DALLA PARTE DEI CITTADINI: UN FISCO SEMPLICE E PIÙ LEGGERO",
         "CASHBACK FISCALE Introduzione di un meccanismo che permetta l’immediato accredito su conto corrente "
         "delle spese detraibili sostenute con strumenti elettronici."),
        (lavoratori, "STABILIZZAZIONE DI ‘DECONTRIBUZIONE SUD’ per proteggere e creare nuovi posti di lavoro "
                     "nel Mezzogiorno"),
        (lavoratori, "UN NUOVO STATUTO DEI LAVORI, DELLE LAVORATRICI E DEI LAVORATORI PER GARANTIRE A "
                     "DIPENDENTI E AUTONOMI GLI STESSI DIRITTI E LE STESSE TUTELE"),
        (lavoratori, "RIFORMA DEGLI AMMORTIZZATORI SOCIALI IN SENSO UNIVERSALE Anche per autonomi, partite Iva, "
                     "liberi professionisti e per le nuove tipologie di lavoro"),
    ]
