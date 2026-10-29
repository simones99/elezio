# Pipeline: dal documento fonte alle schede verificate

Ultimo aggiornamento: 27 ottobre 2026. Decisioni di fondo in [ADR 0005](adr/0005-pipeline-da-programma-a-schede.md); termini in [GLOSSARY.md](../GLOSSARY.md); schema dei file in [schema-scheda.md](schema-scheda.md). Questo file è la vista operativa e cambia a ogni run: modelli, prompt, comandi, costi, checklist. Deciso nel ticket [Pipeline da programma a schede verificate](https://github.com/simones99/elezio/issues/9).

## Passi

| # | Passo | Input | Output | Serve un LLM |
| --- | --- | --- | --- | --- |
| 1 | Acquisizione | URL ufficiale | PDF nel repo privato, SHA-256, copia Wayback, YAML fonte in bozza | no |
| 2 | Estrazione testo | PDF | testo estratto con marcatori di pagina (`pdfplumber` o `pypdf`) | no |
| 3 | OCR | PDF scansionato | testo estratto (Tesseract `ita`; ripiego: modello con visione, pagina per pagina come PNG) | solo il ripiego |
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
pipeline acquisisci --url <url> --fonte <id>
pipeline estrai --fonte <id>                 # passi 2-4
pipeline classifica --fonte <id>             # passo 5
pipeline bozze --fonte <id> [--tema <slug>]  # passi 6-7
pipeline verifica                            # passo 9, usato anche in CI
pipeline valuta-classificatore               # precisione e richiamo sul campione d'oro
```

Python standalone in `pipeline/`, indipendente dallo stack del sito. L'umano interviene due volte: conferma il YAML della fonte dopo l'acquisizione (titolo, tipo, partiti condivisi, copia canonica) e revisiona le schede.

## Configurazione

`pipeline.toml` versionato nel repo pubblico; ogni valore è sovrascrivibile dalla variabile d'ambiente indicata. Le chiavi stanno solo nelle variabili d'ambiente.

| Chiave | Variabile | Default |
| --- | --- | --- |
| `base_url` | `ELEZIO_LLM_BASE_URL` | `https://openrouter.ai/api/v1` (alternativa UE stretta: `https://api.mistral.ai/v1`) |
| chiave | `ELEZIO_LLM_API_KEY` | nessuna (passi 5 e 6 disattivati) |
| `modello_sintesi` | `ELEZIO_MODELLO_SINTESI` | `mistralai/mistral-large-4-0` |
| `modello_classificazione` | `ELEZIO_MODELLO_CLASSIFICAZIONE` | `mistralai/ministral-14b-2512` |
| `modello_ocr` | `ELEZIO_MODELLO_OCR` | `mistralai/mistral-medium-3-5` (multimodale) |
| `provider` | `ELEZIO_LLM_PROVIDER` | `mistral` (su OpenRouter: `provider.order=["mistral"]`, `allow_fallbacks=false`) |
| `classificatore` | `ELEZIO_CLASSIFICATORE` | `llm` (alternativa: `jev`) |
| chiave JEV | `ELEZIO_JEV_API_KEY` | nessuna |
| `tetto_dollari_per_run` | `ELEZIO_TETTO_DOLLARI` | `30` |
| `soglia_classificazione` | `ELEZIO_SOGLIA_CLASSIFICAZIONE` | `0.5` |

Client: SDK `openai` con `base_url`, così lo stesso codice gira su OpenRouter, Ollama (`http://localhost:11434/v1`), LM Studio, vLLM. Il backend `jev` usa l'API TypeSafe e vale solo per il passo 5.

Default dei modelli: famiglia Mistral, perché il maintainer vuole l'inferenza in UE. Large 4 per la sintesi, Ministral 3 14B per la classificazione, Medium 3.5 (multimodale) per l'OCR di ripiego. Gli id sono quelli esposti da OpenRouter il 27 ottobre 2026; si fissano definitivamente alla prima run, provando due o tre modelli su un documento. Criterio: sintesi su un modello della fascia Large/Pro con contesto di almeno 32k; classificazione su un modello della fascia Small/Ministral o un 8-14B locale (Ministral 3 è Apache 2.0 e gira anche su Ollama). Mai usare alias come `mistral-large-latest` in `bozza_da`: l'id registrato deve restare risolvibile.

Residenza UE: i modelli Mistral su OpenRouter vanno bloccati sul provider `mistral` (`provider.order` più `allow_fallbacks=false`), altrimenti OpenRouter può instradare su un altro host. Il gateway OpenRouter stesso però processa la richiesta negli USA sul piano gratuito: la base URL regionale `https://eu.openrouter.ai` è solo sui piani Business ed Enterprise. Per una residenza UE stretta si punta `base_url` direttamente a `https://api.mistral.ai/v1` (endpoint compatibile OpenAI, stesso client) con gli id nativi di Mistral, da verificare alla prima run; la stessa API offre OCR 4.1, che può sostituire il ripiego con modello multimodale.

## Passaggi e classificazione

Un passaggio è un paragrafo del testo estratto con la sua pagina, spezzato se supera circa 200 parole. Riceve 0..n temi perché può contenere più proposte: la regola "ogni proposta un solo tema" si applica alla sintesi, non al passaggio. I passaggi classificati vivono nel repo privato in `lavoro/<fonte>/passaggi.jsonl`.

Backend `llm`: 20 passaggi per chiamata, prompt con definizione, sotto-questioni, esempi dentro/altrove di ogni tema, output JSON strutturato. Backend `jev`: stato = un passaggio, 12 domande `Noul` "questo passaggio propone qualcosa su <tema>?", una per tema, con definizione ed esempi nella descrizione; probabilità sotto la soglia scartata.

Campione d'oro: 60 passaggi del programma AVS 2022 depositato etichettati a mano dal maintainer in `pipeline/campione/avs-2022.jsonl` nel repo pubblico (sono citazioni brevi con pagina, entro i limiti decisi nel ticket #4). La copia depositata è una scansione: il testo viene da Mistral OCR, segmentato con `segmenta_markdown`. Sono 48 passaggi stratificati per sezione e 12 casi limite, uno per confine di `temi.yaml` (seme 28); ogni riga dice da quale gruppo viene. Comando: `python -m elezio_pipeline valuta-classificatore --modelli <id>,<id>` da `pipeline/`. `pipeline valuta-classificatore` stampa precisione e richiamo per tema per ogni backend. Il backend con il richiamo migliore diventa il default; sotto il 90 percento di richiamo nessun backend è accettato senza revisione umana della classificazione.

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

Prompt in `pipeline/prompts/<nome>-v<N>.md`, mai modificati dopo l'uso: una modifica è un nuovo file. `bozza_da.modello` è l'id completo del modello, `bozza_da.prompt` il nome del file. La pagina metodologia pubblica i prompt.

## Verifica delle citazioni

Sottostringa esatta dopo normalizzazione di entrambi i lati: spazi e a capo collassati, virgolette e apostrofi tipografici unificati, trattini di sillabazione a fine riga rimossi, trattini unificati. Maiuscole e accenti restano come sono. Una citazione è un passaggio contiguo: niente `[...]`; due pezzi sono due citazioni. La ricerca avviene nella pagina indicata, con tolleranza di una pagina in più o in meno per gli errori di impaginazione dell'OCR: in quel caso la pagina viene corretta. Il revisore corregge a mano gli errori OCR dentro le citazioni, non nell'intero testo estratto.

## Revisione

Una PR per documento fonte (7 PR per il 2022, fino a 36 schede per l'accordo di centrodestra). Per ogni scheda il revisore:

1. apre il PDF alla pagina citata e conferma che la citazione esiste e non è fuori contesto;
2. conferma che la sintesi non aggiunge nulla oltre le citazioni;
3. conferma il tema secondo gli esempi dentro/altrove;
4. porta `stato` a `verificata`, oppure lascia bozza con una nota.

Non corregge lo stile della sintesi a meno che sia sbagliata. Budget: circa 10 minuti per scheda, 120 schede, circa 20 ore.

## Fase 2 (programmi 2027)

`pipeline acquisisci --elezione 2027` legge il JSON della sezione Elezioni trasparenti del Ministero, riconosce i partiti in perimetro tramite `alias` del file partito, scarica, calcola hash, archivia, crea il YAML della fonte in bozza e lancia estrazione e OCR. Poi `pipeline classifica` e `pipeline bozze` senza intervento. L'umano conferma i YAML delle fonti e revisiona.

Le 20 ore di revisione non stanno in 4 settimane a 5 ore: la pubblicazione è incrementale per tema, nell'ordine di `temi.yaml`, tutti i partiti insieme per ogni tema, e il maintainer dichiara 10 ore a settimana nelle 2 settimane dopo la pubblicazione dei programmi. Il quiz si attiva solo quando i temi delle sue affermazioni sono tutti verificati.

## Costi

Stima per il 2022 (7 fonti depositate, circa 250k token di testo): classificazione, una lettura del testo più i prompt, qualche decina di centesimi con un modello Flash e circa un centesimo con JEV; bozze, 84 chiamate con i soli passaggi del tema, pochi dollari con un modello Pro; OCR di ripiego, circa 90 pagine, sotto i 3 dollari; Tesseract gratis. Ordine di grandezza sotto i 10 dollari per elezione, spesa una tantum. I prezzi effettivi dei modelli Gemini su OpenRouter vanno letti su openrouter.ai/models al momento della run: non sono riportati qui per non invecchiare.

La pipeline registra `usage` di ogni chiamata in `lavoro/log/<run>.jsonl` nel repo privato e si ferma oltre il tetto per run. La pagina metodologia pubblica il costo reale di generazione per elezione.

## Repo privato `elezio-fonti`

```
elezio-fonti/
├── pdf/<fonte>.pdf
├── testo/<fonte>.txt              # testo estratto con marcatori di pagina
├── lavoro/<fonte>/passaggi.jsonl
├── lavoro/<fonte>/bozze/<tema>.json
└── lavoro/log/<run>.jsonl
```

Il repo pubblico tiene solo `contenuti/fonti/<fonte>.yaml` con URL, hash e percorso relativo (`testo_estratto`, `copie_equivalenti`, `ocr`). La CI pubblica clona `elezio-fonti` con un token di sola lettura per `pipeline verifica`.
