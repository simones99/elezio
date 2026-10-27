# elezio: roadmap fino alle politiche 2027

Ultimo aggiornamento: 27 ottobre 2026. Le decisioni aperte vivono come ticket figli della [Mappa: elezio v1](https://github.com/simones99/elezio/issues/1); questo file è la vista temporale, non l'elenco delle decisioni.

## Vincoli

- Una persona sola più agenti AI, circa 5 ore a settimana.
- Da oggi ad aprile 2027: circa 26 settimane, circa 130 ore totali.
- Budget sotto 20 euro al mese.
- La legislatura XIX scade nell'autunno 2027. I programmi si depositano tra il 44° e il 42° giorno prima del voto e il Ministero dell'Interno li pubblica nella sezione Elezioni trasparenti entro circa 32 giorni prima del voto (DPR 361/1957 art. 14-bis, legge 165/2017 art. 4). Il prodotto deve essere pronto prima di quella finestra.

Conseguenza: ogni fase ha un budget in ore e un solo risultato. Quando una fase sfora, si taglia il contenuto, non si sposta la scadenza.

## Fase 0: decidere (novembre e dicembre 2026, circa 30 ore)

Risultato: tutte le decisioni della mappa chiuse, dati 2022 strutturati, repo pubblico.

- Ricerche già chiuse il 27 ottobre 2026 (findings sui branch `research/*`): Open Election Compass riusabile come bundle statico; fonti 2022 sulle copie depositate al Ministero, 5 su 8 da OCR; regole su loghi, PDF, citazioni e analytics (GoatCounter).
- Decidere i 12 temi, lo schema dati della scheda, lo stack, il modello del quiz, la pipeline da programma a schede.
- Prototipo usa e getta di scheda e confronto su mobile.
- Nome, dominio, licenze, `CREDITS.md`, repo pubblico.
- Preparare i 10 documenti fonte 2022 (PDF, hash, testo estratto) nella struttura decisa.

Uscita della fase: ADR scritti, glossario aggiornato, mappa senza ticket aperti sul nucleo v1.

## Fase 1: costruire la beta sui dati 2022 (gennaio e febbraio 2027, circa 50 ore)

Risultato: sito online in beta pubblica entro il 28 febbraio 2027.

- Scaffolding del sito con lo stack deciso e il componente quiz riusato.
- Pipeline: dal PDF alla bozza di scheda con LLM, revisione umana, pubblicazione. Budget di revisione: circa 10 minuti per scheda, 120 schede, circa 20 ore.
- Pagine: elenco partiti, pagina tema con schede, confronto tra 2-3 partiti, quiz, risultato del quiz, metodologia, crediti.
- Analytics senza cookie con l'evento "quiz completato".
- Beta pubblica: condividere con 10-20 persone di fiducia, raccogliere correzioni nel registro pubblico.

Niente feature oltre il nucleo. Ogni idea nuova finisce nella mappa come fog.

## Fase 2: rilasciare sui programmi 2027 (marzo e aprile 2027, circa 50 ore)

Risultato: sito aggiornato sui programmi 2027 entro pochi giorni dalla loro pubblicazione, poi lancio pubblico.

- Playbook pronto prima (ticket dedicato nella mappa): per ogni partito, dove uscirà il programma, se usare la copia depositata o quella nativa del sito di partito, come gira la pipeline, quanto tempo serve per 120 schede. Finestra utile: dai 44 ai 32 giorni prima del voto.
- Le schede 2022 restano visibili come storia, marcate chiaramente con l'elezione di riferimento; le schede 2027 le affiancano o le sostituiscono secondo lo schema deciso.
- Aggiornare le affermazioni del quiz solo se una posizione cambia davvero.
- Lancio: post pubblici, contatto con qualche giornalista o docente, misurazione dei quiz completati.

Se le elezioni vengono anticipate rispetto alla primavera 2027, la Fase 2 parte appena i programmi escono, con quello che c'è.

## Dopo v1 (non pianificato)

In ordine di probabilità, non di promessa: pagina storia e risultati riusando Electio Italia, modalità cieca, confronto promesse 2022 contro atti della legislatura, finanziamenti ai partiti come modulo separato, ricerca semantica sui programmi.

## Come si lavora

- Ogni sessione di lavoro parte dalla mappa: si prende il primo ticket della frontiera, lo si assegna, lo si risolve, lo si chiude.
- Le decisioni difficili diventano ADR in `docs/adr/`; i termini diventano voci di `GLOSSARY.md`.
- I findings di ricerca vivono su branch `research/<nome>`, linkati dal ticket, mai mergiati.
