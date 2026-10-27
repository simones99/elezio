# elezio

Sito che rende fruibili i programmi elettorali italiani per tema, li confronta tra partiti e offre un quiz di orientamento. Questo glossario fissa i termini del dominio; non contiene scelte di implementazione.

## Contenuto

**Partito**:
Soggetto politico in perimetro, identificato in modo stabile anche se cambia nome, si fonde o si scinde.
_Avoid_: lista, forza politica, movimento (come termine generico)

**Programma**:
Il documento ufficiale con cui un partito si presenta a una elezione politica. Ha una elezione di riferimento (2022, 2027).
_Avoid_: manifesto, piattaforma

**Documento fonte**:
Qualsiasi documento ufficiale da cui si cita una posizione: il programma, oppure un documento programmatico diverso quando il programma manca o non copre un tema.
_Avoid_: fonte generica, riferimento

**Tema**:
Una delle 12 aree di policy fisse in cui v1 organizza i contenuti. Ogni proposta appartiene a un solo tema.
_Avoid_: argomento, categoria, topic

**Scheda**:
L'unità di contenuto: la posizione di un partito su un tema, con sintesi semplice, proposta originale, citazione, riferimento al documento fonte e stato di verifica.
_Avoid_: card, voce, posizione (per indicare l'intera unità)

**Posizione**:
Ciò che un partito propone o sostiene su un tema, come risulta dal documento fonte. Una scheda contiene una posizione; una posizione può essere dichiarata, inferita o assente.
_Avoid_: opinione, idea

**Citazione**:
Frammento testuale preso alla lettera dal documento fonte, con riferimento alla pagina. Ogni posizione dichiarata ne ha almeno una.
_Avoid_: estratto, quote

**Sintesi**:
Riscrittura in linguaggio semplice della posizione, pensata per chi legge da telefono. Non sostituisce la citazione.
_Avoid_: riassunto, spiegazione

**Stato di verifica**:
Dove si trova una scheda nel processo editoriale: almeno bozza e verificata; gli altri stati sono da decidere. Si pubblicano solo schede verificate.
_Avoid_: status, flag

**Confronto**:
La presentazione affiancata delle schede di due o tre partiti sullo stesso tema.
_Avoid_: comparazione, versus

## Quiz

**Affermazione**:
Una frase di policy a cui chi fa il quiz risponde con accordo o disaccordo. Ogni affermazione è legata a un tema e a una posizione per ciascun partito.
_Avoid_: domanda, tesi, statement

**Affinità**:
Il punteggio che il quiz calcola tra le risposte di chi lo fa e le posizioni di ciascun partito. La formula è pubblica.
_Avoid_: match, compatibilità, allineamento

## Processo

**Revisore**:
La persona che verifica una scheda prima della pubblicazione. In v1 è il maintainer.
_Avoid_: editor, moderatore

**Registro delle correzioni**:
L'elenco pubblico delle modifiche fatte alle schede dopo la pubblicazione, con data e motivo.
_Avoid_: changelog, errata
