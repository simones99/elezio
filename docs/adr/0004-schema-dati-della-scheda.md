---
status: accepted
date: 2026-10-27
---

# Schema dati della scheda: fonte come entità, due tipi di posizione, tre stati, criterio di inclusione

Una scheda è identificata da partito, tema ed elezione di riferimento: la scheda 2027 non sovrascrive la 2022 ma la affianca, e il lettore vede sempre a quale elezione si riferisce. Il documento fonte è un'entità propria, non un campo della scheda, perché nel 2022 Fratelli d'Italia, Lega e Forza Italia hanno depositato lo stesso accordo di coalizione e perché i PDF non si possono ridistribuire: la fonte registra URL ufficiale, hash, data e i partiti che la condividono, e la scheda cita per identificatore di fonte più pagina. Quando una fonte è condivisa da più partiti la posizione è di coalizione, e lo si deriva dalla fonte invece di dichiararlo a mano. La posizione ha due soli tipi, dichiarata o assente: il tipo "inferita" è stato eliminato perché ADR 0003 vieta l'inferenza, e il caso di Futuro Nazionale (nessun programma 2022, un documento programmatico del 2026) è una posizione dichiarata da un documento fonte di tipo diverso, che il lettore vede come tale. Gli stati di verifica sono bozza, verificata e contestata; "superata" non è uno stato ma deriva dall'esistenza della scheda dell'elezione successiva. Il criterio di inclusione dei partiti è: più del 2 percento alle ultime elezioni politiche, oppure almeno 5 parlamentari in carica che dichiarano l'appartenenza al momento del rilascio; copre Futuro Nazionale senza eccezioni ad hoc e non usa i sondaggi. Lo schema campo per campo vive in `docs/schema-scheda.md`.

## Considered options

- Fonte come campo della scheda (URL e pagina inline): scartata perché l'accordo di coalizione andrebbe duplicato in 36 schede e l'hash andrebbe ripetuto o omesso.
- Tipo di posizione "inferita da altri documenti": scartato perché contraddice ADR 0003 e perché il caso che doveva coprire è una citazione da un documento fonte, non un'inferenza.
- Quattro stati con "superata" esplicita: scartati perché lo stato sarebbe ridondante con l'elezione di riferimento e andrebbe mantenuto a mano al rilascio delle schede 2027.
- Criterio originale (gruppo parlamentare autonomo o più del 2 percento nel 2022) con eccezione dichiarata per Futuro Nazionale: scartato perché un'eccezione nominativa indebolisce la metodologia pubblica. Il criterio con soglia di 5 parlamentari in carica è verificabile sui siti di Camera e Senato.
- Soglia sui sondaggi per i partiti nuovi: scartata perché richiede di scegliere istituti e medie, e non è verificabile in modo stabile.
- Quando un partito ha più versioni dello stesso programma (M5S depositato breve, PD depositato precedente all'aggiornamento), la copia depositata al Ministero è la fonte primaria; la versione estesa pubblicata dal partito è ammessa come seconda fonte dello stesso partito solo per i temi che la copia depositata non copre, e ogni citazione dice da quale fonte proviene. Alternativa scartata: usare solo la copia nativa, più completa ma non ufficiale e soggetta a sparire dal sito del partito.

## Consequences

Il campo "proposta originale" esce dal glossario: la scheda ha un titolo di una riga, una sintesi e una lista di citazioni. Il livello della posizione (partito o coalizione) e lo stato "superata" sono calcolati in build, non scritti nei file. La pipeline (ticket dedicato) deve validare che ogni citazione esista nel testo della fonte indicata e che le citazioni di una scheda non superino le 300 parole in totale. Il file dei partiti registra per ciascuno la via di inclusione e la data della verifica, e la pagina metodologia li pubblica.
