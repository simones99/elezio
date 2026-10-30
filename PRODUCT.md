# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primario: l'elettore indeciso tra i 18 e i 35 anni, da telefono, che legge poco e vuole farsi un'idea in cinque minuti, verificandola da solo se vuole. Arriva da un link condiviso, da una ricerca o dal quiz, spesso nelle settimane prima del voto.

Seconda ondata, non bersaglio di v1: giornalisti, insegnanti, ricercatori.

## Product Purpose

Rendere fruibili i programmi elettorali italiani: per tema, in linguaggio semplice, sempre con la citazione testuale e la pagina del documento originale. Tre funzioni in v1: schede per tema (10 partiti per 12 temi, 120 schede), confronto tematico tra due o tre partiti, quiz di orientamento.

Successo: sito online entro il 28 febbraio 2027 con 120 schede verificate e un quiz funzionante; almeno 500 quiz completati entro il giorno del voto.

## Positioning

Nessuna posizione senza citazione: ogni frase attribuita a un partito è sostenuta da un brano alla lettera di un documento fonte registrato (URL ufficiale, hash, pagina), e la build verifica che il brano esista nel testo estratto. La macchina propone le bozze, una persona verifica ogni scheda, e la metodologia (temi, criteri di inclusione, prompt, modello del quiz) è pubblica.

## Operating Context

- Lettura da telefono, in momenti brevi; il confronto si condivide come URL (`/confronto/<tema>/<a>-<b>/`).
- Le fonti sono i programmi depositati al Ministero dell'Interno (sezione Elezioni trasparenti), spesso PDF scansionati; il programma esteso del partito si cita solo per i temi che il depositato non copre.
- Beta sui programmi delle politiche 2022, rilascio pubblico sui programmi 2027 appena pubblicati (entro circa 32 giorni prima del voto).

## Capabilities and Constraints

- Sito statico (Astro), nessun backend, nessun account, nessuna risposta salvata; il confronto deve essere leggibile senza JavaScript. Vedi `docs/stack.md`.
- Una scheda: titolo, sintesi di 2-5 frasi, citazioni con pagina (massimo 300 parole in totale), livello (partito o coalizione), tipo di documento, elezione di riferimento, stato di verifica (`verificata`, `contestata` con avviso). Una posizione è `dichiarata` o `assente`, mai inferita. Vedi `docs/schema-scheda.md`.
- Una scheda superata da un'elezione successiva resta visibile come storia, con link alla più recente.
- Solo italiano, solo web responsive. Analytics senza cookie (GoatCounter).
- Termini del dominio in `GLOSSARY.md`: scheda, posizione, citazione, sintesi, confronto, tema, sotto-questione.

## Brand Commitments

- Nome: elezio, all'indirizzo `elezio.pages.dev`, senza dominio proprio (ticket #19).
- Neutralità visibile: nessun colore di partito nell'interfaccia. I partiti si riconoscono per sigla e contrassegno ufficiale, piccolo, nella forma depositata, mai alterato, sempre con alternativa testuale; i contrassegni non entrano mai nel brand di elezio (icone, anteprime social, materiale promozionale).
- Il quiz è "orientamento sui programmi", mai "per chi votare".
- Il risultato non deve sembrare schierato (gerarchie, ordine o colori che suggeriscono una preferenza), né un sito della pubblica amministrazione, né un paper accademico illeggibile da telefono.

## Evidence on Hand

- `contenuti/temi.yaml`: i 12 temi con definizioni e sotto-questioni.
- Fonti 2022 censite in `docs/research/fonti-programmi.md` sul branch `research/fonti-programmi`; nessuna scheda verificata esiste ancora.
- Regole su loghi, PDF e citazioni in `docs/research/diritti-privacy-analytics.md` sul branch `research/diritti-privacy-analytics`.
- Non esistono testimonianze, utenti, numeri d'uso o citazioni stampa: non vanno inventati.

## Product Principles

- La citazione è la prova: deve essere sempre a un tocco dalla sintesi, con documento e pagina.
- Parità di trattamento: stessi spazi, stessa gerarchia, ordine non preferenziale per tutti i partiti.
- Un'assenza è un'informazione: "il documento non tratta il tema" si mostra con la stessa dignità di una posizione.
- Semplice prima, verificabile subito dopo: la sintesi si legge in pochi secondi, la fonte è lì per chi vuole controllare.

## Accessibility & Inclusion

Target WCAG 2.2 AA. Lettura su schermi piccoli, anche con connessione lenta: niente che dipenda da JavaScript per mostrare il contenuto.
