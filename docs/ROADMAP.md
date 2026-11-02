# elezio: roadmap fino alle politiche 2027

Ultimo aggiornamento: 2 novembre 2026. Le decisioni aperte vivono come ticket figli della [Mappa: elezio v1](https://github.com/simones99/elezio/issues/1); questo file è la vista temporale, non l'elenco delle decisioni.

## Vincoli

- Una persona sola più agenti AI, circa 5 ore a settimana.
- Da oggi ad aprile 2027: circa 26 settimane, circa 130 ore totali.
- Budget sotto 20 euro al mese.
- La legislatura XIX scade nell'autunno 2027. I programmi si depositano tra il 44° e il 42° giorno prima del voto e il Ministero dell'Interno li pubblica nella sezione Elezioni trasparenti entro circa 32 giorni prima del voto (DPR 361/1957 art. 14-bis, legge 165/2017 art. 4). Il prodotto deve essere pronto prima di quella finestra.

Conseguenza: ogni fase ha un budget in ore e un solo risultato. Quando una fase sfora, si taglia il contenuto, non si sposta la scadenza.

## Fase 0: decidere (chiusa il 2 novembre 2026, prevista per novembre e dicembre, circa 30 ore)

Risultato: tutte le decisioni della mappa chiuse, dati 2022 strutturati, repo pubblico.

- Ricerche già chiuse il 27 ottobre 2026 (findings sui branch `research/*`): Open Election Compass riusabile come bundle statico; fonti 2022 sulle copie depositate al Ministero (7 documenti fonte, 4 da OCR, verificato nel ticket #27); regole su loghi, PDF, citazioni e analytics (GoatCounter).
- Decidere i 12 temi, lo schema dati della scheda, lo stack, il modello del quiz, la pipeline da programma a schede.
- Prototipo usa e getta di scheda e confronto su mobile.
- Nome, dominio, licenze, `CREDITS.md`, repo pubblico: nome elezio su `elezio.pages.dev`, senza dominio; repo pubblico dal 2 novembre 2026, con la checklist del ticket [Quando e come rendere pubblico il repository](https://github.com/simones99/elezio/issues/21) completata (README, CONTRIBUTING, codice di condotta, template di segnalazione, gitleaks, impostazioni).
- Preparare i 7 documenti fonte 2022 (PDF, hash, testo estratto) nella struttura decisa: sono 7 e non 10 perché FdI, Lega e FI hanno depositato lo stesso accordo e Azione e Italia Viva un programma comune.

Uscita della fase: ADR scritti, glossario aggiornato, mappa senza ticket aperti sul nucleo v1. Condizioni verificate il 2 novembre 2026, prima di aprire i ticket della Fase 1.

Riserva sui dati 2022: fonti, testi estratti e passaggi sono pronti, ma i passaggi non sono ancora classificati e mancano i file dei partiti e le schede. Sono lavoro della Fase 1 ([#43](https://github.com/simones99/elezio/issues/43), [#44](https://github.com/simones99/elezio/issues/44), [#46](https://github.com/simones99/elezio/issues/46)).

## Fase 1: costruire la beta sui dati 2022 (gennaio e febbraio 2027, circa 50 ore)

Risultato: sito online in beta pubblica entro il 28 febbraio 2027.

Il lavoro è diviso nei ticket da [#37](https://github.com/simones99/elezio/issues/37) a [#55](https://github.com/simones99/elezio/issues/55), figli della mappa, con le dipendenze su GitHub.

- Scaffolding del sito: Astro in `sito/`, contenuti letti da `contenuti/`, Open Election Compass self-hostato in `/quiz/`, deploy su Cloudflare Pages (ADR 0006, `docs/stack.md`).
- Pipeline: dal PDF alla bozza di scheda con LLM, revisione umana, pubblicazione. Budget di revisione: circa 10 minuti per scheda, 120 schede, circa 20 ore.
- Pagine: elenco partiti, pagina tema con schede, confronto tra 2-3 partiti, quiz, risultato del quiz, metodologia, crediti.
- Quiz 2022: 24 affermazioni scritte a mano con le risposte dei partiti, circa 6-8 ore dopo la verifica delle schede (ADR 0007, `docs/quiz.md`).
- Analytics senza cookie con l'evento "quiz completato".
- Beta pubblica: condividere con 10-20 persone di fiducia, raccogliere correzioni nel registro pubblico.

Niente feature oltre il nucleo. Ogni idea nuova finisce nella mappa come fog.

## Fase 2: rilasciare sui programmi 2027

Risultato: sito aggiornato sui programmi 2027 entro pochi giorni dalla loro pubblicazione, poi lancio pubblico. Il playbook completo, con date contate dal giorno del voto (T), è in `docs/playbook-fase-2.md` (deciso in [Playbook Fase 2](https://github.com/simones99/elezio/issues/12)). La legislatura scade nell'autunno 2027: senza voto anticipato i programmi escono intorno ad agosto, quindi la Fase 2 si divide in due.

### Preparazione (marzo e aprile 2027, circa 50 ore)

Risultato: checklist di prontezza del playbook tutta spuntata.

- Action di monitoraggio di Elezioni trasparenti, `pipeline acquisisci` end-to-end sul JSON 2022, alias dei partiti, credito API.
- Striscia di copertura in home, avviso "programmi 2027 in revisione" sui temi, avviso sul quiz 2022: pronti e spenti.
- Prova generale cronometrata sui dati 2022 (2 temi completi): i tempi misurati sostituiscono le stime del playbook.

### Esecuzione (da T-44 al voto, circa 36 ore fuori dalle 130)

- Pubblicazione solo dalle copie depositate al Ministero; la pipeline gira su ogni programma appena compare.
- Revisione per tema nell'ordine di `contenuti/temi.yaml`, una PR per tema con schede e 2 affermazioni del quiz, 15 ore a settimana da T-32 a T-15.
- Le schede 2022 restano visibili come storia; un tema non ancora aggiornato mostra le 2022 con l'avviso.
- Lancio pubblico all'accensione del quiz 2027 (20 affermazioni, circa T-20): post, contatto con qualche giornalista o docente, misurazione dei quiz completati.
- Temi pubblicati fino a T-2, congelamento da T-1.

Se il voto viene anticipato, l'esecuzione parte al decreto di scioglimento dal punto della checklist in cui si è.

## Dopo v1 (non pianificato)

In ordine di probabilità, non di promessa: pagina storia e risultati riusando Electio Italia, modalità cieca, confronto promesse 2022 contro atti della legislatura, finanziamenti ai partiti come modulo separato, ricerca semantica sui programmi.

## Come si lavora

- Ogni sessione di lavoro parte dalla mappa: si prende il primo ticket della frontiera, lo si assegna, lo si risolve, lo si chiude.
- Le decisioni difficili diventano ADR in `docs/adr/`; i termini diventano voci di `GLOSSARY.md`.
- I findings di ricerca vivono su branch `research/<nome>`, linkati dal ticket, mai mergiati.
