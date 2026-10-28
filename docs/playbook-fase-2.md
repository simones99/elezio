# Playbook Fase 2: dai programmi 2027 alle schede online

Ultimo aggiornamento: 28 ottobre 2026. Deciso nel ticket [Playbook Fase 2: dalle pubblicazioni dei programmi 2027 alle schede online](https://github.com/simones99/elezio/issues/12). Pipeline in [pipeline.md](pipeline.md), quiz in [quiz.md](quiz.md), termini in [GLOSSARY.md](../GLOSSARY.md). I tempi di questo file sono stime: la prova generale li sostituisce con quelli misurati.

## Calendario relativo al voto

Tutte le date sono contate dal giorno del voto, **T**. La legislatura XIX scade nell'autunno 2027: senza voto anticipato, i programmi escono intorno ad agosto 2027 (nel 2022 deposito 12-14 agosto, pubblicazione il 24 agosto). Il playbook non dipende dal mese: parte dal decreto di scioglimento.

La Fase 2 ha due parti:

- **Preparazione** (marzo e aprile 2027, dentro il budget di 130 ore): chiudere la checklist di prontezza, prova generale compresa.
- **Esecuzione** (da T-44 a T): il playbook vero, con un budget di ore proprio, fuori dalle 130.

| Quando | Cosa |
| --- | --- |
| Decreto di scioglimento | Il maintainer fissa la data del voto nella configurazione; l'Action di monitoraggio calcola il calendario. |
| Prima del deposito | Se un partito pubblica la versione nativa del programma, la pipeline gira come riscaldamento: nessuna revisione, nessuna pubblicazione. |
| T-44 | Verifica del perimetro (sotto). L'Action inizia il controllo giornaliero di Elezioni trasparenti. |
| T-44 → T-32 | Deposito (T-44 → T-42) e pubblicazione del Ministero (entro T-32). Per ogni programma che compare: acquisizione, estrazione, OCR, classificazione, bozze; il maintainer conferma il YAML della fonte. |
| Tutti pubblicati, oppure T-32 | Parte la revisione del primo tema, al primo dei due eventi. |
| T-32 → T-2 | Una PR per tema, nell'ordine di `contenuti/temi.yaml`. Merge = tema pubblicato. |
| circa T-20 | Il quiz 2027 si accende alla ventesima affermazione verificata (circa 10 temi). Lancio pubblico. |
| T-15 | Da qui nessun aggregato pubblicato dagli analytics (ticket [Diritti su loghi, PDF e citazioni; analytics senza cookie](https://github.com/simones99/elezio/issues/4)). Le pubblicazioni dei temi continuano. |
| T-1, T | Congelamento: nessun merge, il sito resta online com'è. |

## Checklist di prontezza

La preparazione è finita quando è tutta spuntata, prima di T-44.

- [ ] Action di monitoraggio deployata e testata sul JSON di Elezioni trasparenti 2022.
- [ ] `pipeline acquisisci --elezione 2022` funzionante end-to-end dal JSON del Ministero.
- [ ] `alias` aggiornati in tutti i file partito, Futuro Nazionale compreso.
- [ ] Credito API caricato, tetto per run impostato.
- [ ] Template della PR per tema (sotto).
- [ ] Striscia di copertura in home, avviso "programmi 2027 in revisione" sui temi e avviso del quiz 2022 già nel sito, spenti.
- [ ] Prova generale fatta, tempi misurati riportati in questo file.

### Prova generale

Il playbook giocato per intero sui dati 2022, come se il Ministero avesse appena pubblicato: `acquisisci --elezione 2022` dal JSON, estrazione, bozze, poi la revisione cronometrata di 2 temi completi (schede e affermazioni). Misura i minuti veri per scheda e per affermazione e trova i buchi del playbook. È il risultato principale della preparazione.

## Monitoraggio

Una GitHub Action con cron giornaliero, attiva da T-44, legge il JSON di Elezioni trasparenti e apre una issue appena compare il programma di un partito in perimetro. È gratuita e non dipende dalla memoria di nessuno. I siti dei partiti non sono monitorati.

## Fonte

Si pubblica solo dalla copia depositata al Ministero, più il programma esteso per i temi che il depositato non copre (regola di [schema-scheda.md](schema-scheda.md)). Le versioni native pubblicate prima del deposito non si revisionano: nel 2022 le copie depositate erano spesso più corte e le citazioni andrebbero rifatte.

## Perimetro a T-44

Il criterio di inclusione si ricontrolla al deposito, prima che giri la pipeline, aggiornando `alias` e `inclusione` dei file partito.

- **Partito in perimetro che non presenta liste**: "non si presenta", nessuna scheda 2027; le schede 2022 restano.
- **Partito in lista comune o in accordo di coalizione**: fonte condivisa, come nel 2022.
- **Partito nuovo**: entra solo se soddisfa il criterio (per il 2027, in pratica, 5 parlamentari in carica).

La proposta per Presidente del Consiglio, obbligatoria dal 2026, è un fatto del partito per l'elezione: va sulla pagina partito 2027 con la citazione dalla copia depositata, non è una scheda e non entra nel quiz.

## Revisione per tema

Unità di lavoro e di pubblicazione: un tema, con tutti i partiti disponibili. Ordine: `contenuti/temi.yaml`.

Una PR per tema contiene:

1. le schede 2027 del tema, una per partito disponibile, portate a `verificata` con la checklist di [pipeline.md](pipeline.md#revisione);
2. le 2 affermazioni del quiz 2027 del tema con le risposte dei partiti, scritte a mano dopo la verifica delle schede ([quiz.md](quiz.md#criteri-di-formulazione)).

Il merge pubblica il tema. Dentro un tema non si taglia la verifica: il tema esce intero o non esce.

**Copertura**: un tema esce con i partiti disponibili e non aspetta i ritardatari. Un partito senza documento fonte 2027 è "non disponibile", che è diverso da posizione assente.

**Ritardatario**: se il programma di un partito arriva quando alcuni temi sono già usciti, si apre una PR per partito con le sue schede sui temi già pubblicati (fino a 12, circa 2 ore). Questa PR ha la precedenza sul tema successivo, perché un buco su un partito pesa sulla neutralità più di un tema in meno. Il partito diventa partito del quiz appena ha la fonte, quindi le affermazioni a cui non risponde escono dal quiz da sole finché non si completano o riscrivono (ADR 0007).

## Cosa vede il lettore

- **Tema non ancora aggiornato**: le schede 2022, marcate con l'elezione di riferimento, con l'avviso "programmi 2027 in revisione". Mai 2022 e 2027 mescolati nello stesso tema: il confronto resta alla pari.
- **Home**: una striscia di copertura, "7 temi su 12 aggiornati ai programmi 2027", con l'elenco.
- **Quiz 2022 in transizione**: resta online finché il 2027 non ha 20 affermazioni pubblicabili, con l'avviso "basato sui programmi 2022, non su quelli di questa elezione", e sparisce dalla home appena c'è un documento fonte 2027.

Testi e UI di striscia e avvisi non sono ancora prototipati.

## Ore

| Voce | Stima |
| --- | --- |
| Acquisizione, conferma di 10 YAML fonte, controllo OCR | circa 4 h |
| Per tema: 10 schede × 10 min più 2 affermazioni (circa 40 min) | circa 2 h 20 |
| 12 temi | circa 28 h |
| Lancio | circa 4 h |
| **Totale** | **circa 36 h** |

Budget dichiarato: **15 ore a settimana da T-32 a T-15**. Sostituisce le "10 ore a settimana per 2 settimane" del ticket [Pipeline da programma a schede verificate](https://github.com/simones99/elezio/issues/9), che non bastavano una volta aggiunte le affermazioni.

## Taglio

Nessuna data di taglio intermedia: si pubblicano temi fino a T-2. Se le ore non bastano, l'ordine di `temi.yaml` è il taglio: i temi non fatti restano sul 2022 con l'avviso. Da T-1 c'è il congelamento, per prudenza sul silenzio elettorale.

## Lancio

Il lancio pubblico coincide con l'accensione del quiz 2027, non con una data fissa. Prima si comunica poco: il pubblico arriva per il quiz.

Indirizzo: `elezio.pages.dev`, l'unico indirizzo ufficiale, senza dominio proprio (ticket [Nome e dominio definitivi, handle social](https://github.com/simones99/elezio/issues/19)).

Canali: il maintainer promuove elezio dai propri account personali su **Instagram** e **Reddit**, più il contatto diretto con qualche giornalista o docente. Il progetto non ha canali propri: `@elezio` su Instagram è registrato solo per difesa da imitazioni, vuoto, con bio e link al sito, e non si usa.

Regole per chi promuove:

1. ogni post su elezio dichiara che è un progetto del maintainer, aperto, e porta alla pagina metodologia;
2. da T-44 al voto, sugli account usati per promuoverlo, niente contenuti di parte;
3. su Reddit si posta solo dove le regole del subreddit lo permettono (thread dedicati, per esempio in r/italy), un post per subreddit, senza ripetizioni.

Contatto: una casella gratuita a nome del progetto su Proton (server in UE), separata dall'email personale, indicata nelle pagine metodologia e crediti; in più un template di issue "segnalazione" su GitHub. Ogni correzione che ne nasce va nel registro pubblico delle correzioni.

## Voto anticipato

Se il decreto arriva prima che la preparazione sia finita, si parte dal punto della checklist in cui si è, con quello che c'è: monitoraggio e acquisizione a mano se l'Action non è pronta, temi in ordine finché ci sono ore.
