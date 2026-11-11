# Piano della Fase 1: analisi del repo e ordine di lavoro

Scritto il 12 novembre 2026 sullo stato di `main` a `1e29168`. È una fotografia: i ticket figli della [mappa](https://github.com/simones99/elezio/issues/1) restano la fonte dello stato, `docs/ROADMAP.md` quella delle scadenze. Dall'analisi sono nati quattro ticket: #65, #66, #67 e #68.

Chi legge: un agente che riprende lo sviluppo. Prima di iniziare leggi `CLAUDE.md`, `docs/ROADMAP.md`, la mappa (issue #1) e `docs/pipeline.md`. Questo file non li ripete: dice dove siamo, cosa non va e in che ordine lavorare.

## 1. Stato verificato oggi

| Cosa | Stato |
| --- | --- |
| Fase 0 (decisioni) | Chiusa il 2 novembre, con circa sette settimane di anticipo sul piano |
| Pipeline Python (`pipeline/`) | Circa 1.700 righe, 111 test superati, `pipeline verifica` verde in locale |
| Fonti 2022 | 7 documenti acquisiti ed estratti in `../elezio-fonti` (131.000 parole) |
| Classificazione | Fatta solo su AVS (494 passaggi) e M5S (124). Mancano cdx, PD, Azione-IV, +Europa, Futuro Nazionale |
| Schede | 1 su 120: `contenuti/schede/2022/m5s/sanita.md`, in stato bozza |
| File dei partiti | Nessuno (`contenuti/partiti/` non esiste) |
| Sito (`sito/`) | Non esiste. C'è solo il prototipo HTML sul branch `prototipo/10-scheda-confronto` |
| CI | PR #64 aperta: test verdi, `verifica delle citazioni` rossa perché manca il secret `ELEZIO_FONTI_TOKEN` |
| Ticket aperti | 22: da #38 a #55, più #65-#68 aperti con questo piano. Sei sono `needs-action` (li può fare solo il maintainer) |

Scadenza: beta online entro il 28 febbraio 2027, con un budget di circa 50 ore per la Fase 1, di cui 20 di revisione umana.

## 2. Punti forti (da non rompere)

1. **La verifica delle citazioni è deterministica e separata dal modello** (`citazioni.py`, 75 righe). È il pezzo che regge tutto il progetto: rende accettabile qualunque modello e dà sostanza alla regola "nessuna posizione senza citazione". È piccola, testata e gira anche senza chiave.
2. **Nessun modello generativo come OCR.** La misura del ticket #28 ha trovato l'unico errore che la verifica non può vedere (riscritture plausibili) e lo ha escluso per regola. È la decisione migliore del repo.
3. **L'assenza non nasce mai da un errore.** `bozze.py` distingue "nessun passaggio" da "punteggio mancante", non sovrascrive le schede già revisionate e non scrive un `assente` dopo una risposta rotta senza una nota. I casi limite sono coperti dai test.
4. **Provenienza seria delle fonti:** hash, copia Wayback identica al byte, copia canonica dell'accordo di centrodestra scelta con una misura e motivata nel YAML.
5. **Codice sobrio.** Funzioni corte, nessuna astrazione inutile, un solo client LLM con tetto di spesa e log, prompt versionati e mai modificati dopo l'uso.
6. **Documentazione onesta.** `docs/pipeline.md` scrive da sola "questa misura va letta con cautela" e dice perché. È raro e vale più dei numeri.
7. **Disciplina di perimetro.** Tre funzioni, lista esplicita del "non in v1", regola "si taglia il contenuto, non la scadenza".

## 3. Critiche

In ordine di gravità. Le prime tre cambiano il piano.

### 3.1 Lo schema non ha il dato che serve alla pagina centrale

La mappa "chi parla di cosa" (#45) mostra sotto-questioni per partiti e apre le citazioni di ogni incrocio (`DESIGN.md`, righe 316-334). Ma una citazione ha solo `id`, `fonte`, `pagina`, `testo` (`docs/schema-scheda.md`), e lo schema JSON della bozza (`bozze.py:18`) non chiede al modello a quale sotto-questione appartiene. Nessun file dice quale citazione sostiene quale sotto-questione.

Se si generano le 120 bozze prima di chiudere questo buco, vanno rigenerate o etichettate a mano. **Va deciso prima di #44.** Proposta: campo facoltativo `sotto_questione` sulla citazione (stringa identica a una voce di `temi.yaml`, assente per la riga "Altro nel tema"), enum per tema nello schema JSON, prompt `bozza-v2.md`, controllo in `schede.py`. La decisione spetta al maintainer in #42.

### 3.2 Il quiz poggia su documenti troppo corti

La regola di ADR 0007 vuole che ogni affermazione abbia la risposta di tutte le sei righe, ognuna con una citazione. Ma l'accordo di centrodestra è lungo 2.949 parole e il programma M5S 2.749: sono elenchi di titoli. Servono 24 affermazioni, 2 per tema, su cui entrambi dicono qualcosa di citabile, e per il `disaccordo` serve una citazione che dica di no, cosa che i programmi fanno di rado.

Il quiz è la metrica di successo (500 completati) ed è il punto più incerto. Finora la verifica di fattibilità era in fondo al piano (#51, dopo 20 ore di revisione). **Va anticipata (#65):** appena esistono le bozze, una matrice sotto-questione per fonte dice in un'ora se le 24 affermazioni esistono. Se non esistono, il piano di riserva va scelto prima di costruire #50. Opinione: riscrivere il calcolo in TypeScript (un centinaio di righe) è più sano che patchare un bundle minificato in versione alpha.

Nota collegata: FdI, Lega e FI sono una riga sola. Il quiz 2022 non può distinguerli e va detto al lettore.

### 3.3 Troppo lavoro sul classificatore, per un filtro che filtra poco

Cinque ticket (#28, #37, #58, #59, #61) sono andati sulla classificazione. Il risultato a soglia 0,1: precisione tra il 29 e il 38 percento, circa 3 temi per passaggio, `istituzioni` che riceve metà del documento AVS, 108 punteggi esattamente sulla soglia, soglia scelta sugli stessi 120 passaggi su cui è misurata, 370 decisioni che cambiano tra due run a temperatura 0. Il richiamo del 95 percento è comprato lasciando passare quasi tutto.

Due conseguenze pratiche:

- **Per i documenti corti la classificazione è inutile e dannosa.** Accordo di centrodestra e M5S stanno interi in una chiamata. Passarli interi al modello di sintesi azzera il rischio di falsa assenza proprio dove è più alto (36 schede dell'accordo). ADR 0005 ha scartato il documento intero per i contesti da 140k token e l'hardware locale: non vale per 3.000 parole. Proposta: sotto una soglia di parole `pipeline bozze` salta il filtro. Tocca un ADR, quindi serve il sì del maintainer.
- **Basta misurare il classificatore.** Il giudizio ora si dà sulle bozze (#44), non su altre run del campione.

### 3.4 Quindici giorni, 67 commit, zero pagine

Circa 3.800 righe di documenti, 1.700 di pipeline, nessun sito. Le decisioni sono buone, ma il rischio vero (un utente legge una scheda da telefono e la capisce) non è ancora stato toccato. La Fase 1 deve invertire il rapporto: prima la fetta verticale online, poi il resto.

### 3.5 La revisione umana è il collo di bottiglia e non è misurata

Venti ore su cinquanta dipendono dall'ipotesi "10 minuti a scheda", mai provata. #38 è pronto dal 2 novembre ed è `needs-action`. Finché non è fatto, il budget della Fase 1 è una stima. Inoltre il revisore oggi lavora su YAML, PDF e terminale: uno strumento di revisione (#66) vale più di qualunque miglioria alla pipeline.

### 3.6 Futuro Nazionale nella beta 2022 costa molto e dice poco

Il documento è del 2026, registrato con `elezione: 2022`, per un partito che nel 2022 non esisteva. Sono 53.925 parole (il 41 percento del corpus, 609 passaggi), 12 schede da revisionare, fuori dal quiz, con una nota di avvertimento ancora da scrivere (#42). È il primo candidato al taglio: beta con 108 schede e Futuro Nazionale dal 2027. Decide il maintainer.

### 3.7 Difetti nel codice

- `llm.py:59` (#68): il costo si legge da `usage.cost`, che esiste solo su OpenRouter. Con `base_url` su `api.mistral.ai` o Ollama il costo resta 0 e il tetto di spesa non scatta mai.
- `llm.py:61` (#68): `json.loads(message.content)` con `content` vuoto (rifiuto, risposta troncata) solleva `TypeError`, che i chiamanti non intercettano: prendono solo `JSONDecodeError`.
- `__main__.py:84` (#67): `pipeline classifica` riscrive `passaggi.jsonl` sul posto. Dato che il risultato cambia a ogni run, una bozza già scritta può non corrispondere più alla classificazione salvata.
- `bozza_da` registra modello e prompt della sintesi, non quelli della classificazione né la soglia (#67). La pagina metodologia promette di pubblicare tutto.
- La scheda di esempio ha un titolo di 20 parole che elenca cinque proposte: il prompt dice "una riga" e nessun controllo lo verifica.
- `pipeline bozze` lavora su una coppia fonte-tema alla volta: per #46 servono 84 lanci a mano (#67).
- Manca `.gitattributes`: con `core.autocrlf=true` su Windows le schede finiscono in CRLF sul disco. Python le legge lo stesso, Astro e i diff no.
- Nessun lockfile Python, nessun linter.
- I vincoli sul singolo file saranno scritti due volte, in zod e in `schede.py`. Va bene, a patto che una sola cartella di schede sbagliate di prova sia usata dai test di entrambi.

## 4. Piano in ordine di priorità

Regola generale: una PR per ticket, `main` è protetto. Ogni decisione che tocca un ADR o lo schema si porta al maintainer con una proposta pronta, non si prende da soli.

### P0. Sbloccare (una sessione)

| # | Cosa | Chi |
| --- | --- | --- |
| 1 | Inserire `ELEZIO_FONTI_TOKEN`, rendere i controlli obbligatori, mergiare la PR #64 | maintainer |
| 2 | #38: revisione cronometrata della scheda M5S Sanità | maintainer |
| 3 | Proposta scritta per #42 con le tre decisioni che bloccano: `sotto_questione` sulla citazione (3.1), documento intero sotto soglia (3.3), Futuro Nazionale fuori dalla beta (3.6) | agente prepara, maintainer decide |
| 4 | #68: i due difetti di `llm.py`, con i test. Nella stessa sessione, PR di igiene: `.gitattributes` con `eol=lf` e lockfile | agente |

### P1. Fetta verticale online (#39, poi #40)

Sito Astro secondo `docs/stack.md` con una sola pagina tema, portando stile e markup dal prototipo. Non aspettare #38: sviluppa su una cartella di contenuti di prova (una scheda verificata finta, una bozza, una assente), che serve comunque a Playwright e al quiz. Aggiungi subito il workflow `sito.yml`. Il collegamento a Cloudflare Pages lo fa il maintainer (#40).

Fatto quando: `elezio.pages.dev` mostra la pagina Sanità da telefono e la CI blocca una build rotta.

### P2. Sanità completa e modello di sintesi (#43, #67, #44)

1. File dei 10 partiti (#43).
2. `bozza-v2.md` con `sotto_questione` (se approvata) e un limite al titolo; controllo del titolo in `schede.py`.
3. #67: `pipeline bozze` accetta più fonti e più temi in un lancio e registra classificatore, prompt e soglia accanto alla bozza. Blocca #46.
4. Classificare le 5 fonti mancanti (pochi centesimi).
5. Scegliere il modello di sintesi su un documento, come chiede #44.
6. Confronto sui due documenti corti: bozza dai passaggi classificati contro bozza dal documento intero. È l'esperimento che chiude 3.3.
7. Controllo a mano delle assenze, partendo da `2022-cdx-accordo`.

### P3. Tutte le bozze e fattibilità del quiz (#46, #65)

Generare gli altri 11 temi, una PR per fonte. Subito dopo, **matrice di fattibilità del quiz (#65)**: per ogni sotto-questione, quali delle sei righe hanno una citazione. Riportala in #51. #65 blocca #50 e #51. Se le affermazioni possibili sono meno di 20, fermati e porta al maintainer la scelta del piano di riserva prima di toccare #50.

### P4. Strumento di revisione, poi le pagine

1. #66: modalità di sviluppo del sito che mostra le bozze con citazioni, note e link al PDF alla pagina giusta. Parte appena esiste il sito (#39). Serve al maintainer per #47: va consegnata prima delle pagine rifinite.
2. Pagina tema completa (#45), confronto (#48), partiti (#49), home (#53).
3. Quiz (#50) e evento GoatCounter (#52), nella forma decisa in P3.
4. Metodologia, crediti, privacy, registro delle correzioni (#54).

### Solo il maintainer, in parallelo

#47 (revisione, 20 ore: partire dall'accordo di centrodestra, che vale 36 schede), #51 (affermazioni), #55 (beta). Se #38 misura più di 10 minuti a scheda, si taglia: prima Futuro Nazionale, poi i temi in fondo a `temi.yaml`.

## 5. Cosa non fare

- Altre misure del classificatore o nuovi prompt di classificazione, salvo che P2 trovi una falsa assenza.
- Il backend `jev`: mai misurato, nessuna chiave, non serve alla beta.
- `pipeline acquisisci --elezione 2027` e tutto il resto della Fase 2 prima della beta.
- Nuove funzioni fuori dal nucleo: vanno nella mappa come fog.
- Modificare un prompt già usato: si crea un file nuovo.
- Portare una scheda a `verificata`: lo fa solo il revisore umano.
- Spendere oltre il tetto di `pipeline.toml`. La spesa attesa per tutte le bozze 2022 è sotto i 10 dollari.

## 6. Convenzioni da rispettare

- Issue, documenti e commit in italiano, prosa normale. Formato dei commit: `<area>: <cosa> (#ticket)`.
- Branch `task/<n>-<slug>`, PR verso `main`, mai push diretto.
- Le decisioni difficili diventano ADR, i termini nuovi vanno in `GLOSSARY.md`.
- PDF e testi estratti restano in `../elezio-fonti`, mai nel repo pubblico.
- Gusto visivo: `DESIGN.md` e `PRODUCT.md`. Nessun colore di partito.
