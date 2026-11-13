# Pipeline: dal documento fonte alle schede verificate

Ultimo aggiornamento: 12 novembre 2026. Decisioni di fondo in [ADR 0005](adr/0005-pipeline-da-programma-a-schede.md); termini in [GLOSSARY.md](../GLOSSARY.md); schema dei file in [schema-scheda.md](schema-scheda.md). Questo file è la vista operativa e cambia a ogni run: modelli, prompt, comandi, costi, checklist. Deciso nel ticket [Pipeline da programma a schede verificate](https://github.com/simones99/elezio/issues/9).

## Passi

| # | Passo | Input | Output | Serve un LLM |
| --- | --- | --- | --- | --- |
| 1 | Acquisizione | URL ufficiale | PDF nel repo privato, SHA-256, copia Wayback, YAML fonte in bozza | no |
| 2 | Estrazione testo | PDF | testo estratto con marcatori di pagina (`pdfplumber` o `pypdf`) | no |
| 3 | OCR | PDF scansionato, anche con strato OCR incorporato | testo estratto (Mistral OCR, una pagina per chiamata; ripiego senza chiave: Tesseract `ita` in Docker) | no (Mistral OCR vuole la chiave, Tesseract no) |
| 4 | Segmentazione | testo estratto | passaggi (paragrafo, pagina, massimo circa 200 parole) | no |
| 5 | Classificazione | passaggi, `temi.yaml` | per ogni passaggio 0..n temi con punteggio | sì (backend `llm` o `jev`) |
| 6 | Bozza | passaggi di un tema, sotto-questioni, dentro/altrove | JSON: posizione, titolo, sintesi, citazioni con pagina | sì |
| 7 | Verifica e rendering | JSON | file scheda `stato: bozza` con `bozza_da`, oppure scarto con nota | no |
| 8 | Revisione | PR per fonte | `stato: verificata` o bozza con nota | no |
| 9 | Verifica in CI | tutte le schede | build bloccata se una citazione non esiste nel testo estratto | no |

Senza endpoint LLM configurato i passi 5 e 6 non partono e le schede si scrivono a mano (`bozza_da` assente). Tutto il resto funziona.

## Comandi

```
pipeline acquisisci --elezione 2027          # legge il JSON di Elezioni trasparenti, scarica i programmi dei partiti in perimetro
pipeline acquisisci --url <url> --fonte <id> --partiti <slug,...> --elezione <anno> [--tipo <tipo>] [--copia-di <fonte>]
pipeline estrai --fonte <id>                 # passi 2-4: testo nativo oppure OCR, poi passaggi
pipeline classifica --fonte <id>             # passo 5
pipeline passaggi --fonte <id> --tema <slug> # per il revisore: passaggi assegnati al tema e possibili perdite
pipeline bozze --fonte <id> --tema <slug>    # passi 6-7
pipeline verifica                            # passo 9: YAML delle fonti, schede e citazioni; in CI con #41
pipeline valuta-classificatore               # precisione e richiamo sul campione d'oro
```

`pipeline acquisisci --elezione 2027` non c'è ancora: arriva con la preparazione della Fase 2. `pipeline bozze` lavora per ora su una coppia fonte-tema alla volta.

Python standalone in `pipeline/`, indipendente dallo stack del sito. Si installa con `pip install -e "./pipeline[test]"`, in modalità modificabile perché prompt e `pipeline.toml` si leggono dalla cartella; i test si lanciano con `python -m pytest` da `pipeline/`. L'umano interviene due volte: conferma il YAML della fonte dopo l'acquisizione (titolo, tipo, partiti condivisi, copia canonica) e revisiona le schede.

## Configurazione

`pipeline.toml` versionato nel repo pubblico; ogni valore è sovrascrivibile dalla variabile d'ambiente indicata. Le chiavi stanno solo nelle variabili d'ambiente.

| Chiave | Variabile | Default |
| --- | --- | --- |
| `base_url` | `ELEZIO_LLM_BASE_URL` | `https://openrouter.ai/api/v1` (alternativa UE stretta: `https://api.mistral.ai/v1`) |
| chiave | `ELEZIO_LLM_API_KEY` | nessuna (passi 5 e 6 disattivati) |
| `modello_sintesi` | `ELEZIO_MODELLO_SINTESI` | `mistralai/mistral-large-4-0` |
| `modello_classificazione` | `ELEZIO_MODELLO_CLASSIFICAZIONE` | `mistralai/ministral-14b-2512` |
| `ocr` | `ELEZIO_OCR` | `mistral-ocr` (alternativa senza chiave: `tesseract`) |
| `provider` | `ELEZIO_LLM_PROVIDER` | `mistral` (su OpenRouter: `provider.order=["mistral"]`, `allow_fallbacks=false`) |
| `classificatore` | `ELEZIO_CLASSIFICATORE` | `llm` (alternativa: `jev`) |
| chiave JEV | `ELEZIO_JEV_API_KEY` | nessuna |
| `tetto_dollari_per_run` | `ELEZIO_TETTO_DOLLARI` | `30`. Funziona solo su OpenRouter, vedi sotto |
| `fonti` | `ELEZIO_FONTI` | `../elezio-fonti`, il clone locale del repo privato accanto al repo pubblico |
| `contenuti` | `ELEZIO_CONTENUTI` | `contenuti`, relativo alla radice del repo |
| `soglia_classificazione` | `ELEZIO_SOGLIA_CLASSIFICAZIONE` | `0.1` |

Client: SDK `openai` con `base_url`, così lo stesso codice gira su OpenRouter, Ollama (`http://localhost:11434/v1`), LM Studio, vLLM. Il backend `jev` usa l'API TypeSafe e vale solo per il passo 5.

Tetto di spesa: la pipeline somma il costo che l'endpoint restituisce in `usage.cost` e si ferma prima della chiamata successiva quando il tetto è raggiunto. Solo OpenRouter restituisce quel campo. Su `api.mistral.ai`, Ollama, LM Studio e vLLM il costo resta 0 e il tetto non scatta: alla prima risposta senza costo il comando stampa una volta `il tetto di spesa non è attivo`, e il costo che riporta alla fine è 0. Lì la spesa si limita dal pannello del fornitore. Si è scelto l'avviso e non una stima dai token perché i prezzi per modello in `pipeline.toml` invecchierebbero senza che nessuno se ne accorga (#68).

Default dei modelli: famiglia Mistral, perché il maintainer vuole l'inferenza in UE. Large 4 per la sintesi, Ministral 3 14B per la classificazione, Mistral OCR per le scansioni. Gli id sono verificati il 30 ottobre 2026 su OpenRouter e su `api.mistral.ai` (tabella sotto); il modello di sintesi si fissa alla prima run delle bozze, provando due o tre modelli su un documento. Criterio: sintesi su un modello della fascia Large/Pro con contesto di almeno 32k; classificazione su un modello della fascia Small/Ministral o un 8-14B locale (Ministral 3 è Apache 2.0 e gira anche su Ollama). Mai usare alias come `mistral-large-latest` in `bozza_da`: l'id registrato deve restare risolvibile.

Residenza UE: i modelli Mistral su OpenRouter vanno bloccati sul provider `mistral` (`provider.order` più `allow_fallbacks=false`), altrimenti OpenRouter può instradare su un altro host. Il gateway OpenRouter stesso però processa la richiesta negli USA sul piano gratuito: la base URL regionale `https://eu.openrouter.ai` è solo sui piani Business ed Enterprise. Per una residenza UE stretta si punta `base_url` direttamente a `https://api.mistral.ai/v1` (endpoint compatibile OpenAI, stesso client) con gli id nativi di Mistral; la stessa API offre anche Mistral OCR in modo nativo.

| Uso | Id su OpenRouter | Id nativo su `api.mistral.ai` |
| --- | --- | --- |
| Sintesi (default) | `mistralai/mistral-large-4-0` | `mistral-large-4-0` |
| Classificazione (default) | `mistralai/ministral-14b-2512` | `ministral-14b-2512` |
| Classificazione, provato | `mistralai/ministral-8b-2512` | `ministral-8b-2512` |
| Classificazione, provato | `mistralai/mistral-small-2603` | `mistral-small-2603` |
| OCR (default) | plugin `file-parser`, `engine: mistral-ocr` | `mistral-ocr-4-1` (Mistral OCR 4.1) |

`mistralai/mistral-large-2512` esiste solo su OpenRouter, senza un id nativo corrispondente: non si usa. Sull'API nativa `mistral-ocr-2512` è Mistral OCR 3.0, non la 4.1, e `mistral-ocr-latest` è un alias da non registrare. Il plugin di OpenRouter non dice quale versione di Mistral OCR applica, per questo `ocr_versione` resta facoltativo. Elenco nativo letto da `GET /v1/models`, che non consuma token; le chiamate della pipeline passano da OpenRouter senza una chiave Mistral collegata, quindi si paga solo OpenRouter.

## OCR

Deciso nel ticket [#28](https://github.com/simones99/elezio/issues/28) misurando su 70 pagine di scansioni 2022: AVS, Lega e FI (accordo di centrodestra). Per ogni documento, 300 citazioni da 15 parole prese da un riferimento pulito con lo stesso contenuto (PDF nativo dell'accordo su ANSA, pagina web del programma AVS), cercate nel testo OCR con la normalizzazione della verifica. I valori sono limiti inferiori, perché il riferimento può differire un po' dal depositato.

| Documento | Strato incorporato | Tesseract | Mistral OCR | Medium 3.5 |
| --- | --- | --- | --- | --- |
| AVS | 60,3% | 72,3% | **86,0%** | 84,3% |
| Lega | n.d. | 74,3% | 91,0% | **94,0%** |
| FI | n.d. | 42,3% | **91,7%** | 91,0% |

- **Mistral OCR è il default.** Via OpenRouter: plugin `file-parser` con `engine: mistral-ocr`, un PDF di una pagina per chiamata, testo letto dalle `annotations` della risposta, provider bloccato su `mistral`. Il guardrail ZDR di OpenRouter non copre i plugin. Costo misurato: circa 0,002 dollari a pagina. Il Markdown dell'uscita si conserva per la segmentazione (`segmenta_markdown`) e si toglie nella normalizzazione.
- **Tesseract è il ripiego senza chiave.** Tesseract `ita` nell'immagine `pipeline/docker/tesseract`, pagine a 300 dpi in scala di grigi, `--psm 1`. Regge le scansioni pulite, non i timbri e le sigle a margine dell'accordo FI. L'immagine Docker si costruisce al primo uso e ogni pagina le passa da stdin, senza cartelle montate; la versione (es. `tesseract 5.3.0 ita`) va in `ocr_versione`. Senza chiave, `pipeline acquisisci` registra `ocr: tesseract`.
- **Il motore lo decide la fonte.** `pipeline estrai` usa il campo `ocr` del YAML, non `ELEZIO_OCR`, e lo scrive in `lavoro/<fonte>/ocr/motore.txt`: una fonte non mescola pagine di due motori, e per cambiarlo si cancella la cartella.
- **Nessun modello generativo come OCR.** Medium 3.5 legge quasi come Mistral OCR, ma sbaglia riscrivendo parole plausibili, che la verifica delle citazioni non vede (ADR 0005).
- **Lo strato OCR incorporato non si usa.** Un PDF depositato con strato di testo prodotto da OCR (AVS 2022) si tratta come una scansione: lo strato resta 12 punti sotto Tesseract.

Il YAML della fonte registra il motore in `ocr` e, se nota, la versione in `ocr_versione` ([schema-scheda.md](schema-scheda.md)).

## Passaggi e classificazione

Un passaggio è un paragrafo del testo estratto con la sua pagina, spezzato se supera circa 200 parole. Riceve 0..n temi perché può contenere più proposte: la regola "ogni proposta un solo tema" si applica alla sintesi, non al passaggio. I passaggi classificati vivono nel repo privato in `lavoro/<fonte>/passaggi.jsonl`.

Nei PDF con testo nativo `segmenta` toglie prima intestazioni e piè di pagina (righe identiche su almeno metà delle pagine). Se il documento ha titoli in un corpo maggiore del testo, come il programma M5S 2022, il titolo è la riga più grande: il maiuscolo a corpo testo è il nome di una proposta. In questo caso chiudono il paragrafo anche uno spazio verticale oltre 1,6 volte l'interlinea e il cambio pagina. Negli altri documenti (Azione-IV, Futuro Nazionale) il titolo è la riga in maiuscolo. I test sono in `pipeline/tests/`: `python -m pytest tests` da `pipeline/` (#33).

Backend `llm`: 20 passaggi per chiamata, prompt con definizione, sotto-questioni, esempi dentro/altrove di ogni tema, output JSON strutturato con il punteggio di tutti i 12 temi per ogni passaggio, imposto dallo schema con una chiave obbligatoria per tema. Un endpoint che non rispetta lo schema può comunque saltare temi o passaggi, o dare risposte inservibili: un punteggio che non è un numero tra 0 e 1, una risposta rotta e una risposta senza contenuto (rifiuto, risposta troncata) valgono come mancanti. I passaggi incompleti si ripetono una volta in una chiamata a parte, e quelli che restano incompleti si salvano così come sono, con un avviso nel comando e una sezione apposita in `pipeline passaggi`. Backend `jev`: stato = un passaggio, 12 domande `Noul` "questo passaggio propone qualcosa su <tema>?", una per tema, con definizione ed esempi nella descrizione; probabilità sotto la soglia scartata.

Campione d'oro: 120 passaggi del programma AVS 2022 depositato etichettati a mano dal maintainer in `pipeline/campione/avs-2022.jsonl` nel repo pubblico (sono citazioni brevi con pagina, entro i limiti decisi nel ticket #4). La copia depositata è una scansione: il testo viene da Mistral OCR, segmentato con `segmenta_markdown`. Due lotti da 60, scelti da `pipeline/campione/seleziona.py`: il primo ha 48 passaggi stratificati per sezione e 12 casi limite, uno per confine di `temi.yaml` (seme 28); il secondo aggiunge un secondo caso limite per i confini che ne hanno un altro (9) e stratificati fino a 120 (seme 29). Ogni riga dice lotto e origine. Le etichette seguono la regola "ogni proposta un solo tema" degli esempi dentro/altrove. Comando: `python -m elezio_pipeline valuta-classificatore --modelli <id>,<id>` da `pipeline/`. `pipeline valuta-classificatore` stampa precisione e richiamo per tema per ogni backend. Il backend con il richiamo migliore diventa il default; sotto il 90 percento di richiamo nessun backend è accettato senza revisione umana della classificazione.

Misura del ticket [#28](https://github.com/simones99/elezio/issues/28) (29-30 ottobre 2026), backend `llm`, 120 passaggi, 121 temi veri, prompt v2, soglia 0,2:

| Modello | Precisione | Richiamo | Costo |
| --- | --- | --- | --- |
| `mistralai/ministral-14b-2512` | 61,9% | **86,0%** | 0,004 $ |
| `mistralai/ministral-8b-2512` | 67,4% | 80,2% | 0,003 $ |
| `mistralai/mistral-small-2603` | 73,7% | 71,9% | 0,005 $ |
| `mistralai/mistral-large-4-0` | 78,2% | 80,2% | 0,110 $ |

Large non fa meglio del 14B sul richiamo, quindi il limite non è la fascia Ministral: sono i confini tra temi (giustizia e ambiente sui reati ambientali, ambiente sul benessere animale) e la soggettività del campione. Con 120 passaggi l'incertezza sul richiamo è di circa ±6 punti. Il backend `jev` non è misurato: manca la chiave.

Misure dei ticket [#37](https://github.com/simones99/elezio/issues/37) e [#58](https://github.com/simones99/elezio/issues/58) (2 novembre 2026), stesso campione, solo sul modello di default. La soglia 0,1 è calcolata sulle stesse previsioni della riga sopra, senza una nuova chiamata:

| Prompt | Schema | Soglia | Temi assegnati | Precisione | Richiamo | Temi persi visibili tra gli scartati | Costo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `classificazione-v2.md` | lista | 0,2 | 168 | 61,9% | 86,0% | n.d. | 0,004 $ |
| `classificazione-v3.md` | lista | 0,2 | 314 | 36,9% | 95,9% | 5 su 5 | 0,009 $ |
| `classificazione-v3.md` | 12 chiavi | 0,2 | 182 | 58,2% | 87,6% | 12 su 15 | 0,006 $ |
| `classificazione-v3.md` | 12 chiavi | **0,1** | 296 | 38,9% | **95,0%** | 3 su 6 | 0,006 $ |

Default `ministral-14b-2512`, `classificazione-v3.md`, schema a 12 chiavi, soglia 0,1. La lista non è affidabile: su M5S 2022 una chiamata su 7 (passaggi 0101-0120) ha ignorato la regola dei 12 temi e ripetendola con la stessa lista è fallita di nuovo, mentre con le 12 chiavi è risultata completa in due prove su due, e nella run sull'intera fonte tutti i 124 passaggi hanno i 12 punteggi. Le chiavi obbligatorie però cambiano il comportamento del modello, che assegna meno temi: a soglia 0,2 il richiamo scenderebbe sotto il 90 percento. Sommando assegnati e scartati, il revisore controlla gli stessi passaggi a soglia 0,1 e a 0,2, ma quelli tra 0,1 e 0,2 arrivano da soli alla bozza invece di dover essere recuperati a mano.

Questa misura va letta con cautela. La soglia è scelta sugli stessi 120 passaggi su cui è misurata, quindi il richiamo è ottimistico. Il risultato è fragile: 108 voci stanno esattamente a 0,1, e a 0,15 il richiamo torna a 87,6%. Il prompt v3 chiama improbabile ciò che sta sotto 0,2, quindi un tema assegnato tra 0,1 e 0,2 è uno che il modello stesso ritiene improbabile. Il prezzo è la precisione: il tema riceve circa 1,8 volte i passaggi della v2, e la bozza può contenere più materiale fuori tema, da fermare in revisione. Gli altri modelli non sono rimisurati con questa configurazione.

La v3 chiede tutti i 12 temi per ogni passaggio perché un invito a elencare in più i temi improbabili non basta: due formulazioni di questo tipo, scartate prima dell'uso, hanno dato 1 e 8 voci sotto 0,2 e nessun tema perso visibile, con richiamo 86,8% e 85,1%.

Per la revisione della classificazione `pipeline passaggi` mostra i passaggi assegnati al tema, quelli scartati con punteggio sopra 0 e sotto la soglia, dal più alto, quelli senza temi e, se ce ne sono, quelli con punteggi incompleti, per cui gli scartati non sono affidabili. Sul campione gli scartati sono in media 10 per tema. I temi persi con punteggio 0 non compaiono tra gli scartati e nessuna vista li mostra: in quella run sono 3 su 6, le altre sono nella sezione qui sotto. Un passaggio con soli punteggi sotto la soglia compare sia tra gli scartati sia tra quelli senza temi.

Limite noto: avere tutti i 12 punteggi non vuol dire che il tema giusto abbia un punteggio sopra 0, quindi le perdite con punteggio 0 restano invisibili, e una posizione può risultare assente anche per questo. Per i passaggi senza il punteggio del tema `pipeline bozze` invece si ferma o mette una nota (sezione [Bozza](#bozza)). Il peso di queste perdite è misurato qui sotto.

### Temi persi e punteggio 0

Misura del ticket [#61](https://github.com/simones99/elezio/issues/61) (2 novembre 2026): `ministral-14b-2512`, `classificazione-v3.md`, schema a 12 chiavi, soglia 0,1. Sono le etichette del campione d'oro misurate in due modi: classificando il campione da solo, in ordine di id, quindi senza i passaggi che nel documento gli stanno accanto, e classificando AVS 2022 intero, come fa `pipeline classifica`. M5S 2022 ha una sola run e nessuna etichetta. I dati grezzi sono in `elezio-fonti`, in `lavoro/misure/61/`.

| Classificazione | Temi assegnati sui 120 passaggi | Precisione | Richiamo | Temi persi su 121 | Di cui a 0 |
| --- | --- | --- | --- | --- | --- |
| Campione da solo, run 1 | 345 | 33,9% | 96,7% | 4 | 3 |
| Campione da solo, run 2 | 312 | 37,5% | 96,7% | 4 | 4 |
| Campione da solo, run 3 | 367 | 31,9% | 96,7% | 4 | 4 |
| AVS intero, run 1 | 343 | 33,5% | 95,0% | 6 | 2 |
| AVS intero, run 2 | 402 | 28,6% | 95,0% | 6 | 3 |

- **Il risultato cambia da una run all'altra anche a temperatura 0.** Su AVS intero le due run assegnano 1357 e 1557 temi, e cambiano 370 decisioni su 5928 (494 passaggi per 12 temi). Il richiamo è stabile, la precisione va letta come un intervallo.
- **Il numero di temi persi varia poco, quali sono cambia.** Sono tra 4 e 6, contando anche la run di #58 che ne ha persi 6. Tra le due condizioni i punteggi si spostano: 0285 passa da 0 a 0,8, 0097 da 0,3-0,8 a 0. La spiegazione più probabile sono i passaggi vicini nella chiamata, ma non è provata.
- **Nessuna coppia resta a 0 in tutte le 5 run.** Solo 0393 si perde sempre, con 0 o 0,01. Tutti gli altri casi a 0 oscillano o sono a 0 in una sola condizione.
- **Il passaggio perso non sparisce dal documento.** Tranne 0285 sul campione da solo, ogni passaggio perso ha un altro tema da 0,5 in su. Non dice però se il tema perso conta: 0341 rispetta questa condizione ed è un errore vero.

Le 10 coppie perse in almeno una run, con il punteggio del tema perso in ogni run. Il giudizio sull'etichetta è una proposta che il maintainer deve confermare, e il campione resta com'è finché non lo fa:

| Passaggio | Etichette (persa in grassetto) | Campione 1, 2, 3 | AVS 1, 2 | Altri temi da 0,5 in su | Etichetta secondo `temi.yaml` |
| --- | --- | --- | --- | --- | --- |
| 0393, consultori familiari | `sanita`, **`giustizia`** | 0, 0, 0 | 0,01, 0 | `sanita`, `famiglia` | dubbia: nessun esempio di `giustizia` ne parla |
| 0285, moratoria delle spese della Difesa | **`europa`** | 0, 0, 0 | 0,8, 0,8 | nessuno | giusta: la spesa militare è in `europa`; errore vero, solo sul campione da solo |
| 0292, comunicazione nonviolenta a scuola | **`europa`** | 0, 0, 0 | 0,1, 0,1 | `scuola` | confine: lo strumento dice `scuola`, il precedente "Educazione civica sull'immigrazione" dice il tema trattato |
| 0390, valori del SSN e dignità della persona | `sanita`, **`giustizia`** | 0,1, 0, 0 | 0,01, 0,1 | `sanita` | dubbia: parla del servizio sanitario |
| 0097, professioni di frontiera delle donne | **`giustizia`** | 0,7, 0,8, 0,3 | 0, 0 | `lavoro` | confine: parità di genere o lavoro |
| 0341, edilizia scolastica | **`scuola`** | 0,8, 0,9, 0,7 | 0,05, 0,05 | `ambiente`, `casa`, `sanita` | giusta: è una sotto-questione di `scuola`; errore vero, visibile tra gli scartati |
| 0413, case popolari | **`famiglia`**, `casa` | 0,1, 0,1, 0,1 | 0, 0 | `casa`, `ambiente` | dubbia: lo strumento è la casa |
| 0472, anagrafe dei rifiuti | **`giustizia`** | 0,1, 0,1, 0,1 | 0,01, 0,01 | `ambiente`, `istituzioni` | confine: reati ambientali, già noto |
| 0476, banche dati ambientali | **`giustizia`** | 0,7, 0,1, 0,1 | 0,15, 0,01 | `ambiente`, `istituzioni` | confine: reati ambientali, già noto |
| 0222, privatizzazione dei beni comuni | **`ambiente`**, `casa` | 0,05, 0,1, 0,1 | 0,8, 0,8 | `casa`, `imprese` | incerta: nel campione la nota del maintainer dice "sono indeciso" |

Se il giudizio è confermato, gli errori veri sono 2 su 10, e nel documento intero uno solo: 0341, a 0,05, quindi visibile al revisore. Nessun tema perso a 0 su AVS intero sarebbe un errore vero. Sono però pochi casi.

Passaggi assegnati per fonte e tema, tra parentesi quelli da 0,5 in su:

| Tema | AVS 2022, run 1 | AVS 2022, run 2 | M5S 2022 |
| --- | --- | --- | --- |
| `fisco` | 66 (28) | 83 (30) | 15 (14) |
| `lavoro` | 152 (86) | 170 (94) | 26 (21) |
| `imprese` | 125 (43) | 164 (45) | 42 (29) |
| `sanita` | 63 (39) | 68 (42) | 9 (6) |
| `scuola` | 77 (62) | 89 (61) | 11 (10) |
| `famiglia` | 116 (46) | 143 (47) | 21 (9) |
| `immigrazione` | 39 (26) | 39 (26) | 4 (3) |
| `ambiente` | 212 (149) | 224 (146) | 33 (22) |
| `casa` | 76 (33) | 78 (32) | 18 (10) |
| `giustizia` | 112 (70) | 133 (80) | 16 (10) |
| `europa` | 96 (44) | 119 (48) | 9 (7) |
| `istituzioni` | 223 (34) | 247 (51) | 39 (17) |

Nessun tema resta senza passaggi, quindi non c'è nessuna assenza da cercare a mano nel testo estratto e il tempo di quel controllo non è misurato: il confronto con il budget di 10 minuti per scheda resta aperto. Con una precisione tra il 29 e il 38 percento questo risultato è quasi obbligato, e non dimostra che queste fonti non abbiano posizioni assenti false: le bozze non sono state generate.

Cosa questa misura non copre:

- **Documenti brevi.** Sono due fonti su sette, ed entrambe trattano tutti i temi. Una posizione assente falsa richiede di perdere tutti i passaggi di un tema in una fonte, quindi il rischio sta nei temi toccati una volta sola. Sul campione si perde tra il 3,3 e il 5 percento dei temi, ma con 21 casi limite su 120 il valore può essere sovrastimato, e non è una stima per quel caso.
- **Il modello di sintesi.** A soglia 0,1 il classificatore quasi non lascia temi vuoti, quindi è il modello di sintesi a dire `assente`, leggendo molti passaggi fuori tema. Non è misurato.
- **Il peso sulle bozze.** Su AVS intero i temi assegnati sono 2,75 e 3,15 per passaggio, contro 1,61 e 1,64 a soglia 0,2. `istituzioni` riceve 223 e 247 passaggi su 494, di cui 34 e 51 da 0,5 in su.

Raccomandazioni, confermate dal maintainer il 2 novembre 2026 e riportate nei criteri dei ticket citati e nella checklist di [Revisione](#revisione):

1. **Nessun intervento nella pipeline per ora.** Una seconda chiamata mirata sui temi rimasti vuoti, su queste due fonti, non partirebbe mai.
2. **Controllo a mano di ogni posizione assente in revisione (#47):** passaggi assegnati, scartati e ricerca nel testo estratto, cronometrando il tempo.
3. **Guardare per prime le assenze dei documenti brevi,** a partire dall'accordo di centrodestra, su Sanità in #44 e sugli altri temi in #46. Una sola posizione assente falsa riapre la decisione.
4. **Misurare le bozze sui temi con molti passaggi fuori tema in #46,** a partire da `istituzioni`, che #44 non tocca. Se portano a sintesi sbagliate o a un `assente` falso, la soglia 0,1 va rivista. Su AVS intero la soglia 0,2 dà richiamo 90,1% e 88,4%, precisione 50,9% e 50,2%.

## Bozza

Una chiamata per coppia fonte-tema. Input: i passaggi del tema con pagina, definizione e sotto-questioni del tema, esempi dentro/altrove, regole dello schema. Output JSON:

```json
{
  "posizione": "dichiarata",
  "titolo": "...",
  "sintesi": "...",
  "citazioni": [{"pagina": 12, "testo": "..."}]
}
```

oppure `{"posizione": "assente"}` se nessun passaggio tratta il tema. Lo script valida contro lo schema, esegue la verifica delle citazioni e scrive `contenuti/schede/<elezione>/<partito>/<tema>.md` con `stato: bozza` e `bozza_da: {modello, prompt}`. Per una fonte condivisa (accordo di coalizione) la stessa bozza viene scritta per ogni partito che la condivide. Se una citazione non passa, lo script la scarta e ritenta una volta chiedendo la correzione; se fallisce ancora, la scheda resta bozza con il problema in `note`.

Casi limite. Se il classificatore non assegna al tema nessun passaggio, la scheda è assente senza chiamare il modello, senza `bozza_da` e con una nota per il revisore. Se però qualche passaggio non ha il punteggio del tema, l'assenza non è dimostrata: `pipeline bozze` esce con codice 1, elenca quei passaggi e non scrive nulla, lasciando intatta una scheda già esistente. Se invece al tema sono assegnati dei passaggi e altri non hanno il suo punteggio, la bozza si scrive con una nota che li elenca, anche quando il modello risponde assente. Un passaggio senza il punteggio di un altro tema non conta. Se dopo il nuovo tentativo non resta nessuna citazione valida, la posizione resta `dichiarata` senza citazioni e `pipeline verifica` fallisce: la scheda non diventa mai assente per un errore del modello, e un `assente` arrivato al secondo tentativo, dopo una risposta scartata di qualunque tipo, porta una nota. Una scheda già `verificata` o `contestata` non si sovrascrive: se lo sono tutte quelle della fonte, il comando esce con codice 0 senza guardare i punteggi. Una risposta inservibile anche al secondo tentativo non scrive nessun file.

Prompt in `pipeline/prompts/<nome>-v<N>.md`, mai modificati dopo l'uso: una modifica è un nuovo file. `bozza_da.modello` è l'id completo del modello, `bozza_da.prompt` il nome del file. La pagina metodologia pubblica i prompt.

## Verifica delle citazioni

Sottostringa esatta dopo normalizzazione di entrambi i lati: spazi e a capo collassati, virgolette e apostrofi tipografici unificati, trattini di sillabazione a fine riga rimossi, trattini unificati. Maiuscole e accenti restano come sono. Una citazione è un passaggio contiguo: niente `[...]`; due pezzi sono due citazioni. La ricerca avviene nella pagina indicata, con tolleranza di una pagina in più o in meno per gli errori di impaginazione dell'OCR: in quel caso la pagina viene corretta. Il revisore corregge a mano gli errori OCR dentro le citazioni, non nell'intero testo estratto.

## Revisione

Per il 2022, una PR per documento fonte (7 PR, fino a 36 schede per l'accordo di centrodestra). Dal 2027, una PR per tema con tutti i partiti disponibili e le 2 affermazioni del quiz del tema (vedi [playbook-fase-2.md](playbook-fase-2.md)). Per ogni scheda il revisore:

1. apre il PDF alla pagina citata e conferma che la citazione esiste e non è fuori contesto;
2. conferma che la sintesi non aggiunge nulla oltre le citazioni;
3. conferma il tema secondo gli esempi dentro/altrove;
4. se la posizione è assente, controlla con `pipeline passaggi` i passaggi assegnati e quelli scartati, cerca il tema nel testo estratto e segna quanto tempo ci mette;
5. porta `stato` a `verificata`, oppure lascia bozza con una nota.

Non corregge lo stile della sintesi a meno che sia sbagliata. Budget: circa 10 minuti per scheda, 120 schede, circa 20 ore. Il tempo del controllo delle posizioni assenti non è ancora misurato ([#61](https://github.com/simones99/elezio/issues/61)): si misura in #47.

## Fase 2 (programmi 2027)

`pipeline acquisisci --elezione 2027` legge il JSON della sezione Elezioni trasparenti del Ministero, riconosce i partiti in perimetro tramite `alias` del file partito, scarica, calcola hash, archivia, crea il YAML della fonte in bozza e lancia estrazione e OCR. Poi `pipeline classifica` e `pipeline bozze` senza intervento. L'umano conferma i YAML delle fonti e revisiona.

La pubblicazione è incrementale per tema, nell'ordine di `temi.yaml`, tutti i partiti disponibili insieme per ogni tema: una PR per tema con schede e affermazioni del quiz, il merge pubblica il tema. La pipeline gira su ogni programma appena il Ministero lo pubblica; la revisione parte quando sono pubblicati tutti i partiti in perimetro, o a T-32 se prima. Ore: circa 36 tra revisione, affermazioni, acquisizione e lancio, con 15 ore a settimana dichiarate da T-32 a T-15. Calendario, checklist di prontezza, ritardatari e taglio in [playbook-fase-2.md](playbook-fase-2.md).

## Costi

Misurato su M5S 2022 (#37, #58): classificazione di 124 passaggi con `ministral-14b-2512`, prompt v3 e schema a 12 chiavi 0,006 dollari, bozza di Sanità con `mistral-large-4-0` 0,015 dollari, una chiamata. AVS 2022 (#61): classificazione di 494 passaggi 0,025 dollari, con 4 o 5 ripetizioni per i passaggi saltati dal modello.

Stima per il 2022 (7 fonti depositate, circa 250k token di testo): classificazione, una lettura del testo più i prompt, qualche decina di centesimi con un modello Flash e circa un centesimo con JEV; bozze, 84 chiamate con i soli passaggi del tema, pochi dollari con un modello Pro; OCR con Mistral OCR a circa 0,002 dollari a pagina, sotto il dollaro per tutte le scansioni; Tesseract gratis. Ordine di grandezza sotto i 10 dollari per elezione, spesa una tantum. I prezzi effettivi dei modelli Gemini su OpenRouter vanno letti su openrouter.ai/models al momento della run: non sono riportati qui per non invecchiare.

La pipeline registra `usage` di ogni chiamata in `lavoro/log/<run>.jsonl` nel repo privato e si ferma oltre il tetto per run, dove l'endpoint restituisce il costo (vedi [Configurazione](#configurazione)). La pagina metodologia pubblica il costo reale di generazione per elezione.

## Repo privato `elezio-fonti`

```
elezio-fonti/
├── pdf/<fonte>.pdf
├── testo/<fonte>.txt              # testo estratto con marcatori di pagina
├── lavoro/<fonte>/ocr/p<NNN>.md     # uscita dell'OCR, una pagina per file (Markdown di Mistral OCR o testo di Tesseract)
├── lavoro/<fonte>/ocr/motore.txt    # motore che ha prodotto le pagine
├── lavoro/<fonte>/ocr-log.jsonl     # usage e costo di ogni pagina
├── lavoro/<fonte>/passaggi.jsonl    # passaggi segmentati, poi classificati
├── lavoro/<fonte>/bozze/<tema>.json
└── lavoro/log/<run>.jsonl
```

Il repo pubblico tiene solo `contenuti/fonti/<fonte>.yaml` con URL, hash e percorso relativo (`testo_estratto`, `copie_equivalenti`, `ocr`). La CI pubblica clona `elezio-fonti` con un token di sola lettura per `pipeline verifica`.

`pipeline acquisisci` registra in `archivio` la prima copia su Wayback identica al byte al PDF scaricato (confronto del digest SHA-1 dell'API CDX), così l'archivio prova anche che il documento non è cambiato. Una fonte riceve `ocr` quando il PDF non ha testo nativo: più di un quarto delle pagine coperte da un'immagine, oppure meno di 50 parole a pagina. Le pagine OCR già salvate non si rifanno, quindi `pipeline estrai` si può rilanciare senza ripagarle. Per il 2022 le fonti sono 7, di cui 4 da OCR (accordo di centrodestra, PD, AVS, +Europa); la scelta della copia canonica dell'accordo è motivata in testa al suo YAML.
