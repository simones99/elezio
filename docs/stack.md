# Stack tecnico di v1: vista operativa

Ultimo aggiornamento: 27 ottobre 2026. Decisioni di fondo in [ADR 0006](adr/0006-stack-tecnico-v1.md); deciso nel ticket [Stack tecnico di v1](https://github.com/simones99/elezio/issues/7). Questo file cambia quando cambiano versioni, comandi o configurazione.

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
    │   └── loghi/
    └── tests/smoke.spec.ts
```

Astro legge `../contenuti` con il loader `glob` del content layer; nessun file di dati vive in `sito/`.

## Strumenti e versioni

- Node LTS corrente, pnpm. Versioni fissate in `sito/package.json` e `.nvmrc`.
- Astro, ultima major stabile al momento dello scaffolding. Nessun framework UI; isole in TypeScript vanilla.
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

1. `pipeline.yml` (su `contenuti/**`, `pipeline/**`): clona `elezio-fonti` con un token di sola lettura, esegue `pipeline verifica`.
2. `sito.yml` (su `sito/**`, `contenuti/**`): `pnpm install --frozen-lockfile`, `astro check`, `astro build`, `lychee` sui link interni del build, Playwright con un solo test che apre home, una scheda, un confronto e `/quiz/` e verifica che Open Election Compass si sia montato.

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
