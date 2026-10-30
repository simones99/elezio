# elezio

I programmi elettorali dei partiti italiani, per tema, in linguaggio semplice e sempre con la citazione testuale e la pagina del documento depositato. Con un confronto tra partiti e un quiz di orientamento.

Indirizzo: [elezio.pages.dev](https://elezio.pages.dev) (non ancora online).

## Stato

In progettazione. La beta sui programmi delle politiche 2022 è prevista entro il 28 febbraio 2027; i programmi 2027 entrano appena il Ministero dell'Interno li pubblica. Tempi e fasi in [docs/ROADMAP.md](docs/ROADMAP.md), decisioni aperte e chiuse nella [Mappa: elezio v1](https://github.com/simones99/elezio/issues/1).

## Come funziona

- **Fonte**: la copia del programma depositata al Ministero dell'Interno (sezione Elezioni trasparenti), registrata con URL e hash.
- **Nessuna posizione senza citazione**: ogni posizione attribuita a un partito ha almeno una citazione testuale con pagina, e la build verifica che il testo esista davvero nel documento ([ADR 0003](docs/adr/0003-nessuna-posizione-senza-citazione.md)).
- **Revisione umana**: un modello linguistico prepara le bozze, il maintainer le verifica una per una prima della pubblicazione. Modelli e prompt sono versionati e pubblici ([docs/pipeline.md](docs/pipeline.md)).
- **Sito statico**: nessun backend, nessun account, il quiz si calcola nel browser e le risposte non lasciano il dispositivo ([ADR 0001](docs/adr/0001-sito-statico-senza-backend.md)).

## Documenti

- [docs/VISION.md](docs/VISION.md): perché, per chi, cosa c'è in v1.
- [GLOSSARY.md](GLOSSARY.md): i termini del dominio (scheda, posizione, citazione, tema...).
- [docs/schema-scheda.md](docs/schema-scheda.md), [docs/quiz.md](docs/quiz.md), [docs/stack.md](docs/stack.md), [docs/playbook-fase-2.md](docs/playbook-fase-2.md).
- [docs/adr/](docs/adr/): le scelte difficili e il loro perché.
- [PRODUCT.md](PRODUCT.md) e [DESIGN.md](DESIGN.md): prodotto e sistema visivo.

## Segnalazioni e contributi

Hai trovato un errore in una scheda? Apri una [segnalazione](https://github.com/simones99/elezio/issues/new?template=segnalazione.yml). Per contribuire leggi [CONTRIBUTING.md](CONTRIBUTING.md) e il [codice di condotta](CODE_OF_CONDUCT.md).

## Licenze

Codice sotto [AGPL-3.0](LICENSE). Contenuti editoriali in `contenuti/` sotto [CC BY-SA 4.0](contenuti/LICENSE), esclusi le citazioni dei documenti fonte e i contrassegni dei partiti. Componenti di terze parti in [CREDITS.md](CREDITS.md), avvisi in [NOTICE](NOTICE).
