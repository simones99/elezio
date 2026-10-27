---
status: accepted
date: 2026-10-27
---

# Stack tecnico di v1: Astro in monorepo, Cloudflare Pages, quiz in pagina dedicata, confronti pre-renderizzati

Lo stack segue il componente più grosso riusato, e l'audit (ticket [Audit delle repository open source candidate al riuso](https://github.com/simones99/elezio/issues/2)) ha stabilito che Open Election Compass è un bundle UMD che si monta da solo e non impone nulla al resto del sito. Lo stack è quindi libero e si sceglie per chi lo manterrà: una persona con circa 5 ore a settimana e agenti AI.

**Il sito è Astro, in un monorepo con pipeline e contenuti.** `sito/` (Astro), `pipeline/` (Python), `contenuti/` (dati), `docs/`. Astro legge `contenuti/` direttamente con il content layer: i Markdown con frontmatter e i YAML hanno uno schema zod che la build applica, non esistono copie dei dati. Zero JavaScript di default, isole solo dove serve interattività. Astro è scelto perché struttura i dati con schemi, perché agenti e documentazione lo conoscono bene, e perché non vincola a un framework UI.

**Due validatori, nessuna regola duplicata.** Lo schema zod valida forma e coerenza interna dei file (campi, enum, slug uguali alle cartelle). `pipeline verifica` in Python controlla solo ciò che richiede il repo privato o incroci tra file: citazioni nel testo estratto, 300 parole, fonte che include il partito, una scheda per tripla.

**Hosting su Cloudflare Pages.** Gratuito, dominio proprio, header HTTP configurabili per la CSP, anteprima per ogni PR, deploy da GitHub Actions solo da `main`. Il sito non tratta dati personali, quindi la residenza dell'hosting pesa meno di quella dell'analytics, che è in UE (GoatCounter hosted gira su Hetzner in Finlandia e Germania, operatore in Irlanda).

**Il quiz vive in una pagina dedicata, non in un iframe.** `/quiz/` è una pagina Astro senza il layout del sito, che carica il bundle UMD di Open Election Compass self-hostato e il JSON di configurazione inline. Il bundle non si carica su nessun'altra pagina. Il JSON lo genera Astro in build da `contenuti/`: Python non produce dati per il sito.

**I confronti sono pagine pre-renderizzate.** Per ogni tema una pagina per ogni coppia di partiti, con URL condivisibile; il terzo partito si aggiunge via query string da un'isola minima. Ogni confronto è leggibile senza JavaScript.

**CSS puro e vendorizzazione totale.** Stili scoped di Astro più un file di token, mobile-first, nessun framework CSS o UI. Nessuna risorsa da CDN esterni: la CSP ammette `'self'` più il dominio di GoatCounter.

## Considered options

- Nuxt o Vue per adottare Open Election Compass nativamente: scartato perché il modulo Nuxt del pacchetto è rotto e il bundle UMD non lo richiede.
- Eleventy: scartato perché non offre schemi sui dati, che qui sostituiscono una parte dei test.
- Hugo: scartato perché i template Go sono meno leggibili per gli agenti e il resto della toolchain è già Node per Open Election Compass.
- GitHub Pages: scartato perché non permette header HTTP (CSP) né anteprime per PR.
- Hosting in UE (Bunny.net, Codeberg Pages): non scartato, resta l'alternativa se si vuole coerenza con la scelta di inferenza in UE; non scelto per la semplicità di Cloudflare Pages.
- Quiz in iframe: scartato perché genera doppio scroll su mobile e una pagina dedicata isola già il CSS.
- Confronto interamente lato client da un JSON per tema: scartato perché senza JavaScript non si vede nulla e gli URL non sarebbero condivisibili.
- Tailwind o un framework UI: scartati perché il sito ha poche pagine tipo e i token bastano.
- JSON per il quiz generato dalla pipeline Python: scartato perché avrebbe due lettori dei contenuti.

## Consequences

Il repo ha due toolchain (pnpm e Python) con CI separate per percorso. Tutte le pagine di confronto sono statiche: 45 coppie per 12 temi nel 2022, il doppio quando si aggiungono le schede 2027. Il prototipo UI (ticket aperto) decide l'aspetto, non lo stack. Il ticket sul quiz deve stabilire il formato delle affermazioni e il modo di agganciare l'evento "quiz completato" a Open Election Compass. Dettagli operativi (layout delle cartelle, CI, CSP, comandi) in `docs/stack.md`.
