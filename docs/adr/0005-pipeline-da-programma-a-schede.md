---
status: accepted
date: 2026-10-27
---

# Pipeline da programma a schede: OCR della copia depositata, passaggi classificati, modello sostituibile e opzionale

La pipeline trasforma un documento fonte in schede in stato bozza e ha un solo scopo: far arrivare al revisore bozze che rispettano ADR 0003 senza che il revisore debba rileggere il documento. Sei scelte sono difficili da invertire e stanno qui; il resto (modelli, prompt, comandi, costi, checklist) vive in `docs/pipeline.md` e cambia a ogni run.

**Il testo di riferimento è l'OCR della copia depositata al Ministero.** La pagina citata in una scheda è la pagina della copia ufficiale, quindi il testo estratto si produce da quella copia, con OCR quando è una scansione. Il PDF nativo pubblicato dal partito aiuta a correggere l'OCR e vale come fonte separata di tipo programma esteso, mai come testo di riferimento del depositato. Quando più partiti depositano lo stesso documento con impaginazioni diverse (accordo di centrodestra 2022), una sola copia è canonica e le altre sono registrate solo come prova di deposito.

**Il documento si spezza in passaggi classificati per tema, poi si sintetizza per tema.** Ogni paragrafo del testo estratto diventa un passaggio con numero di pagina; un classificatore assegna a ogni passaggio zero o più temi; una chiamata generativa per coppia fonte-tema produce la bozza sui soli passaggi del tema. Le chiamate restano piccole, il lavoro gira anche su un modello locale, e l'insieme dei passaggi classificati è un dato riusabile (quiz, controllo di copertura).

**Il modello restituisce JSON, la pipeline scrive i file.** Il modello non scrive mai Markdown. Uno script valida il JSON contro lo schema della scheda, esegue la verifica delle citazioni e scrive il file con `stato: bozza` e `bozza_da` compilato. Una citazione che non passa non entra mai nel file: si scarta, il modello riprova una volta e se fallisce ancora la scheda resta bozza con il problema in `note`. Se non resta nessuna citazione valida, la posizione resta `dichiarata` senza citazioni e `pipeline verifica` fallisce, quindi la scheda non può arrivare al sito (ADR 0003). Due casi non scrivono nessun file: una risposta inservibile anche al secondo tentativo, e un tema senza passaggi assegnati quando qualche passaggio non ha il suo punteggio, perché l'assenza non sarebbe dimostrata.

**La verifica delle citazioni è deterministica e indipendente dal modello.** Ogni citazione deve esistere come sottostringa contigua del testo estratto della fonte, dopo una normalizzazione fissa, nella pagina indicata o in quella adiacente. Gira in CI come passo separato prima della build del sito. È questo controllo, non la qualità del modello, che rende accettabile usare modelli piccoli, locali o sconosciuti.

**L'endpoint LLM è configurabile e opzionale.** La pipeline parla con un endpoint compatibile OpenAI (OpenRouter, Ollama, LM Studio, vLLM) scelto in un file di configurazione, con la chiave da variabile d'ambiente. Senza endpoint, acquisizione, estrazione, OCR, verifica e rendering funzionano lo stesso e le schede si scrivono a mano. Unica eccezione ammessa: il classificatore ha un secondo backend facoltativo (JEV di TypeSafe) confinato al passo di classificazione, perché è un modello di sola classificazione con costo trascurabile; nessun altro SDK proprietario entra nella pipeline.

**PDF e testi estratti stanno in un repository privato separato.** Il repository pubblico contiene solo i YAML delle fonti con URL ufficiale, hash e percorso relativo; la CI pubblica clona il repository privato con un token per eseguire la verifica. La questione legale sull'archivio dei testi estratti resta aperta nella mappa e questa scelta non la pregiudica.

## Considered options

- Un prompt per coppia fonte-tema con il documento intero in contesto, senza classificazione: scartato perché richiede contesti da 10k a 140k token per chiamata, impossibili su hardware locale senza GPU, e rilegge ogni documento dodici volte.
- Recupero semantico (RAG, Elysia su Weaviate) per abbassare i costi: scartato perché il recupero top-k perde passaggi e produce posizioni assenti false, aggiunge un vector store da mantenere e il costo da abbattere è già sotto i 10 dollari per elezione.
- Nessun file se la verifica delle citazioni fallisce: scartato perché il revisore non vedrebbe né la bozza né il problema, mentre la bozza con la nota li mostra entrambi e il blocco resta affidato a `pipeline verifica`.
- Citazioni restituite dall'API del provider al posto del verificatore proprio: scartate perché dipendono dal provider, non funzionano sulle scansioni e non sostituiscono comunque il controllo in CI sui file committati.
- SDK e modello di un singolo fornitore fissati nel codice: scartati perché chi lancia la pipeline deve poter scegliere endpoint e modello e perché la pipeline deve funzionare anche senza chiave.
- PDF nativo del partito come testo di riferimento per le scansioni: scartato perché l'impaginazione differisce da quella della copia depositata e la pagina citata non sarebbe verificabile sull'originale.
- Testi estratti nel repository pubblico: scartati perché decidono da soli una questione legale ancora aperta.
- Modello generativo con visione come OCR (Mistral Medium 3.5, pagina per pagina): scartato dopo la misura del ticket #28. Passa quasi tante citazioni quanto Mistral OCR, ma i suoi errori sono riscritture plausibili ("prevedono" diventa "prevedano", "slegata" diventa "sganciata"): la citazione esiste nel testo estratto e non nella pagina, e la verifica deterministica non può accorgersene. Si usa solo un OCR dedicato.
- Strato OCR incorporato nel PDF depositato come testo estratto: scartato, sulle citazioni di AVS 2022 resta 12 punti sotto Tesseract.
- Batch API per dimezzare i costi: scartato perché aggiunge attese fino a 24 ore e in Fase 2 la velocità vale più dei pochi dollari risparmiati.

## Consequences

Chi vuole rigenerare le schede può farlo con un qualunque endpoint compatibile OpenAI o in locale, e il modello usato è pubblico in `bozza_da` e nella pagina metodologia. La classificazione è il punto debole non coperto dal verificatore: un passaggio non classificato diventa una posizione assente falsa, quindi il classificatore di default si sceglie misurando il richiamo su un campione etichettato a mano e non si accetta sotto la soglia fissata in `docs/pipeline.md`. Il repository privato è un secondo repository da mantenere e un token in CI. La revisione resta il collo di bottiglia: 120 schede a 10 minuti sono 20 ore, quindi in Fase 2 si pubblica per tema in modo incrementale e il quiz si attiva solo quando i suoi temi sono tutti verificati.
