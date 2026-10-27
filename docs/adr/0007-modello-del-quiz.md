---
status: accepted
date: 2026-10-27
---

# Modello del quiz: ogni partito risponde con una citazione, Open Election Compass senza modifiche

Il quiz usa Open Election Compass (ADR 0006), che dà a ogni partito una risposta per affermazione (`approve`, `neutral`, `reject`, `skip`) e calcola l'affinità con la matrice cityblock 2/1/0. Il sorgente della 2.0.0-alpha.5 ha due proprietà che decidono il modello. La prima: il punteggio massimo dipende solo dalle affermazioni a cui ha risposto chi fa il quiz, quindi un partito senza risposta su un'affermazione prende 0 punti come se fosse in disaccordo pieno, e nessuna opzione di configurazione lo cambia. La seconda: accetta solo algoritmi con nome, senza matrici personalizzate. Allo stesso tempo ADR 0003 vieta di attribuire a un partito qualcosa che il suo documento fonte non dice.

**Ogni risposta del partito è accordo o disaccordo, sostenuta da una citazione della sua scheda.** La risposta punta a una citazione già presente nella scheda dello stesso partito sullo stesso tema; se manca, la si aggiunge alla scheda. Non esiste una risposta neutra del partito: se la posizione non è netta, l'affermazione va riscritta o scartata. Il neutro resta solo per chi fa il quiz.

**Un'affermazione entra nel quiz solo se tutti i partiti del quiz hanno una risposta.** È questa regola di selezione, e non una modifica al bundle, a evitare che un partito silenzioso venga contato come contrario. Il costo è che le affermazioni si concentrano sulle questioni che tutti i documenti toccano.

**Il quiz è per elezione di riferimento.** Ci sono 24 affermazioni, due per tema su sotto-questioni diverse, in ordine fisso con i temi alternati. Nel quiz di un'elezione entrano solo i partiti con un programma, un programma esteso o un accordo di coalizione per quella elezione: per questo Futuro Nazionale non è nel quiz 2022 ed entra nel 2027. Partiti con risposte identiche su tutte le affermazioni, perché citano lo stesso documento fonte, compaiono come un solo raggruppamento: nel 2022 Fratelli d'Italia, Lega e Forza Italia, e Azione e Italia Viva. Il quiz 2022 ha quindi 6 righe. Quando esce il quiz di una nuova elezione, il precedente si toglie dal sito.

**Open Election Compass si usa così com'è.** Tre risposte più "salta", cityblock 2/1/0, "importante" con peso doppio fino a metà delle affermazioni, salto fino a un quarto. La spiegazione del risultato, in linguaggio semplice, entra con le stringhe sovrascritte.

## Considered options

- Risposta del partito decisa dal revisore leggendo la scheda, senza citazione propria: scartata perché è inferenza.
- Citazione propria della risposta, separata dalla scheda: scartata perché raddoppia le citazioni da verificare.
- Partito senza posizione mappato su "neutro": scartato perché è inferenza.
- Patch del bundle minificato per togliere dal massimo del partito le affermazioni a cui non risponde: scartata per ora perché è codice GPL compilato con una toolchain fragile. Resta il piano di riserva se i dati 2022 non danno almeno 20 affermazioni valide.
- Accettare la penalità e dichiararla: scartato perché fuorviante per chi fa il quiz.
- Scala a cinque risposte (algoritmo hybrid): scartata perché "parzialmente d'accordo" per un partito è un giudizio, non una citazione.
- Risposta neutra del partito per posizioni condizionate: scartata per lo stesso motivo.
- Fratelli d'Italia, Lega e Forza Italia come tre righe separate: scartato perché tre pari merito identici sembrano un errore.
- Risposte nel frontmatter delle schede: scartato perché ogni affermazione aggiunta riporterebbe in bozza dieci schede già verificate e spargerebbe un'affermazione su dieci file.

## Consequences

Le affermazioni sono file propri con un loro stato di verifica; le citazioni restano nelle schede, che acquistano un identificatore stabile per le citazioni usate dal quiz. Le affermazioni le scrive a mano il maintainer, senza LLM, in circa 6-8 ore per elezione. Il quiz si pubblica solo con almeno 20 affermazioni verificate. La fine del quiz si intercetta leggendo lo store interno di Open Election Compass, protetto da un test Playwright. Formato dei file, controlli, mappatura sul JSON di Open Election Compass e aggancio dell'analytics in `docs/quiz.md`.
