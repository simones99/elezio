---
version: 1
slug: "prototipi-10-scheda-confronto-index-html"
primary_target: "prototipi/10-scheda-confronto/index.html"
related_targets: []
---

# Schede e confronto (prototipo ticket #10)

Scope: pagina tema con le schede dei partiti e confronto tra 2-3 partiti, su telefono (390 px) prima di tutto. Visitor mode: Read. Prototipo usa e getta, tre varianti strutturali dello stesso mondo, su branch `prototipo/10-scheda-confronto`.

Audience e compito: elettore 18-35 da telefono che vuole capire in pochi secondi cosa propone un partito su un tema e poterlo verificare. Prova: citazione alla lettera con documento e pagina. Vincoli: confronto leggibile senza JavaScript, terzo partito via `?terzo=`, scheda con titolo, sintesi, citazioni con pagina, livello, tipo di documento, elezione, stato (`docs/schema-scheda.md`).

Esito (28 ottobre 2026): l'utente sceglie il mondo lapidario e la variante D, cioè la pagina A con la mappa di C, con pop-up sul punto ed espansione della riga sulla questione. Il mondo grottesco e le varianti A, B, C restano sul branch come storia.

Domande che il prototipo doveva chiudere: sintesi prima o citazione prima; quanto testo regge uno schermo; come si segnala una posizione assente (e se mostrare i vuoti per sotto-questione).

Contenuti: citazioni vere dai programmi depositati 2022 di M5S, AVS, Azione-Italia Viva (tema Sanità); sintesi e titoli scritti per il prototipo, non verificati; posizione assente e stato contestata solo come esempi fittizi dichiarati.

## Direction contract

THESIS: La pagina di un'etichetta italiana di pregio applicata al dovere civico: capitali lapidarie, grottesco largo, inchiostro bruno su carta calda, tantissima aria. Rifiuta la griglia di card con accento blu dei siti civici e il grigio da modulistica PA.

OWN-WORLD: Fondo carta #FAF8F1, inchiostro bruno #271002, pietra #DED8CF per i riquadri di confronto e di citazione. Titoli in capitali romane da iscrizione (Cinzel), testo e interfaccia in grottesco largo (Archivo esteso). Link in maiuscoletto sottolineato, azioni come bottoni tondi scuri. Nessun colore di partito, nessuna foto; i contrassegni piccoli e inalterati sono l'unica immagine.

STORY: Chi legge capisce in una riga cosa propone ciascun partito sul tema, vede che ogni frase ha la sua pagina, apre la citazione se vuole controllare, e vede con la stessa dignità quando un programma non tratta qualcosa.

FIRST VIEWPORT: Barra sottile con ELEZIO e il percorso; titolo del tema in capitali grandi a sinistra, definizione rientrata sotto; poi la mappa "chi parla di cosa": sotto-questioni in riga, partiti in colonna (contrassegno e sigla), punto pieno, cerchio vuoto o cerchio tratteggiato. Tocco su un punto: pop-up (foglio dal basso su telefono) con le citazioni di quel partito su quella questione e la pagina. Tocco sulla questione: la riga si apre e al posto dei punti compaiono le frasi dei partiti. Sotto la mappa, le schede della variante A: titolo, sintesi, citazioni a un tocco.

FORM: Pinned dall'utente su riferimento (moncalisse.com), dopo tre giri di tiro rifiutati; nessuna posizione nella lista. seed:7ffa4b2693b7e19e

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
