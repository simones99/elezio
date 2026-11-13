# Stack tecnico di v1: vista operativa

Ultimo aggiornamento: 13 novembre 2026. Decisioni di fondo in [ADR 0006](adr/0006-stack-tecnico-v1.md); deciso nel ticket [Stack tecnico di v1](https://github.com/simones99/elezio/issues/7). Questo file cambia quando cambiano versioni, comandi o configurazione.

## Layout del repo

```
elezio/
├── contenuti/            # dati: temi, partiti, fonti, schede, quiz (vedi docs/schema-scheda.md)
├── docs/                 # vision, roadmap, ADR, schemi
├── pipeline/             # Python standalone (vedi docs/pipeline.md)
└── sito/                 # Astro
    ├── src/
    │   ├── content.config.ts   # collezioni con loader glob su ../contenuti, schemi zod
    │   ├── layouts/
    │   ├── pages/
    │   │   ├── index.astro
    │   │   ├── temi/[tema].astro
    │   │   ├── partiti/[partito].astro
    │   │   ├── confronto/[tema]/[coppia].astro
    │   │   ├── quiz/index.astro         # pagina dedicata, senza layout del sito
    │   │   ├── quiz/config.json.ts      # endpoint statico: JSON per Open Election Compass
    │   │   ├── metodologia.astro
    │   │   └── crediti.astro
    │   └── styles/tokens.css
    ├── public/
    │   ├── vendor/open-election-compass.umd.min.js   # self-hostato, versione fissata
    │   ├── _headers                                 # CSP e header per Cloudflare Pages
    │   └── fonts/                                   # Cinzel e Archivo, con le licenze OFL
    └── tests/
        ├── smoke.spec.ts
        └── contenuti-prova/                         # contenuti finti per il test di fumo
```

Astro legge `../contenuti` con i loader `glob` e `file` del content layer; nessun dato pubblicato vive in `sito/`, che ha solo i contenuti inventati dei test (`tests/contenuti-prova/`). I contrassegni stanno accanto ai file dei partiti, in `contenuti/partiti/loghi/`, e il campo `logo` li indica con un percorso relativo (`./loghi/m5s.png`): la build fallisce se il file manca.

Con la variabile `ELEZIO_CONTENUTI` (percorso relativo a `sito/`) il sito si costruisce da un'altra cartella, con build e cache separate (`dist-prova/`, `node_modules/.astro-prova/`). La usano i test: `tests/contenuti-prova/` ha tre partiti inventati con una scheda verificata, una assente e una bozza, casi che i contenuti veri non hanno ancora.

## Strumenti e versioni

- Node 26 (LTS corrente), pnpm 11. Versioni fissate in `sito/package.json` (`packageManager`, versioni esatte) e `sito/.nvmrc`.
- Astro 7.4, scaffolding del 13 novembre 2026. Nessun framework UI; isole in TypeScript vanilla.
- TypeScript 6: `astro check` non supporta ancora TypeScript 7.
- Playwright con il solo Chromium, viewport da telefono (390 px) e JavaScript spento.
- Open Election Compass: pacchetto `@open-election-compass/client` 2.0.0-alpha.5, file `dist/open-election-compass.umd.min.js` copiato in `public/vendor/` con la versione nel nome del file e la licenza GPL-3.0 in `CREDITS.md`. Modalità "friends" spenta.
- Python 3.12 o successivo per `pipeline/` (vedi `docs/pipeline.md`).

## Collezioni e schemi

| Collezione | Sorgente | Schema |
| --- | --- | --- |
| `temi` | `contenuti/temi.yaml` | id, nome, definizione, sotto_questioni, dentro, altrove |
| `partiti` | `contenuti/partiti/*.yaml` | campi di `docs/schema-scheda.md` |
| `fonti` | `contenuti/fonti/*.yaml` | campi di `docs/schema-scheda.md` |
| `schede` | `contenuti/schede/**/*.md` | frontmatter di `docs/schema-scheda.md`; slug di partito, tema ed elezione coerenti con il percorso |
| `affermazioni` | `contenuti/quiz/<elezione>/*.yaml` | campi di `docs/quiz.md` |

Lo schema zod rifiuta la build su campi mancanti, enum sbagliati, slug non coerenti, `posizione: dichiarata` senza citazioni, `posizione: assente` con titolo. I controlli che richiedono il repo privato o incroci tra file stanno in `pipeline verifica`.

## Pagine

- Home, elenco temi, pagina tema con le schede di tutti i partiti, pagina partito con le sue 12 schede, confronto, quiz, risultato del quiz (dentro Open Election Compass), metodologia, crediti, privacy.
- Confronto: `/confronto/<tema>/<a>-<b>/` con gli slug in ordine alfabetico, 45 coppie per tema. Il selettore dei partiti è un'isola che cambia URL. Terzo partito: `?terzo=<slug>`, letto da un'isola che carica la scheda da `/dati/<tema>.json` (endpoint statico).
- Quiz: `/quiz/` senza layout del sito; `<div id="open-election-compass">`, tag `<open-election-compass load-tag="#config">`, JSON inline generato da `quiz/config.json.ts`. Il bundle è caricato solo qui.
- Schede in stato `bozza` non vengono renderizzate; `contestata` sì, con avviso.

## CI (GitHub Actions)

Su ogni PR, due workflow filtrati per percorso:

1. `pipeline.yml` (su `contenuti/**`, `pipeline/**`): esegue i test della pipeline, poi clona `elezio-fonti` con un token di sola lettura ed esegue `pipeline verifica`.
2. `sito.yml` (su `sito/**`, `contenuti/**`): `pnpm install --frozen-lockfile`, `astro check`, `astro build` sui contenuti veri, `lychee` offline sui link interni del build, Playwright sui contenuti di prova. Oggi il test di fumo apre la home e la pagina tema e controlla schede, citazioni, assenza, bozza nascosta e niente scorrimento orizzontale; confronto e `/quiz/` (con Open Election Compass montato) si aggiungono con i loro ticket.

Il filtro per percorso sta dentro ogni workflow (job `percorsi toccati` in `pipeline.yml`, `percorsi toccati dal sito` in `sito.yml`), non in `on.pull_request.paths`: un controllo richiesto dalla protezione di `main` che non parte resterebbe in attesa e bloccherebbe la PR, mentre un job saltato vale come superato.

`sito.yml` ha il job `build del sito`, con Node da `sito/.nvmrc` e permessi `contents: read`; se Playwright fallisce carica `test-results/` come artefatto.

`pipeline.yml` ha due job, entrambi con Python 3.12 e permessi `contents: read`:

- `test della pipeline`: `python -m pytest` da `pipeline/` e `pipeline verifica` sul solo schema di fonti e schede. Non ha bisogno di secret, quindi gira anche sulle PR da fork.
- `verifica delle citazioni`: clona `pdf/` e `testo/` di `elezio-fonti` accanto al repo ed esegue `pipeline verifica` completa (hash dei PDF, citazioni nel testo estratto).

### Token di `elezio-fonti`

`verifica delle citazioni` dipende dal secret `ELEZIO_FONTI_TOKEN` del repo `elezio`: un fine-grained personal access token limitato al solo repo `simones99/elezio-fonti`, con il solo permesso Contents in lettura. Lo inserisce il maintainer (Settings, Secrets and variables, Actions) e lo rinnova alla scadenza. Il token passa solo all'azione `actions/checkout`, che lo maschera nei log e con `persist-credentials: false` non lo lascia nella configurazione di git; nessuno script lo riceve.

Senza il secret il job fallisce con un messaggio esplicito invece di ripiegare sul solo schema: la verifica delle citazioni non resta mai saltata senza che si veda. Vale anche per le PR da fork, a cui GitHub non passa i secret.

Deploy: Cloudflare Pages collegato al repo, build da `main`, anteprima per ogni PR. Nessun unit test sul sito in v1.

## Header e analytics

`public/_headers`:

```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' https://gc.zgo.at; img-src 'self' https://<codice>.goatcounter.com; connect-src 'self' https://<codice>.goatcounter.com; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

Lo `'unsafe-inline'` per gli stili è richiesto dagli stili scoped di Astro; da rivedere se Astro offre nonce. Script GoatCounter solo in produzione (variabile d'ambiente di build), evento `quiz-completato` inviato con `window.goatcounter.count`; il modo di intercettare la fine del quiz in Open Election Compass lo decide il ticket sul quiz. GoatCounter hosted: server Hetzner in Finlandia e Germania, operatore in Irlanda (privacy policy letta il 27 ottobre 2026).

## Fuori dallo stack v1

Ricerca full-text, service worker, ottimizzazione immagini oltre i loghi, i18n, librerie grafici. Hosting alternativo in UE (Bunny.net o Codeberg Pages) resta possibile senza cambiare la build: il sito è una cartella statica.
