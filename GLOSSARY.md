# elezio

Sito che rende fruibili i programmi elettorali italiani per tema, li confronta tra partiti e offre un quiz di orientamento. Questo glossario fissa i termini del dominio; non contiene scelte di implementazione.

## Contenuto

**Partito**:
Soggetto politico in perimetro, identificato in modo stabile anche se cambia nome, si fonde o si scinde. Entra in perimetro solo se soddisfa il criterio di inclusione.
_Avoid_: lista, forza politica, movimento (come termine generico)

**Elezione di riferimento**:
L'elezione politica a cui una scheda e un documento fonte si riferiscono (2022, 2027). Le schede di elezioni diverse coesistono; quella più recente non cancella la precedente.
_Avoid_: anno, edizione, versione

**Documento fonte**:
Un documento ufficiale da cui si cita una posizione, registrato una sola volta con URL ufficiale, hash e data. Può essere un programma, un programma esteso, un accordo di coalizione o un documento programmatico; può essere condiviso da più partiti.
_Avoid_: fonte generica, riferimento

**Programma**:
Il documento ufficiale con cui un partito si presenta a una elezione politica, nella copia depositata al Ministero dell'Interno. Ha una elezione di riferimento. È il documento fonte primario.
_Avoid_: manifesto, piattaforma

**Programma esteso**:
La versione più lunga o più recente del programma pubblicata dal partito sul proprio sito e non depositata al Ministero. Si cita solo per i temi che il programma depositato non copre.
_Avoid_: programma completo, programma vero

**Accordo di coalizione**:
Un documento fonte depositato da più partiti insieme al posto di programmi di partito distinti. Le posizioni che ne derivano sono posizioni di coalizione.
_Avoid_: programma comune, programma di coalizione

**Documento programmatico**:
Un documento fonte ufficiale di un partito che non è un programma elettorale: manifesto, statuto, documento di indirizzo. Si usa quando il partito non ha un programma per l'elezione di riferimento.
_Avoid_: manifesto (come termine generico), documento di partito

**Tema**:
Una delle 12 aree di policy fisse in cui v1 organizza i contenuti, con un nome canonico, una definizione di una riga e un ordine di presentazione. Ogni proposta appartiene a un solo tema: in caso di dubbio decide lo strumento che cambia (la legge, la voce di bilancio, l'ente che agisce), non l'obiettivo né il destinatario. Non esiste un tema "altro".
_Avoid_: argomento, categoria, topic, area

**Sotto-questione**:
Una delle 3-6 questioni fisse in cui un tema si articola, uguale per tutti i partiti e per tutte le elezioni. Guida l'ordine della sintesi, la scelta del titolo della scheda e le affermazioni del quiz. Non è una scheda: per ogni partito, tema ed elezione la scheda resta una sola. Può restare vuota per una elezione se nessun documento fonte la tratta.
_Avoid_: sottotema, sezione, punto, sotto-tema

**Scheda**:
L'unità di contenuto: la posizione di un partito su un tema per una elezione di riferimento, con titolo, sintesi semplice, citazioni, riferimento al documento fonte e stato di verifica. Per ogni partito, tema ed elezione esiste al massimo una scheda.
_Avoid_: card, voce, posizione (per indicare l'intera unità), proposta originale

**Posizione**:
Ciò che un partito propone o sostiene su un tema, come risulta dal documento fonte. Una scheda contiene una posizione; una posizione è dichiarata (sostenuta da almeno una citazione) oppure assente (nessun documento fonte del partito tratta il tema). Non esistono posizioni inferite.
_Avoid_: opinione, idea, posizione inferita

**Posizione di coalizione**:
Una posizione dichiarata in un documento fonte condiviso da più partiti. È attribuita a ciascuno di quei partiti e il lettore vede che è di coalizione, non del singolo partito.
_Avoid_: posizione comune, posizione condivisa

**Citazione**:
Frammento testuale preso alla lettera dal documento fonte, con riferimento al documento e alla pagina. Ogni posizione dichiarata ne ha almeno una; le citazioni di una scheda non superano in totale le 300 parole.
_Avoid_: estratto, quote

**Sintesi**:
Riscrittura in linguaggio semplice della posizione, pensata per chi legge da telefono. Segue l'ordine delle sotto-questioni del tema e tocca solo quelle che il documento fonte tratta. Non sostituisce la citazione.
_Avoid_: riassunto, spiegazione

**Stato di verifica**:
Dove si trova una scheda nel processo editoriale: bozza (non pubblicata), verificata (controllata dal revisore, pubblicabile), contestata (segnalazione aperta dopo la pubblicazione, resta online con avviso). Lo cambia solo il revisore.
_Avoid_: status, flag, superata (non è uno stato)

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

**Criterio di inclusione**:
La regola pubblica che decide quali partiti sono in perimetro: più del 2 percento alle ultime elezioni politiche, oppure almeno 5 parlamentari in carica che dichiarano l'appartenenza al momento del rilascio. Per ogni partito si registra quale via lo ha incluso e quando è stata verificata.
_Avoid_: soglia, lista dei partiti, eccezione

**Revisore**:
La persona che verifica una scheda prima della pubblicazione. In v1 è il maintainer.
_Avoid_: editor, moderatore

**Registro delle correzioni**:
L'elenco pubblico delle modifiche fatte alle schede dopo la pubblicazione, con data e motivo.
_Avoid_: changelog, errata
