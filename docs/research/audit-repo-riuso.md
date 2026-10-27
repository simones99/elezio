# Audit delle repository open source candidate al riuso

Ticket: https://github.com/simones99/elezio/issues/2

Data dell'audit: 2026-10-27. Tutti i dati di attività, licenza e dipendenze vengono dall'API GitHub (`gh api`), dal registro npm, da unpkg e dai file sorgente delle repository, non dalla ricerca di settore preesistente (`ricerca/repository_open_source_politica_italiana.md`), che su più punti risulta datata o imprecisa (vedi "Correzioni alla ricerca precedente").

## Domanda

Quali componenti delle cinque repository candidate sono realmente riusabili per elezio v1, a quali condizioni di licenza (il progetto è AGPL-3.0), e quale vincolo di stack ne deriva? In particolare: Open Election Compass (Vue 3) può vivere dentro un sito statico non-Vue, o impone Vue/Nuxt a tutta l'app?

## Risposta breve

- **Open Election Compass (OEC) non impone Vue all'app.** Il pacchetto npm `@open-election-compass/client` è una libreria compilata da Vite in modalità `lib` con Vue incluso nel bundle: si monta in qualsiasi pagina HTML con un `<div id="open-election-compass">`, un tag custom `<open-election-compass load-url="...">` e un unico `<script>` (UMD, 871 KB minificato, circa 273 KB gzip). È la modalità di deploy ufficiale "Option 2: manual, static set-up". La via Nuxt invece è rotta nella versione pubblicata (vedi trappole).
- **Mat-O-Wahl** è un'app jQuery/Bootstrap 4 senza sistema di moduli, incorporabile solo per iframe; funziona ed è mantenuta, ma il codice è legacy per ammissione dell'autore (il changelog elenca "remove all jquery, use JavaScript-Framework" tra i to-do).
- **Licenze:** OEC e Mat-O-Wahl sono GPL-3.0, combinabili con AGPL-3.0 per esplicita previsione di GPLv3 §13 e AGPLv3 §13. Stemwijzert ed Electio Italia **non hanno licenza** (copyright esclusivo per default): si possono solo leggere e citare. Programmi Elettorali 2022 è GPL-2.0 senza clausola "or later": **incompatibile** con AGPL-3.0; la repository del sorgente è senza licenza.
- **Raccomandazione:** riusare OEC come componente quiz montato via script UMD in un sito statico (Astro o equivalente) su un sottopercorso tipo `/quiz/`, con configurazione JSON generata dalla pipeline dati di elezio. Lo stack dell'app resta libero. Mat-O-Wahl resta il piano B se OEC si rivela troppo rigido nell'aspetto o nel flusso.

## Metodo

Per ogni repository ho letto via API GitHub: metadati (licenza rilevata, `pushed_at`, stelle, fork, issue aperte, `archived`), ultimi commit, release e tag, issue aperte, albero dei file, `package.json`/`requirements.txt`, README, testo del file LICENSE e i file sorgente del motore di scoring. Per OEC ho inoltre verificato il registro npm (`registry.npmjs.org`), il contenuto effettivo del pacchetto pubblicato su unpkg (percorsi, dimensioni, host esterni citati nel bundle) e la guida di deploy ufficiale. Per Programmi Elettorali ho estratto i dati dal bundle JS e dal JSON sorgente e verificato con `curl` se i link ai programmi rispondono ancora. Per le licenze ho usato i testi GPLv3/AGPLv3/GPLv2 e le FAQ GNU.

## 1. Open Election Compass (client)

Repository: https://github.com/open-election-compass/client

### Licenza

- `LICENSE` è il testo integrale della GNU GPL v3 ([LICENSE](https://github.com/open-election-compass/client/blob/master/LICENSE)); `package.json` dichiara `"license": "GPL-3.0"` ([package.json](https://github.com/open-election-compass/client/blob/master/package.json)).
- La dipendenza `@open-election-compass/ui` (0.14.0) è dichiarata GPL-3.0 nel registro npm; la repository GitHub `open-election-compass/ui` però non espone un file LICENSE rilevato dall'API (`license: null`). Rischio basso perché la UI arriva già inclusa nel bundle del client, ma da annotare nei crediti.

### Attività (verificata)

- Ultimo push: **2025-07-16** (4 commit: traduzione bulgara, tre fix CI per conflitti di peer dependency). Prima di questi, l'ultimo commit era del **2022-08-27** ([commits](https://github.com/open-election-compass/client/commits/master)).
- Ultima release: **v2.0.0-alpha.5 del 2022-08-27**, marcata prerelease ([releases](https://github.com/open-election-compass/client/releases)). Su npm `latest` = `2.0.0-alpha.5` (pubblicata 2022-08-27); `package.json` in master è a `2.0.0-alpha.6`, mai pubblicata ([npm](https://registry.npmjs.org/@open-election-compass/client)).
- Issue aperte: 32, di cui 6 sono PR automatiche (Dependabot, Crowdin) e la maggior parte sono richieste di funzionalità del 2020-2021. L'issue più recente (#73, 2026-10-22) è un'organizzazione spagnola che chiede di essere elencata tra le istanze per le elezioni del 29-11-2026: segno che il progetto ha ancora un pubblico, non che sia sviluppato attivamente ([issues](https://github.com/open-election-compass/client/issues)).
- 43 stelle, 8 fork. Non archiviata.

Giudizio: **manutenzione minima** (un intervento in tre anni), ma il codice è stabile e usato in produzione da terzi. Nessuna garanzia di risposta a bug.

### Stack e dipendenze

Vue 3.2, Vite 3, TypeScript 4.8, Vuex 4, vue-i18n 9, vee-validate 4 + yup, @vueuse 9, FontAwesome 6, peerjs 1.4 (modalità "friends"), mitt, lodash, nanoid ([package.json](https://github.com/open-election-compass/client/blob/master/package.json)). Tutte le versioni sono del 2022; le PR Dependabot aperte (json5, loader-utils, minimatch, http-cache-semantics) non sono state mergiate. Nel luglio 2025 la CI ha dovuto aggiungere `npm set strict-ssl false && npm ci --force` per far passare l'installazione ([pages.yml](https://github.com/open-election-compass/client/blob/master/.github/workflows/pages.yml)): ricompilare dal sorgente oggi è fragile.

### Come si integra in un sito statico non-Vue (la domanda chiave)

Fatti verificati sul sorgente e sul pacchetto pubblicato:

1. `vite.config.ts` compila in modalità `build.lib` con entry `src/main.ts`, nome globale `OpenElectionCompass`, output `open-election-compass.{umd,es}.min.js`, e con l'alias `vue: 'vue/dist/vue.esm-bundler.js'` (runtime compiler incluso, serve per interpretare il tag custom nell'HTML) ([vite.config.ts](https://github.com/open-election-compass/client/blob/master/vite.config.ts)).
2. `src/main.ts` crea l'app Vue, registra il componente `open-election-compass` e chiama `app.mount('#open-election-compass')` da solo: il bundle si auto-monta appena caricato ([main.ts](https://github.com/open-election-compass/client/blob/master/src/main.ts)).
3. Il pacchetto su npm contiene `dist/open-election-compass.umd.min.js` (871.560 byte, ~273 KB gzip) e `dist/open-election-compass.es.min.js` (1.174.103 byte), più le demo HTML ([unpkg listing](https://unpkg.com/browse/@open-election-compass/client@2.0.0-alpha.5/dist/)). Vue è inlined: nessuna dipendenza esterna da installare.
4. Il componente accetta `load-tag` (selettore di uno `<script type="application/json">` inline), `load-url` (JSON remoto) o `load-object` ([OpenElectionCompass.vue](https://github.com/open-election-compass/client/blob/master/src/OpenElectionCompass.vue), [demo-luedenscheid.html](https://github.com/open-election-compass/client/blob/master/public/demo-luedenscheid.html)).
5. La guida ufficiale documenta esattamente questo uso come "Option 2: manual, static set-up": uno `<script src=... defer>` nel `<head>`, il div contenitore e il tag custom ([deployment guide](https://open-election-compass.com/guide/technical/deployment.html)).

Quindi le tre opzioni del ticket si risolvono così:

- **Build separata montata su un sottopercorso**: non serve una build; basta copiare il file UMD nel sito (la guida stessa consiglia di self-hostarlo "for privacy, security and legal reasons") e creare una pagina `/quiz/index.html` con div + tag + JSON. Lo SSG scelto per elezio non è coinvolto.
- **Iframe**: possibile e consigliabile se si vuole isolare il CSS. Il componente ha uno `<style lang="scss">` globale non scoped oltre a uno scoped ([OpenElectionCompass.vue](https://github.com/open-election-compass/client/blob/master/src/OpenElectionCompass.vue), righe 305 e 335), e carica `@open-election-compass/ui/style.css` ([loadOpenElectionCompassUI.ts](https://github.com/open-election-compass/client/blob/master/src/bootstrap/loadOpenElectionCompassUI.ts)): in una pagina condivisa può esserci interferenza di stili con il resto del sito. Un iframe (o la pagina dedicata di cui sopra, senza altri elementi) evita il problema.
- **Web component**: OEC non espone un custom element registrato con `customElements.define`; il tag `<open-election-compass>` è un componente Vue risolto dal runtime compiler dentro `#open-election-compass`. Non serve comunque: il montaggio automatico copre il caso d'uso.

Conclusione: **OEC non impone Vue, Nuxt o Vuex all'app.** Impone solo una pagina (o iframe) in cui si carica il suo script. Il vincolo reale è un altro: non si può personalizzare l'interfaccia senza forkare e ricompilare (con la fragilità della toolchain 2022 vista sopra).

### Cosa si riusa così com'è

- **Quiz completo**: start, introduzione, tesi con voto (approvo / neutrale / respingo, o scala a 5 con l'algoritmo "hybrid"), marcatura "importante" (peso doppio, massimo 50% delle tesi), skip (massimo 25%), selezione partiti, pagina risultati con percentuali e confronto tesi per tesi con le spiegazioni di ogni partito ([theses.js](https://github.com/open-election-compass/client/blob/master/src/store/modules/theses/theses.js), [sezioni](https://github.com/open-election-compass/client/tree/master/src/components/views/home/sections)).
- **Scoring**: `calculatePointsForParty` somma, per ogni tesi non saltata, `points[posizioneUtente][posizionePartito] * factor` secondo la matrice dell'algoritmo scelto (es. cityblock: 2/1/0) ([calculatePointsForParty.js](https://github.com/open-election-compass/client/blob/master/src/store/modules/parties/calculatePointsForParty.js), [approve-neutral-reject.js](https://github.com/open-election-compass/client/blob/master/src/store/modules/algorithm/algorithms/cityblock/approve-neutral-reject.js)). Sono circa 20 righe senza dipendenze: anche se un giorno si riscrivesse la UI, il metodo è portabile e documentato.
- **Localizzazione italiana**: `src/locales/it.json` ha le stesse 192 stringhe di `en.json` e `de.json` (conteggio sui file). Ogni stringa è sovrascrivibile dal JSON di configurazione (`languages[].overwrites`).
- **Editor di configurazione e HTML generator online** (sul sito del progetto), **guida metodologica** per scrivere e validare le tesi ([Organisation Guide](https://open-election-compass.com/guide/organisation/01-introduction.html)).
- **Formato dati**: JSON con `version`, `languages`, `title`, `subtitle`, `introduction`, `theses[].statement` + `positions{alias:{position, explanation}}`, `parties[]{name, short, alias, description, logo}`, `algorithm`, `analysis`, `footer-links` ([public/index.html](https://github.com/open-election-compass/client/blob/master/public/index.html), [Technical Guide](https://open-election-compass.com/guide/technical/overview.html)). È il contratto che la pipeline dati di elezio deve produrre.

### Cosa va fatto da noi

- Generare il JSON di configurazione da dati versionati nel repo (tesi, posizioni, spiegazioni, loghi).
- Decidere se abilitare `friends` (sessione condivisa via PeerJS) e `analysis` (POST opzionale con opt-in a un endpoint). Entrambe sono disattive per default.
- Tema grafico: solo via CSS sovrapposto o fork.

### Trappole note

1. **Il percorso CDN nella guida è sbagliato per la versione corrente.** La guida indica `.../dist/lib/open-election-compass.umd.min.js`; su `2.0.0-alpha.5` quel percorso risponde 404, il file è in `.../dist/open-election-compass.umd.min.js` (200). Il percorso `dist/lib/` è quello di `1.0.0-beta.13` (Vue 2.6) ([package.json 1.0.0-beta.13](https://unpkg.com/@open-election-compass/client@1.0.0-beta.13/package.json)).
2. **La via Nuxt è rotta.** `src/nuxtModule.js` aggiunge il plugin `dist/nuxt/open-election-compass.common.js` e il CSS `dist/nuxt/open-election-compass.css`, ma la cartella `dist/nuxt/` non esiste nel pacchetto pubblicato (404 su unpkg). È anche un modulo Nuxt 2 (`this.addPlugin`, `this.options.css`). Non usare Nuxt per OEC.
3. **Script npm incoerenti.** `package.json` definisce `build` come `build:demo && build:lib && build:nuxt` e il README cita `test:e2e`, ma nessuno di quegli script esiste; esiste solo `build-only` (`vite build`), che è quello usato dal workflow di pubblicazione npm. Anche `pages.yml` invoca `build:demo`, inesistente.
4. **Versione "alpha" da tre anni.** `2.0.0-alpha.5` è la versione di produzione di fatto; README parla ancora di "Version 1.0.0 is still under development".
5. **Modalità friends**: il bundle contiene i default `friends.open-election-compass.com` e `0.peerjs.com`; è attiva solo con l'attributo `friends`. Per il GDPR, lasciarla spenta o self-hostare un server PeerJS.
6. **Il bundle include un runtime compiler Vue completo**: 871 KB minificati su una pagina. Accettabile per una pagina quiz dedicata, non per essere caricato su ogni pagina del sito.

## 2. Mat-O-Wahl

Repository: https://github.com/msteudtn/Mat-O-Wahl

### Licenza

GPL-3.0: `LICENSE` è il testo GPLv3 ([LICENSE](https://github.com/msteudtn/Mat-O-Wahl/blob/master/LICENSE)); `system/` contiene anche `License-GPL-3.0-en.txt` e `License-MIT-jquery.txt`. Il README sezione "LIZENZ" lo conferma. jQuery e Bootstrap sono MIT, vendorizzati.

### Attività (verificata)

- Ultimo push **2026-10-26** (`pushed_at`), ultimo commit visibile su master **2026-09-06** (changelog); dicembre 2025 lavori sul workflow Docker; aprile 2025 fix a `quicktest` e `general.js` ([commits](https://github.com/msteudtn/Mat-O-Wahl/commits/master)).
- Ultima release **0.6.0.11.20250406** (2025-04-06, supporto Docker); `general.js` riporta `version = "0.6.0.12.20250425"` ([changelog](https://github.com/msteudtn/Mat-O-Wahl/blob/master/system/changelog.md)).
- 21 issue aperte (quasi tutte in tedesco, richieste di funzionalità 2021-2023; una del 2025-12 su Docker). 44 stelle, 27 fork, creata nel 2015.

Giudizio: **mantenuta da un singolo autore a ritmo lento ma costante**; livello di attività superiore a OEC.

### Stack

HTML + jQuery 3.4.1 + Bootstrap 4 + `jquery.csv 0.8.9`, variabili globali, nessun bundler né npm ("**kein** npm, yarn..." nel README). `index.html` carica `data/definition.js` (costanti di configurazione), `system/general.js`, `system/output.js`, e inietta CSS e addon con `document.writeln` ([index.html](https://github.com/msteudtn/Mat-O-Wahl/blob/master/index.html)). Docker = `nginx:1.27.3` che copia la cartella ([Dockerfile](https://github.com/msteudtn/Mat-O-Wahl/blob/master/Dockerfile)).

### Dati

Due CSV a due colonne: domande (`"Breve";"Testo della tesi"`) e partiti a blocchi chiave-valore (`Partei_kurz:`, `Partei_lang:`, `Partei_Beschreibung:`, `Partei_URL:`, `Partei_Bild:` poi le risposte) ([Obsthausen_Fragen.csv](https://github.com/msteudtn/Mat-O-Wahl/blob/master/data/Obsthausen_Fragen.csv), [Obsthausen_Parteien.csv](https://github.com/msteudtn/Mat-O-Wahl/blob/master/data/Obsthausen_Parteien.csv)). Il numero di domande va dichiarato a mano in `definition.js` (`intQuestions`). HTML ammesso dentro le celle.

### Scoring

In `fnEvaluation()`: posizioni utente e partito in {1, 0, -1}; coincidenza = 1 punto, se una delle due è neutrale = 0,5; fattore 2 se "molto importante"; 99 = saltata, esclusa; risultato in percentuale del massimo ([general.js](https://github.com/msteudtn/Mat-O-Wahl/blob/master/system/general.js) righe 100-170). Solo tre risposte; la scala a cinque è un fork esterno citato nei to-do.

### Lingue

Solo `i18n/i18n_de.js` e `i18n/i18n_en.js` (variabili globali `TEXT_*`). L'italiano va aggiunto creando `i18n_it.js`: lavoro di un'ora.

### Integrazione in un sito statico

Mat-O-Wahl è una pagina intera, non un componente: è pensata per vivere nella propria cartella e l'unico meccanismo di incorporamento ufficiale è l'iframe con gli addon `addon_check_iframe_resize_host.js` / `_client.js` ([extras/readme.md](https://github.com/msteudtn/Mat-O-Wahl/blob/master/extras/readme.md)). Nessun vincolo di stack sull'app ospite, ma anche nessuna integrazione: jQuery e Bootstrap 4 dentro l'iframe, tema e tipografia separati da quelli del sito.

### Trappole

- Statistiche opzionali via PHP/MySQL (`extras/statistics*`): da non abilitare.
- Issue #77: rimuovere un partito dal CSV rende inutilizzabile la tabella delle statistiche (solo se si usa la statistica).
- Issue #73 e #69: conflitti fra addon (filtro testo, limit results, contatti).
- Codice con `document.writeln`, variabili globali, nessun test: ogni modifica è manuale.

## 3. Stemwijzert (Blind Party Ranking)

Repository: https://github.com/ERRuijs/Stemwijzert

- **Nessuna licenza**: l'API GitHub restituisce `license: null` e `GET /repos/.../license` risponde 404. Senza licenza il codice è sotto copyright esclusivo dell'autore ([choosealicense.com/no-permission](https://choosealicense.com/no-permission/)); i Terms of Service di GitHub permettono solo visualizzazione e fork, non il riuso in un altro progetto. **Non si può copiare codice.**
- Creata il **2025-10-14** e tutta la storia (rinomine, upload via web, uno zip di sé stessa) è dello stesso giorno; 0 stelle, 0 fork. È un prototipo personale per le elezioni olandesi 2025, con dati StemWijzer e PDF del CPB.
- Stack: Python, Streamlit, Pydantic, Altair ([requirements.txt](https://github.com/ERRuijs/Stemwijzert/blob/main/requirements.txt)): richiede un server Python, incompatibile con un sito statico.
- Il README si riferisce a una repository diversa (`blind-party-ranking`) e a un demo "URL will be available after deployment".

Valore per elezio: solo la **idea di prodotto** (classificare proposte anonime, rivelare i partiti alla fine) e il metodo di punteggio, descritto nel docstring di `utils/scoring.py` (ranking a 3/2/1/0 punti con ripartizione equa dei pareggi) ([scoring.py](https://github.com/ERRuijs/Stemwijzert/blob/main/utils/scoring.py)). Una modalità cieca per elezio andrà scritta da zero, come già previsto dal ticket.

## 4. Electio Italia

Repository: https://github.com/Electio-org/italia

- **Nessuna licenza**: `license: null`; la descrizione della repository è "Private preview of a Election data platform for municipal results"; il README dice "This is a private working repository... Licensing and publication policy will be finalized before public launch" ([README](https://github.com/Electio-org/italia/blob/main/README.md)). Nessuna menzione di licenza in `index.html`, `usage-notes.html`, `data-download.html`, `docs/`. **Né il codice né il bundle di dati derivati sono riusabili senza accordo con l'autore** (Simone Ghezzi Colombo, [CITATION.cff](https://github.com/Electio-org/italia/blob/main/CITATION.cff), versione 0.25.0).
- Attività: creata il **2026-04-07**, 139 commit, ultimo push **oggi 2026-10-27**; a luglio 2026 ha aggiunto le europee comunali 1979-2024 e una tassonomia storica dei partiti. È in sviluppo molto attivo.
- Copertura dichiarata: Camera 1948-2022, Costituente 1946, Europee 1979-2024 a livello comunale, su geometria ISTAT 2021-12-31 con crosswalk delle fusioni; roadmap Senato, Regionali, Comunali, Referendum.
- Stack: JavaScript vanilla a moduli (`modules/*.js`), d3, PapaParse, topojson-client e Tabler vendorizzati; pipeline Python; smoke test Playwright ([package.json](https://github.com/Electio-org/italia/blob/main/package.json)). Repository da 683 MB; `municipality_results_long.csv` è 506 MB e le geometrie full sono su LFS, non servite da Pages.
- Fonte dei dati: open data Eligendo del Ministero dell'Interno. L'inventario di Electio cita per la licenza la direttiva PSI (D.lgs. 36/2006) e rimanda a `info_opendata.php` ([sources_inventory_extended.json](https://github.com/Electio-org/italia/blob/main/data/derived/sources_inventory_extended.json)); quella pagina, letta oggi, descrive le fonti ma **non dichiara una licenza esplicita** ([Eligendo info open data](https://elezionistorico.interno.gov.it/eligendo/info_opendata.php)).

Valore per elezio: per i risultati storici conviene **linkare il sito pubblico di Electio** (https://electio-org.github.io/italia/) e, se si vuole di più, **chiedere all'autore** una licenza sul bundle derivato o, in alternativa, partire dagli zip Eligendo con una pipeline propria. Nessun riuso di codice in v1.

## 5. Programmi Elettorali 2022

Repository: https://github.com/programmielettorali/programmielettorali.github.io e https://github.com/programmielettorali/programmi-elettorali-vuejs-code (è un account utente, non un'organizzazione: 2 repository pubbliche, create nell'agosto 2022).

### Licenza

- `programmielettorali.github.io`: `LICENSE` è il testo GPL **v2** ([LICENSE](https://github.com/programmielettorali/programmielettorali.github.io/blob/main/LICENSE)); non c'è alcuna intestazione "or any later version" nei sorgenti (l'unica occorrenza è nell'appendice standard del testo della licenza). Va trattata come **GPL-2.0-only**, che le FAQ GNU dichiarano incompatibile con GPLv3 e quindi con AGPLv3 (vedi sezione licenze).
- `programmi-elettorali-vuejs-code` (il sorgente): **nessuna licenza** (`license: null`, `GET .../license` 404).
- Ultimo push di entrambe: **2022-09-01**. Progetto concluso con le politiche 2022.

### Cosa contiene davvero

- **Nessun PDF.** L'albero della repository contiene solo `index.html`, un bundle Vue (vue-cli 5, Vue 3.2), un CSS, 23 immagini JPG "banner" di partiti/liste e `LICENSE`. I programmi sono **link esterni**.
- I dati sono in `src/database/PartyDb.json` (21 voci) e `ListeDb.json` (2 voci) della repository sorgente ([PartyDb.json](https://github.com/programmielettorali/programmi-elettorali-vuejs-code/blob/main/src/database/PartyDb.json)). Campi: `id`, `Slug`, `Nome`, `Tipo` (Partito / Lista / Coalizione), `Immagine`, `Collocazione` (Sinistra, Centro-Sinistra, Centro, Centro-Destra, Destra, Trasversale), `Lista`, `Componenti`, `Coalizione`, `Candidato`, `Programma` (URL). Soggetti: Alleanza Verdi Sinistra, Articolo Uno, Azione/Italia Viva, Cambiamo!, coalizione Centro Destra, Democratici e Progressisti, Europa Verde, Forza Italia, Fratelli d'Italia, Italia Sovrana e Popolare, Italexit, Lega, Movimento 5 Stelle, Noi Moderati, Partito Animalista Italiano, PSI, Più Europa, Possibile, Unione Popolare, Verde è Popolare, Vita.
- **Link rot verificato oggi** su 8 URL: rispondono 200 Lega (PDF), Fratelli d'Italia (PDF), coalizione centrodestra (PDF su ansa.it), M5S (pagina), AVS (pagina); 403 il PDF del PD; 404 Italexit e Possibile. Azione/Italia Viva punta a un Google Drive. Non è un archivio affidabile.
- **La scoperta utile**: tre link puntano all'archivio trasparenza del Ministero dell'Interno, `https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/<n>/...pdf` (Forza Italia n. 43, Noi Moderati n. 48, Fratelli d'Italia n. 68). È la pubblicazione ufficiale dei programmi depositati per le politiche 2022, fonte primaria e stabile (le due URL testate rispondono 200 con `application/pdf`). Per il 2027 è da verificare se il Ministero pubblicherà i programmi allo stesso modo: sarebbe la fonte da usare al posto dei siti di partito.

### Riuso

- Codice: no (GPL-2.0-only e sorgente senza licenza; comunque sono due componenti Vue da 5 KB).
- Dati: i 21 record sono fatti (nomi, collocazioni, URL) e non contengono testo creativo; conviene comunque **ricostruirli dalla fonte ministeriale** piuttosto che copiarli, anche per correggere i link morti. Le immagini banner sono materiale dei partiti: non riusarle.

## Compatibilità delle licenze con AGPL-3.0

| Repository | Licenza verificata | Compatibile con AGPL-3.0? | Fonte |
|---|---|---|---|
| Open Election Compass client | GPL-3.0 | Sì. GPLv3 §13 dà "permission to link or combine any covered work with a work licensed under version 3 of the GNU Affero General Public License into a single combined work"; AGPLv3 §13 contiene la previsione speculare. Le FAQ GNU: "Each of these licenses explicitly permits linking with code under the other license". | [GPLv3 §13](https://github.com/open-election-compass/client/blob/master/LICENSE), [AGPLv3 §13](https://github.com/github/choosealicense.com/blob/gh-pages/_licenses/agpl-3.0.txt), [GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html) |
| Mat-O-Wahl | GPL-3.0 | Sì, come sopra. | [LICENSE](https://github.com/msteudtn/Mat-O-Wahl/blob/master/LICENSE) |
| Stemwijzert | nessuna | No: copyright esclusivo per default. | [GitHub API](https://api.github.com/repos/ERRuijs/Stemwijzert), [choosealicense](https://choosealicense.com/no-permission/) |
| Electio Italia | nessuna, "private preview" | No, salvo accordo con l'autore. | [README](https://github.com/Electio-org/italia/blob/main/README.md) |
| Programmi Elettorali (sito) | GPL-2.0-only | No. FAQ GNU "Is GPLv3 compatible with GPLv2?": "No... the two licenses are not compatible"; la matrice vale anche per AGPLv3 ("Each place that the matrix states GPLv3, the same statement about compatibility is true for AGPLv3 as well"); GPLv2 §6 vieta "any further restrictions". | [LICENSE](https://github.com/programmielettorali/programmielettorali.github.io/blob/main/LICENSE), [GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html) |
| Programmi Elettorali (sorgente) | nessuna | No. | [GitHub API](https://api.github.com/repos/programmielettorali/programmi-elettorali-vuejs-code/license) |

Obblighi pratici se si include OEC (o Mat-O-Wahl):

- la parte GPL-3.0 resta GPL-3.0 (GPLv3 §13: "The terms of this License will continue to apply to the part which is the covered work"); non si può ri-licenziare OEC sotto AGPL, ma la combinazione è lecita;
- nel sito vanno mantenuti il testo della GPLv3 e il copyright di Till Sanders/OEC, e va indicato dove sta il sorgente (è sufficiente il link a GitHub/npm se il file non è modificato);
- eventuali modifiche a OEC vanno pubblicate con sorgente sotto GPL-3.0 (un fork pubblico su GitHub basta);
- AGPLv3 §13 richiede di offrire il sorgente corrispondente agli utenti che interagiscono via rete: per un sito statico con repository pubblica è già soddisfatto da un link "codice sorgente" nel footer.

## Tabella comparativa

| | Open Election Compass | Mat-O-Wahl | Stemwijzert | Electio Italia | Programmi Elettorali 2022 |
|---|---|---|---|---|---|
| Licenza | GPL-3.0 | GPL-3.0 | nessuna | nessuna (preview privata) | GPL-2.0-only; sorgente senza licenza |
| Compatibile AGPL-3.0 | sì | sì | no | no | no |
| Ultimo commit | 2025-07-16 (prima: 2022-08) | 2026-09-06 | 2025-10-14 (unico giorno) | 2026-10-27 | 2022-09-01 |
| Ultima release | v2.0.0-alpha.5, 2022-08-27 | 0.6.0.11, 2025-04-06 | nessuna | bundle 0.25.0 (CITATION.cff) | nessuna |
| Issue aperte | 32 (6 PR bot) | 21 | 0 | 0 | 0 |
| Stack | Vue 3 + Vite, bundle UMD autonomo | jQuery 3.4 + Bootstrap 4, nessun build | Python/Streamlit | JS vanilla + d3, pipeline Python | Vue 3 (vue-cli) |
| Dati | JSON (editor online) | 2 CSV + definition.js | JSON + PDF CPB | CSV/JSON derivati da Eligendo, 683 MB | 21 record JSON con URL |
| Scoring | matrice configurabile, 3 o 5 risposte, peso x2, skip | match 1 / neutro 0,5, peso x2, skip | ranking cieco 3/2/1/0 | n/a | n/a |
| Italiano | sì, completo | no (de, en) | no | sì | sì |
| Integrazione in sito statico | 1 script + 1 div + JSON, o iframe | solo iframe | no (server Python) | link al sito pubblico | n/a |
| Vincolo di stack per elezio | nessuno | nessuno | n/a | n/a | n/a |
| Riuso in v1 | quiz + scoring + i18n + editor + formato dati | piano B per il quiz | nessuno (ispirazione) | nessuno (link) | nessuno (fonte ministeriale al suo posto) |
| Rischio principale | manutenzione quasi ferma, toolchain 2022, alpha | codice legacy, UI datata | nessuna licenza | nessuna licenza, repo in flusso | link morti, GPL-2.0 |

## Raccomandazione

**Riusare Open Election Compass come componente quiz, montato via bundle UMD in una pagina dedicata di un sito statico.** Motivi:

1. Risolve la domanda del ticket nel senso favorevole: nessun vincolo Vue/Nuxt sull'app. Il quiz vive in `/quiz/` (o in un iframe) e il resto di elezio può usare qualunque SSG; lo stack si sceglie sugli altri requisiti (programmi, confronto, risultati, finanziamenti).
2. Copre da solo quiz, scoring, pesi, skip, confronto tesi per tesi, italiano, editor di configurazione e guida metodologica: in un budget di circa 130 ore è la voce più grossa che si evita di scrivere.
3. La licenza è pulita rispetto ad AGPL-3.0.
4. Il formato JSON di OEC diventa il contratto fra la redazione e il quiz; è generabile dalla pipeline dati e verificabile con l'editor online.

Condizioni:

- Self-hostare `open-election-compass.umd.min.js` versione `2.0.0-alpha.5` (pinnata, con hash) e non dipendere da unpkg; registrare in un ADR che si usa una alpha ferma al 2022 e che il piano in caso di bug è forkare.
- Tenere `friends` e `analysis` disattivati.
- Isolare il CSS (pagina dedicata senza altri componenti, o iframe).
- Non tentare né la via Nuxt né la ricompilazione dal sorgente in v1.

**Piano B: Mat-O-Wahl** in iframe, se in fase di prototipo l'aspetto o il flusso di OEC risultassero inaccettabili e non modificabili senza fork. Costo: tradurre `i18n_it.js`, convertire i dati in CSV, accettare jQuery/Bootstrap 4 e l'iframe. Stessa licenza.

**Scartati per v1**: Stemwijzert (nessuna licenza, stack server; tenere come riferimento di prodotto per la modalità cieca), Electio Italia (nessuna licenza; linkare il sito, eventualmente chiedere una licenza sui dati derivati per v2), Programmi Elettorali 2022 (GPL-2.0 incompatibile, nessun PDF, link in parte morti; usare invece l'archivio trasparenza del Ministero dell'Interno come fonte dei programmi).

## Correzioni alla ricerca precedente

`ricerca/repository_open_source_politica_italiana.md` va aggiornata su questi punti:

- OEC: "versione 1.0 ancora in sviluppo" è la frase del README, ma la versione reale è 2.0.0-alpha.5 (2022); l'attività è ferma salvo un intervento nel 2025. La ricerca non segnalava che OEC è distribuito come bundle UMD autonomo, che è il fatto decisivo per lo stack.
- Mat-O-Wahl: "possibilità di incorporamento" significa solo iframe; mancano le lingue (niente italiano).
- Stemwijzert: non ha licenza; non lo si può riusare.
- Electio Italia: "oltre 130 commit e aggiornamenti recenti" è corretto, ma manca il punto essenziale: nessuna licenza e repository dichiarata preview privata.
- Programmi Elettorali 2022: la ricerca lasciava intendere un archivio di programmi; in realtà non ospita PDF, ha 21 record con link esterni in parte morti ed è GPL-2.0.

## Fonti consultate

Open Election Compass
- https://github.com/open-election-compass/client (metadati, commit, release, issue via API GitHub)
- https://github.com/open-election-compass/client/blob/master/package.json
- https://github.com/open-election-compass/client/blob/master/vite.config.ts
- https://github.com/open-election-compass/client/blob/master/src/main.ts
- https://github.com/open-election-compass/client/blob/master/src/OpenElectionCompass.vue
- https://github.com/open-election-compass/client/blob/master/src/nuxtModule.js
- https://github.com/open-election-compass/client/blob/master/src/bootstrap/loadOpenElectionCompassUI.ts
- https://github.com/open-election-compass/client/blob/master/src/store/modules/parties/calculatePointsForParty.js
- https://github.com/open-election-compass/client/blob/master/src/store/modules/theses/theses.js
- https://github.com/open-election-compass/client/blob/master/src/store/modules/algorithm/algorithms/cityblock/approve-neutral-reject.js
- https://github.com/open-election-compass/client/blob/master/src/store/modules/algorithm/algorithms/hybrid/hybrid.js
- https://github.com/open-election-compass/client/blob/master/src/store/modules/analysis/analysis.js
- https://github.com/open-election-compass/client/blob/master/src/store/modules/friends/plugin.js
- https://github.com/open-election-compass/client/blob/master/src/locales/it.json
- https://github.com/open-election-compass/client/blob/master/public/index.html
- https://github.com/open-election-compass/client/blob/master/public/demo-luedenscheid.html
- https://github.com/open-election-compass/client/blob/master/.github/workflows/pages.yml
- https://github.com/open-election-compass/client/blob/master/.github/workflows/npm.yml
- https://github.com/open-election-compass/client/blob/master/LICENSE
- https://github.com/open-election-compass/client/issues/73
- https://registry.npmjs.org/@open-election-compass/client
- https://registry.npmjs.org/@open-election-compass/ui
- https://unpkg.com/browse/@open-election-compass/client@2.0.0-alpha.5/dist/
- https://unpkg.com/@open-election-compass/client@2.0.0-alpha.5/dist/open-election-compass.umd.min.js
- https://unpkg.com/@open-election-compass/client@1.0.0-beta.13/package.json
- https://open-election-compass.com/guide/technical/deployment.html
- https://open-election-compass.com/guide/technical/overview.html

Mat-O-Wahl
- https://github.com/msteudtn/Mat-O-Wahl (metadati, commit, release, tag, issue via API GitHub)
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/readme.md
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/LICENSE
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/index.html
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/data/definition.js
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/data/Obsthausen_Fragen.csv
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/data/Obsthausen_Parteien.csv
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/system/general.js
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/system/changelog.md
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/extras/readme.md
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/i18n/i18n_en.js
- https://github.com/msteudtn/Mat-O-Wahl/blob/master/Dockerfile

Stemwijzert
- https://github.com/ERRuijs/Stemwijzert (metadati, commit, albero via API GitHub)
- https://github.com/ERRuijs/Stemwijzert/blob/main/README.md
- https://github.com/ERRuijs/Stemwijzert/blob/main/utils/scoring.py
- https://github.com/ERRuijs/Stemwijzert/blob/main/requirements.txt

Electio Italia
- https://github.com/Electio-org/italia (metadati, commit, albero via API GitHub)
- https://github.com/Electio-org/italia/blob/main/README.md
- https://github.com/Electio-org/italia/blob/main/CITATION.cff
- https://github.com/Electio-org/italia/blob/main/package.json
- https://github.com/Electio-org/italia/blob/main/llms.txt
- https://github.com/Electio-org/italia/blob/main/docs/README.md
- https://github.com/Electio-org/italia/blob/main/docs/SOURCES_INVENTORY.md
- https://github.com/Electio-org/italia/blob/main/docs/methodology.md
- https://github.com/Electio-org/italia/blob/main/data/derived/usage_notes.json
- https://github.com/Electio-org/italia/blob/main/data/derived/sources_inventory_extended.json
- https://elezionistorico.interno.gov.it/eligendo/info_opendata.php

Programmi Elettorali 2022
- https://github.com/programmielettorali/programmielettorali.github.io (metadati, commit, albero via API GitHub)
- https://github.com/programmielettorali/programmielettorali.github.io/blob/main/LICENSE
- https://github.com/programmielettorali/programmielettorali.github.io/blob/main/index.html
- https://github.com/programmielettorali/programmielettorali.github.io/blob/main/js/app.93416542.js
- https://github.com/programmielettorali/programmi-elettorali-vuejs-code
- https://github.com/programmielettorali/programmi-elettorali-vuejs-code/blob/main/src/database/PartyDb.json
- https://github.com/programmielettorali/programmi-elettorali-vuejs-code/blob/main/src/database/ListeDb.json
- https://github.com/programmielettorali/programmi-elettorali-vuejs-code/blob/main/package.json
- https://dait.interno.gov.it/documenti/trasparenza/POLITICHE_20220925/Documenti/68/(68_progr_2_)-programma.pdf (verifica 200)

Licenze
- https://www.gnu.org/licenses/gpl-faq.en.html (voci "Is GPLv3 compatible with GPLv2?", combinazione AGPLv3/GPLv3, matrice di compatibilità)
- https://github.com/github/choosealicense.com/blob/gh-pages/_licenses/agpl-3.0.txt (AGPLv3 §13)
- https://github.com/github/choosealicense.com/blob/gh-pages/_licenses/gpl-2.0.txt (GPLv2 §6)
- https://choosealicense.com/no-permission/
