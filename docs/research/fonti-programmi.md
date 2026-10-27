# Fonti dei programmi 2022 e scadenze di pubblicazione dei programmi 2027

Ticket: https://github.com/simones99/elezio/issues/3

Data della ricerca: 27 ottobre 2026. Tutti i link sono stati verificati con una richiesta HTTP in quella data, salvo dove indicato.

## Sintesi

- Per 9 partiti su 10 esiste un programma ufficiale per le politiche del 25 settembre 2022 ed è ancora scaricabile. La fonte più stabile è la sezione "Elezioni trasparenti" del Ministero dell'Interno (dait.interno.gov.it), che conserva la copia depositata al Viminale di ogni lista. Futuro Nazionale non esisteva nel 2022: ha un manifesto, uno statuto e una "Base Ideologica e Programmatica" (108 pagine, agosto 2026) sul proprio sito.
- Attenzione alla differenza fra programma depositato e programma di campagna. Fratelli d'Italia, Lega e Forza Italia hanno depositato tutte e tre lo stesso documento di coalizione ("Per l'Italia. Accordo quadro di programma per un Governo di centrodestra", 15 punti), non i programmi di partito che circolavano in campagna (il "Programma di governo" della Lega di 202 pagine, la brochure di FdI). Il M5S ha depositato la versione breve (13 pagine) e non quella completa (251 pagine). Il PD ha depositato una versione di 24 pagine che precede l'aggiornamento del 18 agosto (37 pagine).
- Cinque copie depositate su otto sono scansioni senza livello di testo (FdI, FI, Lega, PD, +Europa): servono OCR. Per questi partiti conviene usare il PDF nativo pubblicato dal partito e tenere la copia DAIT come prova di autenticità.
- Il Manifesto Project (versione 2026a) non copre le politiche italiane 2022: nell'elenco partiti la copertura dell'Italia si ferma al 2018. I termini d'uso vietano comunque la redistribuzione dei dati, quindi non è una fonte utilizzabile per pubblicare testi o codifiche sul sito.
- Per il 2027 la legge fissa un calendario preciso rispetto al giorno del voto (T): il programma va depositato al Viminale insieme al contrassegno fra le ore 8 di T-44 e le ore 16 di T-42; il Ministero lo pubblica nella sezione "Elezioni trasparenti" entro 10 giorni dalla scadenza del deposito, quindi entro T-32. Nel 2022 il deposito è avvenuto il 12-14 agosto e la pagina è andata online il 24 agosto, esattamente 10 giorni dopo.
- Novità rilevante: la legge 9 ottobre 2026, n. 180 (in vigore dal 24 ottobre 2026) ha riscritto il sistema elettorale e modificato l'art. 14-bis del DPR 361/1957. Il programma deve ora indicare "la persona da indicare come proposta per l'incarico di Presidente del Consiglio dei ministri" e le liste coalizzate devono dichiarare lo stesso nome. Le liste che non depositano il programma o non indicano quel nome vengono ricusate. Le finestre temporali di deposito e pubblicazione non sono cambiate.

## Metodo

Fonti primarie: Normattiva (testo vigente del DPR 361/1957, della L. 165/2017, della L. 180/2026 e della Costituzione), dait.interno.gov.it (sezione "Elezioni trasparenti" delle politiche 2022, con il file JSON che alimenta la tabella dei contrassegni), interno.gov.it (notizie del 2 e 24 agosto 2022, FAQ 2022), siti dei partiti, manifesto-project.wzb.eu (termini d'uso, API pubblica, codebook 2026a). Il seed https://github.com/programmielettorali/programmielettorali.github.io è stato letto dal bundle JavaScript (il sito è una app Vue, i link sono dentro `js/app.93416542.js`; ultimo commit 9 agosto 2022). Ogni PDF è stato scaricato e misurato con `pdftotext` (conteggio pagine e caratteri estratti); le scansioni sono state ispezionate a vista sulle prime due pagine.

## Tabella partito per partito

Per ogni partito la colonna "Documento" distingue la copia depositata al Viminale (pubblicata su dait.interno.gov.it: è l'unica versione con valore legale e la prova di che cosa la lista ha effettivamente presentato) dalla versione di campagna pubblicata dal partito. Pagine e nota sul testo si riferiscono al file indicato nella riga.

| Partito | Documento | URL | Pagine | Coalizione o lista | Testo | Note |
|---|---|---|---|---|---|---|
| Fratelli d'Italia | Depositato al Viminale: "Per l'Italia. Accordo quadro di programma per un Governo di centrodestra" con logo FdI in copertina | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/68/%2868_progr_2_%29-programma.pdf | 19 | Coalizione (centrodestra), depositato dalla lista "Fratelli d'Italia con Giorgia Meloni", capo forza politica Giorgia Meloni | Scansione, serve OCR | Programma di coalizione in 15 punti. Il PDF nativo dello stesso testo è ancora su ANSA: https://www.ansa.it/documents/1660243246870_CENTRODESTRA.pdf (17 pagine, testo estraibile). |
| Fratelli d'Italia | Programma di partito 2022 (brochure) | https://www.fratelli-italia.it/programma/ (pagina) e https://www.fratelli-italia.it/wp-content/uploads/2022/08/Brochure_programma_FdI_qr_def.pdf (file) | n.d. | Lista | n.d. | Il link al PDF risponde 404 il 27/10/2026; la pagina esiste ancora con il bottone "Scarica il programma in PDF" ma il file non c'è più. Esiste uno snapshot Wayback del 6 gennaio 2023 (https://web.archive.org/web/20230106132018/https://www.fratelli-italia.it/wp-content/uploads/2022/08/Brochure_programma_FdI_qr_def.pdf) che non sono riuscito a scaricare per rate limiting (HTTP 429): da verificare. |
| Partito Democratico | Depositato al Viminale: "Programma del gruppo politico Partito Democratico - Italia Democratica e Progressista" | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/75/%2875_progr_2_%29-programma_politiche_2022.pdf | 24 | Lista (capo forza politica Enrico Letta) | Scansione, serve OCR | Versione depositata il 12-14 agosto, precedente all'aggiornamento del 18 agosto. |
| Partito Democratico | "Insieme per un'Italia democratica e progressista", aggiornamento del 18 agosto 2022 | https://www.partitodemocratico.it/wp-content/uploads/AGGIORNAMENTO-PROGRAMMA_INSIEMEPERUNITALIADEMOCRATICAEPROGRESSISTA_180822.pdf | 37 | Lista | Testo estraibile (122.000 caratteri) | Il sito del PD risponde 403 ai client non browser (Cloudflare); il file va scaricato da browser. Copia Wayback funzionante: https://web.archive.org/web/20230225123809/https://www.partitodemocratico.it/wp-content/uploads/AGGIORNAMENTO-PROGRAMMA_INSIEMEPERUNITALIADEMOCRATICAEPROGRESSISTA_180822.pdf |
| Movimento 5 Stelle | Depositato al Viminale: "Programma M5S 2022 - Cuore e coraggio" (versione breve) | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/74/%2874_progr_2_%29-programma_m5s_2022-cuore_e_coraggio.pdf | 13 | Lista (capo forza politica Giuseppe Conte, depositante) | Testo estraibile | Byte per byte identico a https://www.movimento5stelle.eu/wp-content/uploads/2022/09/ProgrammaM5S_politiche2022_breve.pdf |
| Movimento 5 Stelle | Programma completo | https://www.movimento5stelle.eu/wp-content/uploads/2022/09/Programma-M5S-completo-2022-09-12.pdf (pagina indice: https://www.movimento5stelle.eu/elezioni-politiche-2022-programma-m5s/) | 251 | Lista | Testo estraibile (515.000 caratteri) | Datato 12 settembre 2022, quindi posteriore al deposito. È la versione da usare per le schede tematiche. |
| Lega | Depositato al Viminale: "Per l'Italia. Programma per un Governo di centrodestra" con logo Lega | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/9/%289_progr_2_%29-lega_per_salvini_premier.programma.pdf | 14 | Coalizione (centrodestra), depositato dalla lista "Lega per Salvini Premier", capo forza politica Matteo Salvini | Scansione di bassa qualità, serve OCR | Stesso testo dell'accordo quadro; impaginazione diversa dalla copia FdI. |
| Lega | "Elezioni politiche 2022. Programma di governo" | https://static.legaonline.it/files/Programma_Lega_2022.pdf | 202 | Lista | Testo estraibile (538.000 caratteri) | Link vivo il 27/10/2026, ma è su un CDN statico: conviene archiviarne una copia. Non ho trovato la pagina del sito legaonline.it che lo linka. |
| Forza Italia | Depositato al Viminale: "Per l'Italia. Accordo quadro di programma per un Governo di centrodestra" con logo FI | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/43/%2843_progr_2_%29-pdfa_-_programma_forza_italia_politiche_2022.pdf | 18 | Coalizione (centrodestra), depositato dalla lista "Forza Italia", capo forza politica Silvio Berlusconi | Scansione, serve OCR | Pagine in orizzontale. Nessun programma di partito 2022 è più online su forzaitalia.it: https://www.forzaitalia.it/programma reindirizza all'immagine del programma per le europee 2024. |
| Alleanza Verdi e Sinistra | Depositato al Viminale: "Programma elettorale per le elezioni politiche del 2022" | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/65/%2865_progr_2_%29-programma_di_alleanza_verdi_e_sinistra_in_pdfa.pdf | 38 | Lista (cartello Europa Verde, Sinistra Italiana, Possibile; capo forza politica Angelo Bonelli) | Testo estraibile (144.000 caratteri) | Stesso contenuto della pagina web https://verdisinistra.it/programma-alleanza-verdi-e-sinistra/ (HTML, nessun PDF sul sito). Depositato con tre contrassegni (italiano, tedesco, sloveno). |
| Azione | Depositato al Viminale: "Programma della lista Azione - Italia Viva - Calenda" | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/7/%287_progr_2_%29-programma_azione-italia_viva-calenda.pdf | 52 | Lista comune Azione + Italia Viva (capo forza politica Carlo Calenda) | Testo estraibile (169.000 caratteri) | Un unico programma per i due partiti. La pagina https://www.azione.it/programma-elettorale-2022/ esiste ancora ma non contiene più il PDF. Copia identica (stessi byte) su https://immigrazione.it/docs/2022/politiche2022-01-azione-e-italia_viva.pdf |
| Italia Viva | Come Azione (programma comune) | Vedi riga Azione | 52 | Lista comune | Testo estraibile | https://www.italiaviva.it/programma risponde 404; nel 2022 IV non ha pubblicato un programma separato. Per le posizioni successive alla rottura con Azione (2023) servono documenti più recenti del partito. |
| +Europa | Depositato al Viminale: "Programma +Europa" | https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/92/%2892_progr_2_%29-piu_europa.programma.pdf | 15 | Lista (capo forza politica Emma Bonino) | Scansione, serve OCR | Scansione a due pagine per foglio; indice in 13 capitoli più allegato "Una Generazione avanti". |
| +Europa | "Una Generazione Avanti. Il programma elettorale di +Europa" | https://assets.nationbuilder.com/piueuropa/pages/1728/attachments/original/1661536519/PROGRAMMA__EUROPA_2022_%284%29.pdf?1661536519 (pagina: https://www.piueuropa.eu/una_generazione_avanti_il_programma_elettorale_di_europa) | 35 | Lista | Testo estraibile (99.000 caratteri) | La pagina linka anche la versione "in pillole", la scheda pensioni, il programma per l'estero, una scheda sul digitale e una su cultura e turismo. |
| Futuro Nazionale | Nessun programma 2022 (partito costituito nel 2026). Vedi sezione dedicata. | https://futuronazionale.it/programma/ | 108 | Lista (non ancora presentata a elezioni politiche) | Testo estraibile | Documento programmatico "B.I.P." in due parti su tre; la terza parte non è ancora pubblicata. |

Conteggio: 9 partiti con programma 2022 reperito e verificato, 1 partito (Futuro Nazionale) senza programma 2022 per costruzione. Per i 9 esiste in tutti i casi almeno una versione con testo estraibile, nativa o di terzi, tranne Forza Italia, per cui l'unico testo di partito è il documento di coalizione (ANSA, testo estraibile).

## Note per partito

### Fratelli d'Italia

La lista "Fratelli d'Italia con Giorgia Meloni" (n. 68 nell'elenco DAIT) ha depositato il programma di coalizione, firmato in copertina, con capo forza politica Giorgia Meloni. La brochure di partito 2022 non è più scaricabile dal sito; la pagina programma del sito propone oggi anche "Programma Centrodestra 2022", "Programma Europa FdI 2024" e "3 anni di Governo" (https://www.fratelli-italia.it/wp-content/uploads/2025/10/3-anni-brochure_Def-5.pdf, ottobre 2025), utile come fonte secondaria per le posizioni attuali.

### Partito Democratico

Depositato un testo di 24 pagine con intestazione "Programma ed indicazione del capo del gruppo politico" firmato da Enrico Letta (lista n. 75, due contrassegni: Italia ed estero). Il PD ha poi pubblicato il 18 agosto un aggiornamento di 37 pagine. I due documenti vanno confrontati prima di scegliere la fonte per le schede: il secondo è più completo e ha testo nativo.

### Movimento 5 Stelle

Depositata la versione breve "Cuore e coraggio" (13 pagine), identica al file "breve" sul sito. Il programma completo di 251 pagine del 12 settembre è la fonte più ricca per i 12 temi. Sulla pagina del programma il M5S pubblica anche statuto e codice etico vigenti (giugno 2025).

### Lega

Depositato il programma di coalizione (14 pagine, scansione di qualità bassa, inclinata). Il "Programma di governo" di 202 pagine è sul CDN static.legaonline.it, raggiungibile ma non linkato da una pagina che sia riuscito a individuare: da archiviare subito.

### Forza Italia

Depositato il programma di coalizione (18 pagine in orizzontale). Non ho trovato un programma di partito 2022 ancora online su un dominio di Forza Italia. La stampa dell'epoca (money.it, affaritaliani.it) cita un documento di proposte FI distinto, ma senza un URL verificabile oggi: lacuna aperta.

### Alleanza Verdi e Sinistra

Unico caso in cui la copia depositata è nativa e completa (38 pagine, PDF/A con testo). La stessa lista ha depositato tre contrassegni (n. 65, id 1064, 1066, 1067 per le versioni in italiano, tedesco e sloveno) con lo stesso programma. Statuti depositati: Sinistra Italiana, Possibile, Europa Verde.

### Azione e Italia Viva

Programma comune di 52 pagine, "Italia sul serio" come slogan. Depositanti Carlo Calenda ed Ettore Rosato, con gli statuti di entrambi i partiti. Dopo la rottura della federazione (2023) i due partiti non hanno più un documento comune: per le posizioni 2027 servirà il programma che ciascuno depositerà separatamente.

### +Europa

Deposito di una scansione a due pagine per foglio (15 fogli, circa 30 pagine logiche) con indice in 13 capitoli e allegato "Una Generazione avanti". Il PDF nativo di 35 pagine sul sito ha lo stesso titolo; corrispondenza puntuale dei contenuti da verificare dopo OCR.

### Futuro Nazionale

Sito ufficiale https://futuronazionale.it (denominazione statutaria "Futuro Nazionale con Roberto Vannacci", codice fiscale 91066810465, PEC futuronazionale@pec.it). Documenti programmatici ufficiali trovati:

- Manifesto: https://futuronazionale.it/manifesto/ (solo HTML, nessun PDF). Sei parole chiave nell'acronimo V.I.T.A.L.E.: Virtù, Identità, Tradizioni, Amore, Libertà, Eccellenza/Entusiasmo.
- Programma: https://futuronazionale.it/programma/ con PDF "B.I.P. - Base Ideologica e Programmatica di Futuro Nazionale per l'Italia del futuro (2027-2037)", prima e seconda parte di tre, datato 24 agosto 2026: https://futuronazionale.it/wp-content/uploads/2026/09/GIUSTIFICATO_SLOT-1-e-2_Base-Programmatica-di-Futuro-Nazionale-24-agosto-2026.pdf (108 pagine, testo estraibile, 384.000 caratteri). Capitoli: dottrina economica e fiscalità; lavoro e PMI; Made in Italy; credito; "assimilazione e remigrazione"; esteri e UE; sicurezza; giustizia; energia; difesa; cybersicurezza; sussidiarietà e riforma della PA; demografia, vita, famiglia. Il documento dichiara esplicitamente che la terza parte deve ancora uscire.
- Statuto: https://futuronazionale.it/statuto/ con PDF https://futuronazionale.it/wp-content/uploads/2026/09/Statuto_aggiornato_Futuro_Nazionale_II.pdf (21 pagine, testo estraibile). L'art. 2 elenca i valori fondamentali, utile per i temi non coperti dal B.I.P.
- Pagina "Elezioni trasparenti" del partito (https://futuronazionale.it/elezioni-trasparenti/): documenta una candidatura alle suppletive del collegio uninominale Calabria 05 (candidato Domenico Giannetta), quindi il partito ha già un precedente di deposito di documentazione elettorale.
- Il sito linka il programma del partito europeo ESN (https://esn-party.eu/what-we-stand-for/political-program/) come riferimento ideologico.

Non verificato: data esatta di costituzione e di registrazione nel registro dei partiti (DL 149/2013); la stampa riporta lo statuto firmato dal notaio a inizio 2026 e l'assemblea fondativa a Roma a giugno 2026 (RSI, Reuters via Internazionale), ma non ho trovato un atto primario. Avvertenza tecnica: le pagine del sito pesano oltre 22 MB ciascuna (immagini inline), quindi i fetch automatici devono avere timeout alti.

## Manifesto Project

- Copertura: l'elenco dei partiti del dataset 2026a (https://manifesto-project.wzb.eu/down/data/2026a/codebooks/parties_MPDataset_MPDS2026a.pdf, sezione 34 Italy) ferma la copertura italiana al 2018 per tutti i partiti rilevanti: PD (32440) 2008-2018, FI (32610) 1994-2006 e 2018, FdI (32630) 2013-2018, Lega (32720) 1992-2018, M5S (32956) 2013-2018. Non compaiono voci per AVS, Azione-IV o +Europa, né alcuna elezione italiana 2022. Il codebook principale dichiara un arco temporale 1920-2025 per il dataset nel complesso, ma l'Italia 2022 non è dentro. Non ho potuto interrogare l'elenco testi del corpus (richiede API key); la conclusione si basa sul codebook pubblico.
- Accesso: la consultazione online del corpus non richiede registrazione; download CSV, pacchetti manifestoR/manifestata e API (`get_core`, `get_parties`, `metadata`, `texts_and_annotations`) richiedono account e API key. Endpoint pubblici senza chiave: `list_core_versions`, `list_metadata_versions`, `get_core_codebook`, `get_core_citation`, `get_corpus_citation` (verificato: https://manifesto-project.wzb.eu/api/v1/list_core_versions.json elenca fino a MPDS2026a; `get_parties` senza chiave reindirizza a `not_authorized`). Fonte: https://manifesto-project.wzb.eu/information/documents/api
- Termini d'uso (https://manifesto-project.wzb.eu/information/documents/terms_of_use): dati forniti a scopo di ricerca scientifica; "Redistribution of the provided data is forbidden" salvo autorizzazione scritta; obbligo di citazione e di invio delle pubblicazioni; nessuna licenza aperta. I termini non distinguono tra codifiche e testi del corpus, quindi il divieto si applica a entrambi.
- Conclusione per elezio: il Manifesto Project non serve né per i testi 2022 (non li ha) né come fonte redistribuibile. Al massimo è un riferimento metodologico per lo schema di codifica tematica (categorie per quasi-frase), che è pubblico nel codebook.

## Quadro legale e scadenze per i programmi 2027

### Norme vigenti (testo multivigente Normattiva al 27 ottobre 2026)

- DPR 30 marzo 1957, n. 361, art. 11: i comizi elettorali sono convocati con decreto del Presidente della Repubblica, pubblicato in Gazzetta Ufficiale "non oltre il 45° giorno antecedente quello della votazione".
- DPR 361/1957, art. 14, primo comma: i partiti depositano al Ministero dell'Interno il contrassegno; se iscritti nel registro dei partiti (DL 149/2013) depositano anche lo statuto, altrimenti una dichiarazione di trasparenza con firma autenticata.
- DPR 361/1957, art. 14-bis, comma 3 (come modificato dalla L. 180/2026): "Contestualmente al deposito del contrassegno di cui all'articolo 14, i partiti o i gruppi politici organizzati depositano il programma elettorale, nel quale dichiarano il nome e cognome della persona da indicare come proposta per l'incarico di Presidente del Consiglio dei ministri. Nel caso di liste collegate tra loro, queste dichiarano obbligatoriamente il medesimo nome." Nuovo comma 3-bis: chi concorre al premio di governabilità dichiara nello stesso atto il collegamento con le liste del Senato. Comma 5: entro T-30 gli Uffici centrali circoscrizionali comunicano le liste ammesse all'Ufficio centrale nazionale, che pubblica in GU l'elenco dei collegamenti entro T-20.
- DPR 361/1957, art. 15: il deposito del contrassegno "deve essere effettuato non prima delle ore 8 del 44° e non oltre le ore 16 del 42° giorno antecedente quello della votazione"; l'ufficio del Ministero resta aperto anche nei festivi dalle 8 alle 20; "il contrassegno deve essere depositato a mano su supporto digitale o in triplice esemplare in forma cartacea".
- DPR 361/1957, art. 22, primo comma, n. 1-ter (L. 165/2017, modificato dalla L. 180/2026): l'Ufficio centrale circoscrizionale ricusa le liste dei partiti che non hanno depositato il programma elettorale "o che non abbiano dichiarato il nome e il cognome della persona da indicare come proposta per l'incarico di Presidente del Consiglio dei ministri".
- Legge 3 novembre 2017, n. 165, art. 4 ("Elezioni trasparenti"): "In apposita sezione del sito internet del Ministero dell'interno, denominata 'Elezioni trasparenti', entro dieci giorni dalla scadenza del termine per il deposito dei contrassegni [...] per ciascun partito, movimento e gruppo politico organizzato che ha presentato le liste sono pubblicati in maniera facilmente accessibile: a) il contrassegno depositato [...]; b) lo statuto ovvero la dichiarazione di trasparenza [...]; c) il programma elettorale con il nome e cognome della persona indicata come capo della forza politica". Comma 2: entro dieci giorni dalla scadenza della presentazione delle liste, le liste di candidati per collegio. L'art. 4 della L. 180/2026 abroga solo il comma 6 dell'art. 3 della L. 165/2017; l'art. 4 resta in vigore. Nota: la L. 180/2026 non ha aggiornato la dicitura "capo della forza politica" nell'art. 4 della L. 165/2017, che rimanda però all'art. 14-bis comma 3 riformato.
- Legge 9 ottobre 2026, n. 180, "Disposizioni in materia di elezioni della Camera dei deputati e del Senato della Repubblica" (GU n. 235 del 9 ottobre 2026, in vigore dal 24 ottobre 2026; Normattiva: https://www.normattiva.it/eli/id/2026/10/09/26G00201/ORIGINAL). Introduce il premio di governabilità e le liste circoscrizionali, modifica gli artt. 1, 14-bis, 18-bis, 22 e altri del DPR 361/1957 e il testo unico del Senato. Non tocca gli artt. 11, 14 e 15 sui termini. Art. 5: per le prime elezioni successive, le condizioni per l'esonero dalla raccolta firme (art. 18-bis, comma 2) devono sussistere al 31 dicembre 2025.
- Costituzione, art. 60: le Camere sono elette per cinque anni. Art. 61: "Le elezioni delle nuove Camere hanno luogo entro settanta giorni dalla fine delle precedenti."
- Gazzetta Ufficiale: nei testi vigenti non è prevista alcuna pubblicazione dei programmi in GU. In GU escono il decreto di convocazione dei comizi (art. 11) e l'elenco dei collegamenti ammessi (art. 14-bis, comma 5). La pubblicazione dei programmi avviene solo sul sito del Ministero.

### Calendario tipo rispetto al giorno del voto (T)

| Scadenza | Adempimento | Fonte |
|---|---|---|
| T-45 al più tardi | Pubblicazione in GU del DPR di convocazione dei comizi | DPR 361/1957 art. 11 |
| T-45 | Il Ministero mette online i fac-simile dei moduli per il deposito | L. 165/2017 art. 1, c. 12, lett. b |
| dalle 8 di T-44 alle 16 di T-42 | Deposito al Viminale di contrassegno, statuto o dichiarazione di trasparenza, programma elettorale con il nome del candidato premier | DPR 361/1957 artt. 14, 14-bis c. 3, 15 |
| entro T-32 | Pubblicazione di contrassegni, statuti e programmi nella sezione "Elezioni trasparenti" | L. 165/2017 art. 4, c. 1 ("entro dieci giorni dalla scadenza del termine per il deposito") |
| dalle 8 di T-35 alle 20 di T-34 | Presentazione delle liste presso le Corti d'appello | DPR 361/1957 art. 20 (non modificato) |
| entro T-30 | Comunicazione delle liste ammesse all'Ufficio centrale nazionale | DPR 361/1957 art. 14-bis c. 5 |
| entro T-24 | Pubblicazione delle liste di candidati in "Elezioni trasparenti" | L. 165/2017 art. 4, c. 2 |
| entro T-20 | Pubblicazione in GU dei collegamenti ammessi | DPR 361/1957 art. 14-bis c. 5 |

Precedente 2022 (voto 25 settembre): deposito contrassegni 12-13 agosto ore 8-20 e 14 agosto ore 8-16 (notizia interno.gov.it del 2 agosto 2022: https://www.interno.gov.it/it/notizie/verso-elezioni-politiche-25-settembre-2022-adempimenti-agosto); 101 contrassegni depositati, 75 ammessi (notizia del 18 agosto: https://www.interno.gov.it/it/notizie/elezioni-politiche-2022-75-i-contrassegni-ammessi-dal-viminale); liste 21-22 agosto; sezione trasparenza online il 24 agosto (https://www.interno.gov.it/it/notizie/elezioni-politiche-2022-line-sezione-trasparenza). Il JSON della pagina riporta `dt_rep: 29/08/2022` come data dell'ultimo aggiornamento dei dati. FAQ ufficiali 2022: https://dait.interno.gov.it/elezioni/faq/faq-elezioni-politiche-2022 (FAQ 3 e 8).

### Dove e in che formato

- URL della sezione: https://dait.interno.gov.it/elezioni/trasparenza (indice) e, per il 2022, https://dait.interno.gov.it/elezioni/trasparenza/elezioni-politiche-2022. Per il 2027 è ragionevole attendersi `https://dait.interno.gov.it/elezioni/trasparenza/elezioni-politiche-2027` e una cartella `POLITICHE_<AAAAMMGG>`; da confermare quando esce.
- La pagina è una tabella DataTables caricata via AJAX da un file JSON statico: `https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/POLITICHE_20220925.json` (campi: `n_ord`, `id_dep`, `partito`, `nome_c`/`cogn_c` per il capo della forza politica, `f_contr` per l'immagine del contrassegno, `e_rappr` per mandanti e depositanti, `e_file` con `tp_doc` 2 = programma, 3 = statuto, 6 = dichiarazione di trasparenza). I file stanno in `https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/<n_ord>/<f_doc>`; i contrassegni in `.../Contrassegni/Accettato/Piccolo/<f_contr>`. Nel 2022 il JSON elenca 38 soggetti con 33 programmi, 29 statuti e 20 dichiarazioni di trasparenza. Il codice che costruisce la tabella è in `/eligendo/politiche2022/dima-contrassegni.js` e `/weblib/js/eligendo.js`. Il JSON è la via più semplice per automatizzare lo scarico dei programmi 2027 il giorno in cui compaiono.
- Formato dei programmi: PDF, spesso PDF/A (lo dicono i nomi dei file: "pdfa_-_programma_forza_italia", "in_pdfa"). Nel 2022 la maggioranza erano scansioni del cartaceo firmato e timbrato dal notaio, senza livello di testo: su 8 programmi dei partiti in perimetro, 5 richiedono OCR (FdI, FI, Lega, PD, +Europa) e 3 hanno testo nativo (M5S, AVS, Azione-IV). Il nuovo art. 15 ammette il deposito "su supporto digitale", quindi nel 2027 la quota di PDF nativi potrebbe salire, ma non c'è garanzia. La pipeline del sito deve prevedere OCR di default.
- Nessun obbligo di legge impone ai partiti di pubblicare il programma sul proprio sito: per questo la copia DAIT è l'unica fonte certa e va archiviata subito dopo la pubblicazione (nel 2022 la pagina era aggiornata al 29 agosto e i file sono ancora online dopo quattro anni).

### Implicazioni per il playbook della Fase 2

1. Il primo segnale utile è il DPR di convocazione dei comizi in GU (T-45 al più tardi): fissa T e quindi tutte le date. Dalla fine naturale della legislatura (cinque anni dall'elezione del 2022, art. 60 Cost.) ed entro 70 giorni (art. 61) si ricava la finestra massima per il voto 2027, salvo scioglimento anticipato. Non ho verificato su fonte primaria la data della prima riunione delle Camere della XIX legislatura; è il dato da cui calcolare la scadenza naturale.
2. I programmi ufficiali non esistono prima di T-42 (chiusura del deposito) e non sono pubblici prima che il Ministero li metta online, al più tardi T-32. In pratica nel 2022 sono passati 10 giorni esatti. Il sito deve quindi prevedere una finestra di 10 giorni tra la fine del deposito e la disponibilità dei testi, più il tempo di OCR e codifica.
3. I partiti pubblicano quasi sempre una versione di campagna prima del deposito (nel 2022: accordo di centrodestra 11 agosto, PD e Azione-IV 18 agosto, Lega e M5S versioni ampliate dopo il deposito). Queste versioni sono utili per preparare le schede in anticipo ma vanno riconciliate con la copia depositata, che è l'unica con valore legale e che, come nel caso del centrodestra, può essere un documento diverso e più corto.
4. Con la L. 180/2026 le liste coalizzate devono indicare lo stesso candidato premier nel programma: il campo "capo della forza politica" delle schede va rinominato in "proposta per Presidente del Consiglio" e reso un attributo della coalizione.

## Fonti aggiuntive gratuite e stabili per posizioni dichiarate

Verificate il 27 ottobre 2026:

- Statuti depositati al Viminale nel 2022 (stessa cartella DAIT, `tp_doc` 3): FdI, Lega, FI, PD, M5S, Azione, Italia Viva, +Europa, Sinistra Italiana, Possibile, Europa Verde. Sono fonti ufficiali per principi e valori (utili se un tema manca dal programma).
- Statuto e codice etico M5S in vigore dal 23 giugno 2025: https://www.movimento5stelle.eu/doctrasparenza/STATUTO-ASSOCIAZIONE-MOVIMENTO-5-STELLE-in-vigore-dal-23-giugno-2025.pdf e https://www.movimento5stelle.eu/doctrasparenza/CODICE-ETICO-IN-VIGORE-DAL-23-GIUGNO-2025.pdf
- FdI, "3 anni di Governo" (ottobre 2025): https://www.fratelli-italia.it/wp-content/uploads/2025/10/3-anni-brochure_Def-5.pdf; programma europee 2024 sulla stessa pagina programma.
- +Europa, schede tematiche 2022 (pensioni, estero, digitale, cultura e turismo) linkate da https://www.piueuropa.eu/una_generazione_avanti_il_programma_elettorale_di_europa; manifesto attuale https://www.piueuropa.eu/manifesto; Charter of Values (2025): https://assets.nationbuilder.com/piueuropa/pages/72/attachments/original/1739178890/Charter_of_Values-VF.pdf
- Azione, Charter of Values (settembre 2026): https://www.azione.it/wp-content/uploads/2026/09/Charter-of-Values-VF.pdf
- Futuro Nazionale: statuto art. 2 (valori) e B.I.P. (vedi sopra).
- Seed esterno: https://github.com/programmielettorali/programmielettorali.github.io (licenza nel repo, ultimo aggiornamento 9 agosto 2022). Link utili ancora vivi: Lega, M5S, +Europa, AVS, ANSA centrodestra; link morto per script: PD (403). Contiene anche liste fuori perimetro (Italexit, Unione Popolare, Italia Sovrana e Popolare, Possibile, Europa Verde, Articolo 1, PSI) e tre link DAIT (n. 43 FI, 48, 68 FdI).

Non verificate ma segnalate dalla ricerca (fonti secondarie, da usare solo come indice): analisi dei programmi 2022 di Pagella Politica (https://pagellapolitica.it/articoli/azione-italia-viva-programma-elezioni-2022, .../lega-programma-elezioni-2022, .../europa-verde-sinistra-italiana-programma-elezioni-2022), schede dell'Osservatorio Conti Pubblici Italiani (https://osservatoriocpi.unicatt.it/ocpi-Programma%20Azione%20Italia%20Viva.pdf), studio accademico Trastulli e Mastroianni, "What's new under the sun? A corpus-linguistic analysis of the 2022 Italian election campaign themes in party manifestos", Modern Italy 2023 (https://doi.org/10.1017/mit.2023.45).

## Cosa non sono riuscito a verificare

- Contenuto della brochure FdI 2022 (file 404 sul sito; snapshot Wayback non scaricabile per HTTP 429 durante la ricerca).
- Esistenza di un programma di partito Forza Italia 2022 distinto dal documento di coalizione, con URL ancora vivo.
- Corrispondenza esatta fra la scansione +Europa depositata (15 fogli) e il PDF nativo di 35 pagine, e fra il PD depositato (24 pagine) e l'aggiornamento (37 pagine): richiede OCR.
- Copertura Italia 2022 nel Manifesto Corpus a livello di testi non codificati (serve API key); il codebook 2026a non la elenca.
- Date primarie di costituzione e registrazione di Futuro Nazionale; data della prima riunione delle Camere della XIX legislatura (necessaria per calcolare la scadenza naturale del 2027).
- Pagina del sito Lega che linka Programma_Lega_2022.pdf (il file è vivo ma raggiunto solo per URL diretto).
