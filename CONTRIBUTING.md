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

## PR da fork e verifica delle citazioni

Su `main` entrano solo PR con tutti i controlli della CI superati. Uno di questi, `verifica delle citazioni`, legge i PDF e i testi estratti dei documenti fonte da un repository privato, e per farlo usa il secret `ELEZIO_FONTI_TOKEN`. GitHub non passa i secret alle PR aperte da un fork, quindi:

- se la tua PR non tocca `contenuti/`, `pipeline/` né `.github/`, il controllo non serve: viene saltato, vale come superato e la PR segue la strada normale;
- se tocca `contenuti/` o `pipeline/`, `test della pipeline` gira lo stesso (schema e test, senza secret), mentre `verifica delle citazioni` diventa rossa con il messaggio "Il secret ELEZIO_FONTI_TOKEN non è disponibile". Non è un errore tuo, e non serve correggere nulla;
- se tocca `.github/`, i suoi controlli non contano, di qualunque colore siano: una PR da fork gira con i workflow che lei stessa modifica, quindi potrebbe cambiare proprio i controlli che dovrebbero fermarla.

Negli ultimi due casi il maintainer:

1. legge tutta la PR, in particolare ogni modifica a `.github/`: nel repository i workflow della PR girerebbero con accesso al secret;
2. riporta i tuoi commit, senza cambiarli, su un ramo del repository (`task/<n>-<slug>`, con il numero del ticket o, se non c'è, della tua PR) e apre una PR gemella che rimanda alla tua: lì la CI gira con il secret e con i workflow già letti;
3. se i controlli passano, mergia la PR gemella con un merge commit (mai squash né rebase, e il ramo si aggiorna con un merge), così i commit restano a tuo nome con i loro messaggi originali. Se un controllo fallisce, riporta l'errore nella tua PR: correggi lì e il passaggio si ripete.

La verifica delle citazioni non resta mai saltata senza che si veda: niente merge con i controlli rossi, niente `pull_request_target`, che darebbe il secret a codice non ancora letto.

## Licenze dei contributi

Chi contribuisce lo fa con la stessa licenza del progetto: [AGPL-3.0](LICENSE) per il codice, [CC BY-SA 4.0](contenuti/LICENSE) per i contenuti in `contenuti/`. Non serve firmare nulla. Non aggiungere materiale di terze parti senza licenza; se ne aggiungi con licenza, aggiungi la voce in [CREDITS.md](CREDITS.md) seguendo le regole scritte lì.

## Comportamento

Vale il [codice di condotta](CODE_OF_CONDUCT.md). Le issue non sono il posto per discutere quale partito abbia ragione: si discute solo se elezio riporta correttamente quello che i documenti dicono.
