# Contribuire a elezio

elezio è mantenuto da una persona sola, con circa 5 ore a settimana. I contributi sono benvenuti, dentro alcune regole che servono a tenere il sito neutrale e verificabile.

## Segnalare un errore

Se una scheda attribuisce a un partito qualcosa che il suo programma non dice, o lo dice in modo diverso, apri una [segnalazione](https://github.com/simones99/elezio/issues/new?template=segnalazione.yml) indicando partito, tema, elezione e, se puoi, la pagina del documento fonte. Vale per chiunque: lettori, giornalisti, partiti. Ogni correzione pubblicata finisce nel registro pubblico delle correzioni.

## Contenuti

Le schede seguono una regola dura: nessuna posizione senza citazione testuale dal documento fonte ([ADR 0003](docs/adr/0003-nessuna-posizione-senza-citazione.md)). Per questo:

- una PR che modifica una scheda è una proposta: la scheda torna pubblicabile solo quando il maintainer, unico revisore, la verifica e la porta a `verificata`;
- ogni citazione deve esistere alla lettera nel documento fonte, alla pagina indicata; la CI lo controlla;
- non si accettano sintesi che aggiungono qualcosa oltre le citazioni, né posizioni dedotte.

Schema dei file in [docs/schema-scheda.md](docs/schema-scheda.md), affermazioni del quiz in [docs/quiz.md](docs/quiz.md).

## Codice

PR sul codice benvenute. Per modifiche non piccole apri prima una issue, così ne parliamo prima che tu ci lavori. Le decisioni di fondo sono negli [ADR](docs/adr/) e nella [mappa](https://github.com/simones99/elezio/issues/1): una PR che le contraddice va discussa lì.

## Licenze dei contributi

Chi contribuisce lo fa con la stessa licenza del progetto: [AGPL-3.0](LICENSE) per il codice, [CC BY-SA 4.0](contenuti/LICENSE) per i contenuti in `contenuti/`. Non serve firmare nulla. Non aggiungere materiale di terze parti senza licenza; se ne aggiungi con licenza, aggiungi la voce in [CREDITS.md](CREDITS.md) seguendo le regole scritte lì.

## Comportamento

Vale il [codice di condotta](CODE_OF_CONDUCT.md). Le issue non sono il posto per discutere quale partito abbia ragione: si discute solo se elezio riporta correttamente quello che i documenti dicono.
