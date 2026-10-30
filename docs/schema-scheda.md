# Schema dati: schede, partiti, documenti fonte, temi

Ultimo aggiornamento: 27 ottobre 2026 (temi, campi della fonte per la pipeline, `id` delle citazioni e `sigla` dei partiti per il quiz). Decisioni di fondo in [ADR 0004](adr/0004-schema-dati-della-scheda.md); termini in [GLOSSARY.md](../GLOSSARY.md). Questo file è la vista campo per campo e cambia più spesso dell'ADR.

## Layout dei file

```
contenuti/
├── temi.yaml                         # i 12 temi, ordine di presentazione
├── partiti/<partito>.yaml            # un file per partito
├── fonti/<fonte>.yaml                # un file per documento fonte
└── schede/<elezione>/<partito>/<tema>.md   # una scheda per file
```

Esempio: `contenuti/schede/2022/pd/sanita.md`. Gli identificatori nei percorsi sono gli slug stabili definiti nei file dei partiti, delle fonti e dei temi. Niente accenti né spazi negli slug.

## Scheda (`schede/<elezione>/<partito>/<tema>.md`)

Markdown con frontmatter YAML. Il frontmatter porta i campi strutturati, il corpo è la sintesi.

| Campo | Obbligatorio | Tipo | Note |
| --- | --- | --- | --- |
| `partito` | sì | slug | Deve coincidere con la cartella. |
| `tema` | sì | slug | Deve coincidere con il nome del file. |
| `elezione` | sì | intero (2022, 2027) | Deve coincidere con la cartella. |
| `posizione` | sì | `dichiarata` \| `assente` | Nessun altro valore. |
| `titolo` | se dichiarata | stringa, una riga | Cosa propone il partito, in parole semplici. Vuoto se assente. |
| `citazioni` | se dichiarata, almeno 1 | lista | Vedi sotto. Vuota se assente. Totale parole di tutte le citazioni: massimo 300. |
| `stato` | sì | `bozza` \| `verificata` \| `contestata` | Si pubblicano solo `verificata` e `contestata` (con avviso). |
| `verificata_il` | se stato ≠ bozza | data ISO | Data dell'ultima verifica del revisore. |
| `revisore` | se stato ≠ bozza | stringa | Handle GitHub del revisore. |
| `aggiornata_il` | sì | data ISO | Ultima modifica al contenuto. |
| `bozza_da` | no | oggetto `{modello, prompt}` | Modello LLM e versione del prompt che ha generato la bozza. Pubblicato nella pagina metodologia. Assente se scritta a mano. |
| `note` | no | stringa | Note interne del revisore. Non pubblicate. |

Corpo del file: la sintesi, da 2 a 5 frasi in prosa semplice. Se la posizione è assente, il corpo dice che il documento fonte del partito non tratta il tema; il sito mostra lo stesso testo per tutte le schede assenti.

### Citazione

| Campo | Obbligatorio | Note |
| --- | --- | --- |
| `id` | se citata dal quiz | Slug stabile, unico nella scheda. Le risposte del partito nel quiz puntano a questo `id` (vedi `docs/quiz.md`). |
| `fonte` | sì | Slug di un documento fonte che elenca questo partito tra i `partiti` e ha la stessa `elezione` della scheda. |
| `pagina` | sì | Numero di pagina del PDF ufficiale (intero, oppure intervallo `12-13`). |
| `testo` | sì | Testo alla lettera dal documento. La pipeline verifica che esista nel testo estratto della fonte. |

Regola sulle fonti multiple: se il partito ha un programma depositato che copre il tema, si cita quello. Il programma esteso si cita solo per i temi che il depositato non copre.

### Campi derivati in build, mai scritti nei file

- **Livello della posizione**: `coalizione` se la fonte citata elenca più di un partito, altrimenti `partito`. Il sito lo mostra al lettore.
- **Tipo di documento della posizione**: il `tipo` della fonte citata (programma, programma esteso, accordo di coalizione, documento programmatico). Il sito lo mostra al lettore.
- **Superata**: vera se esiste una scheda dello stesso partito e tema per una elezione successiva. Il sito la mostra con il link alla scheda più recente.

## Partito (`partiti/<partito>.yaml`)

| Campo | Obbligatorio | Note |
| --- | --- | --- |
| `id` | sì | Slug stabile, mai cambiato dopo la creazione (es. `fdi`, `pd`, `m5s`, `lega`, `fi`, `avs`, `azione`, `iv`, `piu-europa`, `futuro-nazionale`). |
| `nome` | sì | Nome corrente. |
| `sigla` | sì | Sigla corrente (es. FdI, PD, M5S), usata nel quiz e nei confronti. |
| `nomi_precedenti` | no | Lista di `{nome, fino_al}`. |
| `alias` | no | Lista di nomi alternativi e sigle usati per riconoscere il partito nei documenti. |
| `logo` | sì | Percorso del contrassegno preso dalla sezione Elezioni trasparenti del Ministero. Non coperto dalla licenza dei dati. |
| `sito` | sì | URL ufficiale. |
| `inclusione` | sì | Oggetto `{via, verificata_il, fonte}`. `via` è `percentuale` (più del 2 percento alle ultime politiche) oppure `parlamentari` (almeno 5 in carica che dichiarano l'appartenenza). `fonte` è l'URL della pagina usata per la verifica (risultati ufficiali o elenco di Camera e Senato). |

## Documento fonte (`fonti/<fonte>.yaml`)

| Campo | Obbligatorio | Note |
| --- | --- | --- |
| `id` | sì | Slug, es. `2022-pd-programma`, `2022-cdx-accordo`, `2026-futuro-nazionale-programmatico`. |
| `titolo` | sì | Titolo del documento come appare sul frontespizio. |
| `tipo` | sì | `programma` \| `programma_esteso` \| `accordo_coalizione` \| `documento_programmatico`. |
| `elezione` | sì | Elezione di riferimento. Per un documento programmatico è l'elezione per cui lo si usa (es. 2022 per Futuro Nazionale nella beta). |
| `partiti` | sì | Lista di slug dei partiti che condividono il documento. Un solo elemento per un programma di partito, tre per l'accordo di centrodestra 2022. |
| `url` | sì | URL della copia ufficiale (Ministero per i depositati, sito del partito per gli estesi). Il PDF non viene ridistribuito. |
| `hash` | sì | SHA-256 del PDF al momento dell'acquisizione. |
| `acquisito_il` | sì | Data dell'acquisizione. |
| `archivio` | no | URL della copia su Wayback Machine o archivio equivalente. |
| `pagine` | sì | Numero di pagine del PDF. |
| `testo_estratto` | sì | Percorso del testo estratto (OCR se la copia depositata è una scansione), usato dalla pipeline per verificare le citazioni. Non pubblicato. |
| `data_documento` | no | Data riportata sul documento, se presente. |
| `copie_equivalenti` | no | Lista di `{url, hash, partito}` per le altre copie depositate dello stesso documento (es. le copie Lega e FI dell'accordo di centrodestra 2022). Prova di deposito; la numerazione di pagina valida è solo quella della copia canonica in `url`. |
| `ocr` | se scansione | `mistral-ocr` \| `tesseract`. Come è stato prodotto il testo estratto quando la copia canonica è una scansione. Conta come scansione anche un PDF con uno strato OCR incorporato: lo strato non si usa come testo estratto. Nessun OCR con modello generativo (ADR 0005). |
| `ocr_versione` | no | Versione del motore OCR, quando è nota: per Tesseract versione e lingua (es. `tesseract 5.3.0 ita`), per Mistral OCR l'id del modello se l'API lo restituisce. |

## Tema (`temi.yaml`)

Lista ordinata di 12 oggetti `{id, nome, definizione, sotto_questioni, dentro, altrove}`. L'ordine nel file è l'ordine di presentazione sul sito. `sotto_questioni` è la lista fissa (3-6 voci) che guida sintesi, titolo e quiz; `dentro` e `altrove` sono esempi di proposte che rientrano nel tema e di proposte simili che stanno in un altro tema, usati come precedenti per la regola "decide lo strumento che cambia". Nomi, definizioni e confini sono decisi dal ticket [I 12 temi di v1](https://github.com/simones99/elezio/issues/5); il file è [`contenuti/temi.yaml`](../contenuti/temi.yaml).

## Vincoli verificati in build

- Per ogni partito, tema ed elezione esiste al massimo una scheda; la beta 2022 ne ha esattamente 120 (10 partiti per 12 temi).
- Ogni scheda `dichiarata` ha almeno una citazione; ogni scheda `assente` ne ha zero e non ha titolo.
- Ogni citazione punta a una fonte che include il partito della scheda e ha la stessa elezione.
- Ogni testo di citazione esiste nel testo estratto della fonte indicata.
- Le citazioni di una scheda non superano le 300 parole in totale.
- Ogni partito in `partiti/` ha `inclusione` compilata; non si pubblicano schede di partiti senza inclusione.
- Non si pubblicano schede in stato `bozza`.
