---
name: elezio
description: I programmi elettorali per tema, con la citazione alla lettera e la pagina del documento ufficiale.
colors:
  inchiostro: "#271002"
  inchiostro-2: "#5C4636"
  carta: "#FAF8F1"
  pietra-2: "#ECE7DF"
  linea: "rgba(39,16,2,.18)"
  velo: "rgba(39,16,2,.42)"
typography:
  display:
    fontFamily: "Cinzel, serif"
    fontSize: "clamp(50px, 13vw, 104px)"
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "0.01em"
  headline:
    fontFamily: "Cinzel, serif"
    fontSize: "19px"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "0.02em"
  marchio:
    fontFamily: "Cinzel, serif"
    fontSize: "19px"
    fontWeight: 600
    letterSpacing: "0.14em"
  title:
    fontFamily: "Archivo, sans-serif"
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.22
    fontVariation: "'wdth' 112"
  body:
    fontFamily: "Archivo, sans-serif"
    fontSize: "16.5px"
    fontWeight: 400
    lineHeight: 1.55
    fontVariation: "'wdth' 108"
    fontFeature: "'tnum'"
  body-lead:
    fontFamily: "Archivo, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
    fontVariation: "'wdth' 108"
  quote:
    fontFamily: "Archivo, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
    fontVariation: "'wdth' 108"
  sigla:
    fontFamily: "Archivo, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    letterSpacing: "0.03em"
    fontVariation: "'wdth' 118"
  label:
    fontFamily: "Archivo, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    letterSpacing: "0.06em"
    fontVariation: "'wdth' 118"
  meta:
    fontFamily: "Archivo, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
    letterSpacing: "0.04em"
    fontVariation: "'wdth' 118"
  nota:
    fontFamily: "Archivo, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
    fontVariation: "'wdth' 108"
rounded:
  none: "0px"
  full: "50%"
spacing:
  xs: "4px"
  sm: "10px"
  md: "16px"
  gutter: "20px"
  lg: "28px"
  xl: "34px"
  xxl: "44px"
components:
  tondo:
    backgroundColor: "{colors.inchiostro}"
    textColor: "{colors.carta}"
    rounded: "{rounded.full}"
    size: "52px"
  tondo-pop:
    backgroundColor: "{colors.inchiostro}"
    textColor: "{colors.carta}"
    rounded: "{rounded.full}"
    size: "44px"
  link-caps:
    textColor: "{colors.inchiostro}"
    typography: "{typography.label}"
  citazione:
    backgroundColor: "{colors.pietra-2}"
    textColor: "{colors.inchiostro}"
    typography: "{typography.quote}"
    rounded: "{rounded.none}"
    padding: "16px 18px"
  contrassegno:
    rounded: "{rounded.full}"
    size: "40px"
  contrassegno-mappa:
    rounded: "{rounded.full}"
    size: "30px"
  mappa-punto:
    textColor: "{colors.inchiostro}"
    rounded: "{rounded.full}"
    size: "44px"
  mappa-punto-hover:
    backgroundColor: "{colors.pietra-2}"
  scheda:
    backgroundColor: "{colors.carta}"
    textColor: "{colors.inchiostro}"
    padding: "32px 0 34px"
  pop-up:
    backgroundColor: "{colors.carta}"
    textColor: "{colors.inchiostro}"
    rounded: "{rounded.none}"
    width: "min(560px, 100vw)"
  scelta-partito:
    textColor: "{colors.inchiostro-2}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "7px 12px"
  scelta-partito-on:
    backgroundColor: "{colors.inchiostro}"
    textColor: "{colors.carta}"
---

# Design System: elezio

## Overview

**Creative North Star: "L'etichetta civica"**

La pagina di un'etichetta italiana di pregio applicata al dovere civico: capitali romane da iscrizione per i titoli, grottesco largo per il testo e l'interfaccia, inchiostro bruno su carta calda, tantissima aria. Il sistema è costruito per un elettore che legge da telefono in momenti brevi: una riga dice cosa propone un partito, un tocco mostra le parole esatte del programma e la pagina da cui vengono. L'unica immagine ammessa è il contrassegno ufficiale del partito, piccolo e inalterato; tutto il resto è tipografia, filetti e due toni di carta.

La gerarchia è piatta per principio: ogni partito riceve la stessa sequenza di elementi, lo stesso spazio e lo stesso peso, in ordine alfabetico. Un'assenza ("il programma non tratta il tema") occupa lo stesso posto e la stessa gerarchia di una posizione dichiarata. Lo stato di una posizione si legge da segni grafici (punto pieno, cerchio vuoto, cerchio tratteggiato, trattino), mai da un colore.

Rifiuti confermati: la griglia di card con accento blu dei siti civici, il grigio da modulistica della pubblica amministrazione, qualunque colore di partito nell'interfaccia, le fotografie.

**Key Characteristics:**
- Monocromia calda: un solo inchiostro bruno su carta crema, con un secondo tono di carta per le citazioni.
- Capitali lapidarie (Cinzel) solo per titolo del tema, titolo del pop-up e marchio; tutto il resto in Archivo esteso.
- Superfici piatte, angoli vivi; il tondo è riservato a contrassegni, punti della mappa e bottoni d'azione.
- Etichette e link in maiuscoletto largo e spaziato; i link sono sottolineati.
- Ogni citazione porta documento e pagina, con la pagina come link al PDF ufficiale.
- Il contenuto è HTML statico; la mappa interattiva è un arricchimento.

## Colors

Una monocromia bruna su carta calda: un inchiostro, la sua versione attenuata, due carte e un filetto trasparente.

### Primary
- **Inchiostro bruno** (inchiostro): testo principale, titoli, filetto forte sopra la mappa e sopra il confronto, fondo dei bottoni tondi, chip del partito selezionato, contorno di focus, selezione del testo (invertita su carta). È l'unico colore attivo del sistema.

### Neutral
- **Carta crema** (carta): fondo della pagina e del pop-up. Valore fissato dall'utente, misurato sul riferimento moncalisse.com; registrato come eccezione approvata in `.impeccable/config.json` (regola `cream-palette`). Non va "corretto" verso il bianco.
- **Inchiostro attenuato** (inchiostro-2): testo secondario: nota sotto il titolo, nomi estesi dei partiti, metadati della scheda, fonte della citazione, legenda, frasi di assenza, intestazione "Questione".
- **Pietra chiara** (pietra-2): fondo del riquadro di citazione e alone del punto della mappa al passaggio del puntatore. Il contratto di direzione indicava una pietra più scura (#DED8CF) per i riquadri; la build scelta usa questa più chiara per citazioni e stati, e la pietra scura non compare nella variante D.
- **Filetto** (linea): divisori tra schede, righe della mappa, testata, testa del pop-up, bordi delle chip non selezionate.
- **Velo** (velo): fondo dietro il pop-up aperto, lo stesso inchiostro al 42%.

### Named Rules
**The Neutralità Rule.** Nessun colore di partito, mai: né negli accenti, né nei punti della mappa, né nelle chip, né negli stati. Il colore appare solo dentro il contrassegno ufficiale, che è un'immagine del partito e non dell'interfaccia.

**The Un Inchiostro Rule.** L'interfaccia ha un solo colore attivo, l'inchiostro bruno. Uno stato, una selezione o un'enfasi si esprimono con peso, forma, riempimento o inversione inchiostro su carta, non con una nuova tinta.

## Typography

**Display Font:** Cinzel (con serif), variabile 400-900, self-hosted
**Body Font:** Archivo (con sans-serif), variabile 100-900, larghezza 62-125%, self-hosted

**Character:** Capitali romane da iscrizione contro un grottesco allargato: la lapide dà il nome alle cose, il grottesco le spiega. Archivo non si usa mai alla larghezza normale: il testo corrente sta a 108%, titoli di scheda a 112%, etichette, sigle e metadati a 118%.

### Hierarchy
- **Display** (Cinzel 500, clamp(50px, 13vw, 104px), interlinea 0.95, maiuscolo): solo il nome del tema in testa alla pagina, allineato a sinistra.
- **Headline** (Cinzel 500, 19px, interlinea 1.15, maiuscolo, spaziatura 0.02em): titolo della sotto-questione nel pop-up.
- **Marchio** (Cinzel 600, 19px, spaziatura 0.14em): il nome "Elezio" nella testata.
- **Title** (Archivo 700, 21px, interlinea 1.22, larghezza 112%, `text-wrap: balance`): titolo della scheda, la riga che dice cosa propone il partito. Nel confronto a due colonne scende a 17.5px. Per una posizione assente il peso scende a 500, stessa dimensione e stesso posto.
- **Body** (Archivo 400, 16.5px, interlinea 1.55, larghezza 108%, cifre tabellari): sintesi, massimo 62ch. La definizione del tema sotto il titolo sale a 17px, massimo 52ch.
- **Quote** (Archivo 400, 16px, interlinea 1.55): testo della citazione nel riquadro; 14.5px dentro la riga aperta della mappa.
- **Sigla** (Archivo 700, 15px, larghezza 118%, spaziatura 0.03em): sigla del partito accanto al contrassegno; 12px nella testa della mappa.
- **Label** (Archivo 600, 13px, larghezza 118%, spaziatura 0.06em, MAIUSCOLO): link e azioni testuali ("Leggi nel programma · 4 citazioni", "Vai alla scheda completa").
- **Meta** (Archivo 400, 12-12.5px, larghezza 118%, spaziatura 0.04-0.05em, MAIUSCOLO, inchiostro attenuato): metadati della scheda (tipo di documento, livello, stato) e riga fonte della citazione. Lo stato di verifica è in inchiostro pieno e 700.
- **Nota** (Archivo 400, 12.5-13px, inchiostro attenuato): nota sotto il titolo, legenda della mappa, istruzioni d'uso, sotto-questione sopra la citazione.

### Named Rules
**The Lapide Rule.** Cinzel compare solo dove si nomina: tema, sotto-questione nel pop-up, marchio. Mai per testo corrente, metadati, bottoni o etichette.

**The Grottesco Largo Rule.** Archivo si usa sempre allargato (108% testo, 112% titoli, 118% etichette e sigle). Il maiuscolo spaziato è riservato a link, metadati e fonti; il testo di lettura resta in tondo minuscolo.

## Layout

Colonna singola su telefono (riferimento 390px), con margine laterale di 20px (gutter). Da 900px il margine diventa `max(48px, (100vw - 1120px) / 2)`, cioè un contenuto di circa 1120px centrato, e l'elenco delle schede passa a due colonne con 56px di spazio tra le colonne.

Sequenza della pagina tema: testata sottile (marchio a sinistra, percorso in maiuscoletto a destra, filetto sotto); titolo del tema in display; definizione rientrata di `clamp(0px, 8vw, 180px)` sotto il titolo, poi la nota; la mappa "chi parla di cosa" con legenda e istruzioni; le schede dei partiti in ordine alfabetico; in fondo l'azione verso il confronto. La pagina confronto ripete testata e titolo, poi la scelta dei partiti, la mappa ristretta ai partiti scelti e le schede affiancate (due colonne con filetto verticale tra le colonne; con un terzo partito diventano una colonna sola impilata).

Ritmo: le schede sono separate da un filetto e da 32-34px di aria sopra e sotto; dentro la scheda gli elementi stanno a 10-16px l'uno dall'altro; le azioni si staccano di 28px. La mappa è una griglia: colonna delle questioni flessibile, poi una colonna di 50px per partito su telefono; da 900px la colonna delle questioni prende almeno 200px e i partiti si dividono lo spazio restante in parti uguali. Ogni riga è alta almeno 54px.

### Named Rules
**The Parità Rule.** Ogni partito riceve la stessa sequenza di elementi, la stessa larghezza di colonna e lo stesso spazio, in ordine alfabetico. Nessun partito è evidenziato, ingrandito o messo per primo per altre ragioni.

**The Senza JavaScript Rule.** Schede, citazioni e confronto sono HTML leggibile senza script; le citazioni si aprono con `details`. Nel sito Astro la mappa è HTML statico generato dalle schede; nel prototipo la disegna JavaScript solo per non ripetere i dati a mano.

## Elevation & Depth

Il sistema è piatto. Non ci sono ombre: la profondità si esprime con il secondo tono di carta (pietra chiara) per i riquadri di citazione, con i filetti e con il velo bruno dietro il pop-up. L'unico strato sopra la pagina è il pop-up, che si distingue per il velo, non per un'ombra; la sua testa resta fissa in alto durante lo scorrimento, su fondo carta.

### Named Rules
**The Carta Piatta Rule.** Nessuna ombra, nessuna sfumatura. Un livello si separa dall'altro con un tono di carta, un filetto o il velo.

## Shapes

Angoli vivi ovunque: riquadri di citazione, pop-up, chip di scelta e schede non hanno raggio. Il tondo pieno è riservato a tre cose: i contrassegni dei partiti, i punti della mappa (e la loro area di tocco da 44px) e i bottoni d'azione scuri. Le linee sono filetti da 1px: inchiostro pieno sopra la mappa e sopra il confronto, filetto trasparente altrove; nella riga aperta della mappa su telefono i divisori tra partiti sono tratteggiati.

Icone in SVG a tratto 1.6px (più, freccia, chiudi) e 1.3px (cerchi della mappa). Il "più" ruota di 45 gradi per diventare una croce quando un elemento è aperto.

## Components

### Bottone tondo (azione)
Un disco scuro con una freccia, accompagnato da un'etichetta sottolineata: l'azione principale della pagina.
- **Forma:** cerchio (50%), 52px; 44px come bottone di chiusura nel pop-up.
- **Colori:** fondo inchiostro, icona carta (20px).
- **Uso:** accanto a un link in maiuscoletto sottolineato ("Confronta due partiti sulla sanità", "Aggiungi un terzo partito", "Controlla tu: apri il programma"); tutto il gruppo è il link.
- **Focus:** contorno inchiostro 2px a 3px di distanza, come ogni elemento attivo.

### Link in maiuscoletto
- **Stile:** Label (Archivo 600, 13px, larghezza 118%, maiuscolo), sottolineatura 1px.
- **Uso:** apertura delle citazioni (con il "più" che ruota), link alle schede, "Vai alla scheda completa".

### Scelta dei partiti (chip)
- **Stile:** riquadro ad angoli vivi, filetto, testo in inchiostro attenuato; selezionato: fondo inchiostro, testo carta.
- **Stato:** massimo tre partiti selezionati.

### Scheda del partito
Lo stesso schema per ogni partito, senza riquadro: separata dalla successiva con un filetto.
- **Ordine:** contrassegno (40px) con sigla e nome esteso; titolo; sintesi; riga di metadati (tipo di documento, livello, stato di verifica); link "Leggi nel programma · N citazioni" che apre le citazioni.
- **Posizione assente:** stessa sequenza e stesso spazio; il titolo dice che il programma non tratta il tema (peso 500), la sintesi lo spiega senza giudizio, e al posto delle citazioni c'è l'azione tonda "Controlla tu: apri il programma".

### Citazione
Il riquadro della prova.
- **Fondo:** pietra chiara, angoli vivi, padding 16px 18px.
- **Contenuto:** sotto-questione in nota sopra; testo alla lettera tra caporali «»; sotto, riga di meta in maiuscoletto con il documento a sinistra e la pagina a destra.
- **Pagina:** "p. N" è un link al PDF ufficiale aperto a quella pagina (`#page=N`), in inchiostro pieno, e non va mai a capo.

### Contrassegno
- **Forma:** il contrassegno depositato, nella sua forma circolare, a 40px nelle schede e nel pop-up, 30px nella testa della mappa, 32px nella riga aperta.
- **Regola:** sempre con la sigla scritta accanto o sotto; con alternativa testuale ("Contrassegno di …") quando è l'unica identificazione, `alt=""` quando la sigla è già scritta accanto.

### Mappa "chi parla di cosa"
Il componente distintivo: sotto-questioni in riga, partiti in colonna.
- **Testa:** "Questione" in meta maiuscolo a sinistra; per ogni partito contrassegno (30px) e sigla. Filetto inchiostro sopra.
- **Vocabolario degli stati:** punto pieno = ne parla; cerchio vuoto = non ne parla; cerchio tratteggiato = da verificare; trattino = niente da segnare, solo nella riga "Altro nel tema", che non è una sotto-questione. Una legenda sotto la mappa ripete i tre segni con le parole.
- **Punto:** bottone tondo da 44px con il segno a 16px; al passaggio del puntatore un alone pietra chiara. L'etichetta accessibile dice partito, questione e stato ("AVS, Medicina territoriale: ne parla. Apri").
- **Tocco su un punto:** apre il pop-up con le citazioni di quel partito su quella questione.
- **Tocco sulla questione:** la riga si apre, il "più" diventa croce, il nome passa a 700 e al posto dei punti compaiono le frasi dei partiti con la pagina. Su telefono ogni partito diventa una sotto-riga a tutta larghezza (contrassegno 32px e sigla a sinistra, frase a destra) separata da un filetto tratteggiato.

### Pop-up della citazione
- **Telefono (sotto 900px):** foglio che sale dal basso, a tutta larghezza, alto al massimo l'86% dello schermo; entra con una salita del 40% in 0.34s.
- **Schermi larghi:** finestra centrata, larga fino a 560px; entra con 18px di salita e dissolvenza.
- **Struttura:** testa fissa (contrassegno 40px, sigla, sotto-questione in Headline, bottone tondo di chiusura 44px a destra) separata da un filetto; corpo con riquadri di citazione; piede con "Vai alla scheda completa". Si chiude con il bottone, con Esc o toccando il velo.

### Testata
- **Stile:** marchio in Cinzel a sinistra, percorso in meta maiuscolo a destra con il primo livello come link; filetto sotto, padding 18px.

### Movimento
Una sola curva, `cubic-bezier(.16,1,.3,1)`: rotazione del "più" (0.25-0.3s) ed entrata del pop-up (0.34s). Con `prefers-reduced-motion` le transizioni si spengono.

## Do's and Don'ts

### Do:
- **Do** usare solo inchiostro bruno, inchiostro attenuato, carta crema e pietra chiara; la carta resta #FAF8F1, valore fissato dall'utente.
- **Do** identificare ogni partito con sigla scritta più contrassegno ufficiale, piccolo (30-40px) e inalterato, sempre con un'alternativa testuale.
- **Do** elencare i partiti in ordine alfabetico, ovunque: schede, colonne della mappa, scelta del confronto.
- **Do** esprimere lo stato di una posizione con un segno (punto pieno, cerchio vuoto, cerchio tratteggiato, trattino) e ripeterlo a parole in legenda ed etichetta accessibile.
- **Do** mostrare ogni citazione nel riquadro pietra chiara, tra caporali «», con documento e "p. N" come link al PDF ufficiale a quella pagina.
- **Do** dare a una posizione assente la stessa sequenza, lo stesso spazio e lo stesso posto in elenco di una posizione dichiarata.
- **Do** aprire il pop-up come foglio dal basso su telefono e come finestra centrata da 900px in su.
- **Do** tenere schede, citazioni e confronto leggibili senza JavaScript; la mappa interattiva è un arricchimento.
- **Do** dare ad ogni elemento toccabile almeno 44px e il contorno di focus in inchiostro da 2px.

### Don't:
- **Don't** usare colori di partito, né colori di stato (verde, rosso, giallo) per dire "ne parla" o "non ne parla".
- **Don't** ritagliare, ricolorare, deformare o ingrandire un contrassegno, né usarlo nel marchio di elezio.
- **Don't** usare ombre, sfumature o angoli arrotondati sui riquadri; il tondo è solo per contrassegni, punti e bottoni d'azione.
- **Don't** usare Cinzel per testo corrente, metadati o bottoni, né Archivo alla larghezza normale.
- **Don't** mettere fotografie o illustrazioni: l'unica immagine è il contrassegno.
- **Don't** mostrare una citazione senza documento e pagina.
- **Don't** usare il cerchio tratteggiato per altro che "da verificare".
