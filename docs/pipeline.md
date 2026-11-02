# Pipeline: dal documento fonte alle schede verificate

Ultimo aggiornamento: 2 novembre 2026. Decisioni di fondo in [ADR 0005](adr/0005-pipeline-da-programma-a-schede.md); termini in [GLOSSARY.md](../GLOSSARY.md); schema dei file in [schema-scheda.md](schema-scheda.md). Questo file è la vista operativa e cambia a ogni run: modelli, prompt, comandi, costi, checklist. Deciso nel ticket [Pipeline da programma a schede verificate](https://github.com/simones99/elezio/issues/9).

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
| `tetto_dollari_per_run` | `ELEZIO_TETTO_DOLLARI` | `30` |
| `fonti` | `ELEZIO_FONTI` | `../elezio-fonti`, il clone locale del repo privato accanto al repo pubblico |
| `contenuti` | `ELEZIO_CONTENUTI` | `contenuti`, relativo alla radice del repo |
| `soglia_classificazione` | `ELEZIO_SOGLIA_CLASSIFICAZIONE` | `0.2` |

Client: SDK `openai` con `base_url`, così lo stesso codice gira su OpenRouter, Ollama (`http://localhost:11434/v1`), LM Studio, vLLM. Il backend `jev` usa l'API TypeSafe e vale solo per il passo 5.

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

Backend `llm`: 20 passaggi per chiamata, prompt con definizione, sotto-questioni, esempi dentro/altrove di ogni tema, output JSON strutturato con il punteggio di tutti i 12 temi per ogni passaggio. Backend `jev`: stato = un passaggio, 12 domande `Noul` "questo passaggio propone qualcosa su <tema>?", una per tema, con definizione ed esempi nella descrizione; probabilità sotto la soglia scartata.

Campione d'oro: 120 passaggi del programma AVS 2022 depositato etichettati a mano dal maintainer in `pipeline/campione/avs-2022.jsonl` nel repo pubblico (sono citazioni brevi con pagina, entro i limiti decisi nel ticket #4). La copia depositata è una scansione: il testo viene da Mistral OCR, segmentato con `segmenta_markdown`. Due lotti da 60, scelti da `pipeline/campione/seleziona.py`: il primo ha 48 passaggi stratificati per sezione e 12 casi limite, uno per confine di `temi.yaml` (seme 28); il secondo aggiunge un secondo caso limite per i confini che ne hanno un altro (9) e stratificati fino a 120 (seme 29). Ogni riga dice lotto e origine. Le etichette seguono la regola "ogni proposta un solo tema" degli esempi dentro/altrove. Comando: `python -m elezio_pipeline valuta-classificatore --modelli <id>,<id>` da `pipeline/`. `pipeline valuta-classificatore` stampa precisione e richiamo per tema per ogni backend. Il backend con il richiamo migliore diventa il default; sotto il 90 percento di richiamo nessun backend è accettato senza revisione umana della classificazione.

Misura del ticket [#28](https://github.com/simones99/elezio/issues/28) (29-30 ottobre 2026), backend `llm`, 120 passaggi, 121 temi veri, prompt v2, soglia 0,2:

| Modello | Precisione | Richiamo | Costo |
| --- | --- | --- | --- |
| `mistralai/ministral-14b-2512` | 61,9% | **86,0%** | 0,004 $ |
| `mistralai/ministral-8b-2512` | 67,4% | 80,2% | 0,003 $ |
| `mistralai/mistral-small-2603` | 73,7% | 71,9% | 0,005 $ |
| `mistralai/mistral-large-4-0` | 78,2% | 80,2% | 0,110 $ |

Large non fa meglio del 14B sul richiamo, quindi il limite non è la fascia Ministral: sono i confini tra temi (giustizia e ambiente sui reati ambientali, ambiente sul benessere animale) e la soggettività del campione. Con 120 passaggi l'incertezza sul richiamo è di circa ±6 punti. Il backend `jev` non è misurato: manca la chiave.

Misura del ticket [#37](https://github.com/simones99/elezio/issues/37) (2 novembre 2026), stesso campione e stessa soglia, solo sul modello di default:

| Prompt | Punteggi sotto 0,2 | Temi assegnati | Precisione | Richiamo | Temi persi visibili tra gli scartati | Costo |
| --- | --- | --- | --- | --- | --- | --- |
| `classificazione-v2.md` | non richiesti | 168 | 61,9% | 86,0% | n.d. | 0,004 $ |
| `classificazione-v3.md` | 1126 su 1440 | 314 | 36,9% | **95,9%** | 5 su 5 | 0,009 $ |

Default `ministral-14b-2512` con `classificazione-v3.md`. Il richiamo passa il 90 percento, ma con l'incertezza del campione il margine è minimo, e gli altri modelli non sono rimisurati con questo prompt. Il prezzo è la precisione: il tema riceve circa il doppio dei passaggi, quindi la bozza può contenere più materiale fuori tema, da fermare in revisione.

La v3 chiede tutti i 12 temi per ogni passaggio perché un invito a elencare in più i temi improbabili non basta: due formulazioni di questo tipo, scartate prima dell'uso, hanno dato 1 e 8 voci sotto 0,2 e nessun tema perso visibile, con richiamo 86,8% e 85,1%.

Per la revisione della classificazione `pipeline passaggi` mostra i passaggi assegnati al tema, quelli scartati con punteggio sopra 0 e sotto la soglia, dal più alto, e quelli senza temi. Sul campione gli scartati sono in media 59 per tema, perché il modello dà spesso 0,05. Da 0,1 in su sono in media 6, ma contengono solo 2 dei 5 temi persi: i primi della lista sono i più probabili, non gli unici da controllare. Un passaggio con soli punteggi bassi compare sia tra gli scartati sia tra quelli senza temi.

Limite noto: lo schema JSON non può obbligare il modello a elencare tutti i 12 temi. Sul campione d'oro ha risposto per tutti i passaggi; su M5S 2022 una chiamata su 7 (passaggi 0101-0120) ha ignorato la regola e si comporta come la v2, quindi quei passaggi non mostrano perdite. La pipeline per ora non lo rileva.

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

Tre casi limite. Se il classificatore non assegna al tema nessun passaggio, la scheda è assente senza chiamare il modello, senza `bozza_da` e con una nota per il revisore. Se dopo il nuovo tentativo non resta nessuna citazione valida, la posizione resta `dichiarata` senza citazioni e `pipeline verifica` fallisce: la scheda non diventa mai assente per un errore del modello, e un `assente` arrivato al secondo tentativo, dopo una risposta scartata di qualunque tipo, porta una nota. Una scheda già `verificata` o `contestata` non si sovrascrive; una risposta inservibile anche al secondo tentativo non scrive nessun file.

Prompt in `pipeline/prompts/<nome>-v<N>.md`, mai modificati dopo l'uso: una modifica è un nuovo file. `bozza_da.modello` è l'id completo del modello, `bozza_da.prompt` il nome del file. La pagina metodologia pubblica i prompt.

## Verifica delle citazioni

Sottostringa esatta dopo normalizzazione di entrambi i lati: spazi e a capo collassati, virgolette e apostrofi tipografici unificati, trattini di sillabazione a fine riga rimossi, trattini unificati. Maiuscole e accenti restano come sono. Una citazione è un passaggio contiguo: niente `[...]`; due pezzi sono due citazioni. La ricerca avviene nella pagina indicata, con tolleranza di una pagina in più o in meno per gli errori di impaginazione dell'OCR: in quel caso la pagina viene corretta. Il revisore corregge a mano gli errori OCR dentro le citazioni, non nell'intero testo estratto.

## Revisione

Per il 2022, una PR per documento fonte (7 PR, fino a 36 schede per l'accordo di centrodestra). Dal 2027, una PR per tema con tutti i partiti disponibili e le 2 affermazioni del quiz del tema (vedi [playbook-fase-2.md](playbook-fase-2.md)). Per ogni scheda il revisore:

1. apre il PDF alla pagina citata e conferma che la citazione esiste e non è fuori contesto;
2. conferma che la sintesi non aggiunge nulla oltre le citazioni;
3. conferma il tema secondo gli esempi dentro/altrove;
4. porta `stato` a `verificata`, oppure lascia bozza con una nota.

Non corregge lo stile della sintesi a meno che sia sbagliata. Budget: circa 10 minuti per scheda, 120 schede, circa 20 ore.

## Fase 2 (programmi 2027)

`pipeline acquisisci --elezione 2027` legge il JSON della sezione Elezioni trasparenti del Ministero, riconosce i partiti in perimetro tramite `alias` del file partito, scarica, calcola hash, archivia, crea il YAML della fonte in bozza e lancia estrazione e OCR. Poi `pipeline classifica` e `pipeline bozze` senza intervento. L'umano conferma i YAML delle fonti e revisiona.

La pubblicazione è incrementale per tema, nell'ordine di `temi.yaml`, tutti i partiti disponibili insieme per ogni tema: una PR per tema con schede e affermazioni del quiz, il merge pubblica il tema. La pipeline gira su ogni programma appena il Ministero lo pubblica; la revisione parte quando sono pubblicati tutti i partiti in perimetro, o a T-32 se prima. Ore: circa 36 tra revisione, affermazioni, acquisizione e lancio, con 15 ore a settimana dichiarate da T-32 a T-15. Calendario, checklist di prontezza, ritardatari e taglio in [playbook-fase-2.md](playbook-fase-2.md).

## Costi

Misurato su M5S 2022 (#37): classificazione di 124 passaggi con `ministral-14b-2512` e prompt v3 0,008 dollari, bozza di Sanità con `mistral-large-4-0` 0,015 dollari, una chiamata.

Stima per il 2022 (7 fonti depositate, circa 250k token di testo): classificazione, una lettura del testo più i prompt, qualche decina di centesimi con un modello Flash e circa un centesimo con JEV; bozze, 84 chiamate con i soli passaggi del tema, pochi dollari con un modello Pro; OCR con Mistral OCR a circa 0,002 dollari a pagina, sotto il dollaro per tutte le scansioni; Tesseract gratis. Ordine di grandezza sotto i 10 dollari per elezione, spesa una tantum. I prezzi effettivi dei modelli Gemini su OpenRouter vanno letti su openrouter.ai/models al momento della run: non sono riportati qui per non invecchiare.

La pipeline registra `usage` di ogni chiamata in `lavoro/log/<run>.jsonl` nel repo privato e si ferma oltre il tetto per run. La pagina metodologia pubblica il costo reale di generazione per elezione.

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
