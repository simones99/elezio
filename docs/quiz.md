# Quiz: affermazioni, risposte dei partiti, configurazione di Open Election Compass

Ultimo aggiornamento: 28 ottobre 2026. Decisioni di fondo in [ADR 0007](adr/0007-modello-del-quiz.md); termini in [GLOSSARY.md](../GLOSSARY.md); deciso nel ticket [Modello del quiz di orientamento](https://github.com/simones99/elezio/issues/8), con il passaggio al quiz 2027 deciso nel ticket [Playbook Fase 2](https://github.com/simones99/elezio/issues/12). Questo file è la vista operativa e cambia più spesso dell'ADR.

## Layout dei file

```
contenuti/quiz/<elezione>/<affermazione>.yaml   # un file per affermazione
```

Esempio: `contenuti/quiz/2022/salario-minimo.yaml`. Lo slug dell'affermazione è il nome del file, stabile dopo la creazione.

## Affermazione (`quiz/<elezione>/<affermazione>.yaml`)

| Campo | Obbligatorio | Tipo | Note |
| --- | --- | --- | --- |
| `elezione` | sì | intero | Deve coincidere con la cartella. |
| `tema` | sì | slug | Uno dei 12 temi di `contenuti/temi.yaml`. |
| `sotto_questione` | sì | stringa | Una delle `sotto_questioni` del tema, scritta identica. |
| `ordine` | sì | intero da 1 | Posizione nel quiz. Unico nell'elezione. |
| `testo` | sì | stringa | L'affermazione. Al massimo 20 parole; senza i caratteri `[ ] < > { } @ \|` (sintassi di Open Election Compass e di vue-i18n). |
| `risposte` | sì | mappa | Chiave: slug del partito. Valore: risposta del partito, vedi sotto. |
| `stato` | sì | `bozza` \| `verificata` \| `contestata` | Come per le schede. |
| `verificata_il` | se stato ≠ bozza | data ISO | |
| `revisore` | se stato ≠ bozza | stringa | Handle GitHub. |
| `aggiornata_il` | sì | data ISO | Ultima modifica. |
| `note` | no | stringa | Note interne. Non pubblicate. |

### Risposta del partito

| Campo | Obbligatorio | Note |
| --- | --- | --- |
| `risposta` | sì | `accordo` \| `disaccordo`. Non esiste il neutro per i partiti. |
| `citazione` | sì | `id` di una citazione nella scheda `schede/<elezione>/<partito>/<tema>.md`, dove elezione e tema sono quelli dell'affermazione. |

Esempio:

```yaml
elezione: 2022
tema: lavoro
sotto_questione: Salario minimo
ordine: 3
testo: Serve un salario minimo stabilito per legge.
risposte:
  pd:
    risposta: accordo
    citazione: salario-minimo-9-euro
  azione:
    risposta: disaccordo
    citazione: contrattazione-collettiva
  # ... un elemento per ogni partito del quiz
stato: verificata
verificata_il: 2027-01-20
revisore: simones99
aggiornata_il: 2027-01-18
```

Il testo della citazione non si ripete qui: vive solo nella scheda. Le citazioni richiamate dal quiz hanno un `id` stabile (vedi `docs/schema-scheda.md`), così riordinare le citazioni di una scheda non cambia la risposta.

## Partiti del quiz e raggruppamenti (derivati in build)

- **Partiti del quiz**: i partiti in perimetro che hanno almeno una fonte di tipo `programma`, `programma_esteso` o `accordo_coalizione` con l'elezione del quiz. Nel 2022 sono 9, senza Futuro Nazionale (solo documento programmatico).
- **Raggruppamento**: due partiti stanno nello stesso raggruppamento se, su tutte le affermazioni pubblicate, danno la stessa risposta e citano la stessa fonte, condivisa da entrambi. La relazione è transitiva. Nel 2022 formano un raggruppamento Fratelli d'Italia, Lega e Forza Italia (accordo di coalizione) e Azione e Italia Viva (programma unico della lista), quindi il quiz 2022 ha 6 righe: PD, M5S, AVS, +Europa, Azione-IV, FdI-Lega-FI. Nessun file lo dichiara: se un partito cambia una sola risposta o fonte, il raggruppamento si scioglie da solo.

## Regole di pubblicazione (applicate dall'endpoint Astro)

Un'affermazione entra nel JSON del quiz solo se:

1. è `verificata`;
2. ha una risposta per ogni partito del quiz;
3. ogni scheda citata è `verificata` e contiene la citazione con quell'`id`.

Un'affermazione `contestata`, o che cita una scheda `contestata`, resta fuori finché la segnalazione non si chiude. Se le affermazioni pubblicabili sono meno di 20, `/quiz/` non carica Open Election Compass e mostra un avviso di sospensione. Sul sito c'è solo il quiz dell'elezione più recente che ha almeno 20 affermazioni pubblicabili.

### Passaggio al quiz 2027

Il quiz 2027 si costruisce tema per tema: le 2 affermazioni di un tema, con le risposte dei partiti, stanno nella stessa PR delle schede 2027 di quel tema e si pubblicano con il suo merge. `ordine` si riassegna a ogni PR, così resta senza buchi e senza due temi uguali di seguito. Il quiz 2027 si accende alla ventesima affermazione pubblicabile, cioè dopo circa 10 temi, e la sua accensione è il lancio pubblico ([playbook-fase-2.md](playbook-fase-2.md)).

Fino ad allora resta il quiz 2022, con l'avviso "basato sui programmi 2022, non su quelli di questa elezione", e sparisce dalla home appena esiste un documento fonte 2027. Un partito il cui programma 2027 arriva tardi diventa partito del quiz appena ha la fonte: le affermazioni a cui non risponde ancora escono dal quiz per la regola 2 finché la sua PR non le completa.

## Criteri di formulazione

Pubblicati nella pagina metodologia.

1. Una sola proposta concreta per affermazione, formulata sullo strumento che cambia (stessa regola dei temi).
2. Niente aggettivi valutativi, parole cariche, doppie negazioni o "e/o".
3. Direzione bilanciata: "accordo" non coincide sempre con la stessa area politica.
4. Discriminazione: nessuna affermazione su cui tutti rispondono uguale; ogni riga del quiz (partito o raggruppamento) ha almeno 6 accordi e 6 disaccordi.
5. Linguaggio da terza media, al massimo 20 parole.

Copertura: 24 affermazioni, 2 per tema, mai due sulla stessa sotto-questione. Ordine fisso con i temi alternati, mai due affermazioni dello stesso tema di seguito. Affermazioni e risposte si scrivono a mano, senza LLM, dopo che le schede del tema sono verificate (dal 2027 nella stessa PR del tema).

## Controlli

- **Schema zod** (singolo file): campi, enum, `elezione` uguale alla cartella, `tema` esistente, `testo` senza caratteri riservati e al massimo 20 parole, `risposta` solo `accordo` o `disaccordo`.
- **`pipeline verifica`** (incroci tra file):
  - `sotto_questione` appartiene al tema;
  - ogni `citazione` esiste nella scheda indicata;
  - `ordine` è unico e senza buchi;
  - non ci sono due affermazioni dello stesso tema di seguito né due sulla stessa sotto-questione;
  - nessuna affermazione è unanime;
  - ogni riga ha tra 6 e 18 accordi. È il controllo automatico dei criteri 3 e 4: verifica l'equilibrio senza classificare i partiti su un asse destra-sinistra, cosa che elezio non fa.

## Mappatura sul JSON di Open Election Compass

Il JSON è generato da `sito/src/pages/quiz/config.json.ts` e incluso inline nella pagina come `<script type="application/json" id="config">`. Lingua unica: `languages: [{name: "Italiano", code: "it"}]`, ogni testo è `{it: "..."}`.

| Campo OEC | Da |
| --- | --- |
| `version` | `"1"` |
| `algorithm` | `"cityblock/approve-neutral-reject"` (default, scritto esplicito) |
| `title`, `subtitle` | Fissi: "Quiz sui programmi", "Politiche <elezione>". |
| `introduction.heading`, `.text` | Testo fisso, vedi sotto. |
| `parties[]` | Una voce per riga del quiz. `alias`: slug del partito, oppure slug del raggruppamento (slug dei partiti in ordine alfabetico uniti da `-`). `name`: nome del partito, oppure sigle unite da ", ". `short`: `sigla`. `description`: una riga di fatto senza giudizi, es. "Programma depositato per le politiche 2022" o "Accordo di coalizione depositato per le politiche 2022". `logo`: contrassegno del partito. Per un raggruppamento si decide in implementazione se OEC accetta una voce senza logo. |
| `theses[]` | Le affermazioni pubblicabili in ordine di `ordine`. `title`: nome del tema. `statement`: `testo`. |
| `theses[].positions.<alias>.position` | `accordo` → `approve`, `disaccordo` → `reject`. `neutral` e `skip` non si generano mai. |
| `theses[].positions.<alias>.explanation` | «testo della citazione» seguito da titolo breve della fonte e pagina, es. «...» (Accordo di coalizione 2022, p. 12). Il testo passa da vue-i18n: il generatore escapa `{ } @ \|` con l'interpolazione letterale (`{'@'}`) e un test lo verifica. Niente link: Open Election Compass mostra testo semplice. |
| `footer-links[]` | Metodologia, Temi, Crediti, Privacy. |
| `analysis` | Assente. Modalità `friends` non attivata. |

Ogni partito deve avere una voce sotto ogni affermazione, altrimenti Open Election Compass va in errore: le regole di pubblicazione lo garantiscono.

## Testi

- **Introduzione**: "Il quiz confronta le tue risposte con i programmi depositati per le politiche <elezione>. Per ogni affermazione scegli d'accordo, neutro o in disaccordo, oppure saltala. Non è un consiglio di voto."
- **Formula**, mostrata nei risultati con `languages[].overwrites`: "2 punti se la tua risposta coincide con quella del partito, 1 se una delle due è neutra, 0 se sono opposte. Le affermazioni che segni come importanti valgono doppio, quelle saltate non contano. L'affinità è la percentuale sul massimo possibile." La chiave di `it.json` da sovrascrivere si sceglie in implementazione.
- I limiti di Open Election Compass restano quelli predefiniti: "importante" al massimo per metà delle affermazioni, "salta" al massimo per un quarto.

## Evento "quiz completato"

Open Election Compass non emette eventi verso la pagina. I risultati compaiono quando `parties.chosen` dello store Vuex diventa `true`, e non torna più `false` (il reset ricarica la pagina). Lo store si raggiunge dall'app Vue montata sul contenitore. Script inline dopo il bundle, solo in produzione:

```js
const store = document.getElementById('open-election-compass')
  .__vue_app__.config.globalProperties.$store;
let inviato = false;
store.watch((s) => s.parties.chosen, (scelto) => {
  if (scelto && !inviato) {
    inviato = true;
    window.goatcounter?.count({ path: 'quiz-completato', event: true });
  }
});
```

Si invia solo l'evento, mai risposte o risultato. È un interno non documentato, stabile perché il bundle è fissato alla 2.0.0-alpha.5. Il test Playwright di `/quiz/` completa il quiz e verifica che la chiamata parta, così un aggiornamento del bundle che rompe l'aggancio fa fallire la CI. In alternativa, un MutationObserver su `[data-section="match"]`.

Fonti nel sorgente della v2.0.0-alpha.5: `src/store/modules/parties/calculatePointsForParty.js`, `src/store/modules/theses/theses.js` (`maxPoints`), `src/store/modules/parties/parties.js`, `src/components/views/home/sections/06-compare/FullAnswer.vue`, `src/main.ts`.

## Piano di riserva

Se i dati 2022 non danno almeno 20 affermazioni con risposta di tutti i partiti del quiz, si valuta una patch del bundle che tolga dal massimo di un partito le affermazioni a cui non risponde (ADR 0007, opzioni considerate).
