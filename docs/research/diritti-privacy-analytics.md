# Diritti su loghi, PDF e citazioni; analytics senza cookie

Ticket: https://github.com/simones99/elezio/issues/4

Data della ricerca: 2026-10-27. Fonti consultate direttamente (normattiva.it, garanteprivacy.it, edpb.europa.eu, agcom.it, dait.interno.gov.it, documentazione ufficiale di Plausible, Umami, Cloudflare, GoatCounter, testi delle licenze). Chi scrive non è un avvocato: le regole qui sotto sono prudenziali e vanno lette insieme alla sezione finale "Da verificare con un legale".

Contesto assunto: sito statico, codice AGPL-3.0, dati del progetto CC-BY-SA 4.0 (ipotesi), nessun backend, quiz calcolato nel browser senza salvare risposte, un solo manutentore, budget sotto 20 euro al mese, taglio informativo e non partigiano.

## Sintesi

1. Loghi e contrassegni: si possono mostrare per identificare partiti e liste, a patto di non alterarli, non usarli come elementi del brand di elezio e non lasciar intendere un'approvazione. Vanno esclusi esplicitamente dalla licenza CC-BY-SA del repo.
2. PDF dei programmi: non ridistribuirli nel repo. Linkare la copia ufficiale pubblicata dal Ministero dell'Interno nella sezione "Elezioni trasparenti" e il sito del partito; conservare solo hash, data e link di archivio.
3. Citazioni: brevi, con finalità di confronto e discussione, sempre con partito, titolo del programma, anno e pagina. Il testo integrale non si ripubblica.
4. Dati del progetto: la CC-BY-SA copre solo ciò che elezio crea (sintesi, classificazioni, struttura dei dati). Citazioni e loghi restano dei rispettivi titolari e vanno marcati come tali.
5. Quiz nel browser: nessun consenso richiesto se non si salva nulla fuori dal dispositivo. Serve comunque un'informativa breve, perché l'hosting registra gli IP. Niente banner se non ci sono cookie o strumenti equivalenti.
6. Il risultato del quiz è un'opinione politica (dato particolare, art. 9 GDPR): non va mai inviato a servizi terzi, neppure come proprietà di un evento analytics.
7. Analytics: scelta consigliata GoatCounter in hosting (gratuito, UE, senza cookie, eventi supportati). Alternativa a pagamento Plausible Cloud Starter (9 $/mese, UE). Cloudflare Web Analytics non conta eventi; Umami Cloud è gratuito ma la catena di fornitori è prevalentemente statunitense.
8. Par condicio: la legge 28/2000 e i regolamenti AGCOM si applicano a emittenti radiotelevisive e stampa; un sito informativo non è destinatario. Resta il divieto generale di diffondere sondaggi nei 15 giorni prima del voto: elezio non deve pubblicare aggregati del quiz presentabili come orientamenti di voto.

## 1. Loghi e contrassegni dei partiti

Cosa dice la legge.

- Il diritto di marchio consente al titolare di vietare l'uso di un segno identico o simile "nell'attività economica" (art. 20, c. 1, Codice della proprietà industriale, d.lgs. 30/2005). L'art. 21 elenca le limitazioni: uso descrittivo e referenziale sono consentiti se conformi ai principi della correttezza professionale; resta vietato l'uso che crea confusione, inganna il pubblico o lede diritti altrui (art. 21, c. 2). Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-02-10;30~art20 e https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-02-10;30~art21
- Un logo è anche un'opera grafica tutelata dal diritto d'autore (art. 2 l. 633/1941). La sua riproduzione su un sito informativo rientra nel diritto di citazione (art. 70, vedi sezione 3) se serve alla discussione e non fa concorrenza allo sfruttamento economico dell'opera.
- I contrassegni depositati per le elezioni politiche sono pubblicati dal Ministero dell'Interno nella sezione "Elezioni trasparenti" entro dieci giorni dalla scadenza del deposito, con lo statuto o la dichiarazione di trasparenza e il programma elettorale (art. 4 l. 165/2017). Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2017-11-03;165~art4 e https://dait.interno.gov.it/elezioni/trasparenza
- La legge sul diritto d'autore non si applica ai "testi degli atti ufficiali dello Stato e delle Amministrazioni pubbliche" (art. 5 l. 633/1941). La pubblicazione ministeriale è un atto ufficiale, ma il contrassegno e il programma restano opere del partito allegate a quell'atto: non si può dare per scontato che diventino liberi. Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art5

Regole operative.

1. Mostrare il contrassegno solo per identificare la lista, nella forma depositata, senza modifiche di colore, proporzioni o ritaglio. Fonte: art. 21, c. 2, CPI (divieto di uso ingannevole o confusorio).
2. Non usare loghi di partito nel logo, nelle icone, nelle anteprime social o nel materiale promozionale di elezio. L'uso deve restare referenziale ("questo è il programma di X"), mai associativo. Fonte: art. 20 e 21 CPI; principio di non partigianeria del progetto.
3. Mettere i file dei loghi in una cartella separata con un README che dichiara: "contrassegni dei rispettivi partiti, riprodotti a fini identificativi e informativi; esclusi dalla licenza CC-BY-SA 4.0 del progetto". La CC-BY-SA non concede diritti di marchio né può licenziare ciò che il licenziante non possiede (sez. 2.b.2 della licenza). Fonte: https://creativecommons.org/licenses/by-sa/4.0/legalcode.it
4. Preferire la versione pubblicata su "Elezioni trasparenti" come fonte, e annotarla accanto a ogni file (URL, data di prelievo). È la copia ufficialmente depositata e offre parità di trattamento tra liste.
5. Rimuovere o sostituire un logo su richiesta motivata del titolare, senza discutere: il costo di un contenzioso supera il valore dell'immagine per un progetto volontario.
6. Prevedere un'alternativa testuale (nome della lista) ovunque il logo compaia, così che la rimozione di un'immagine non rompa il sito.

## 2. PDF dei programmi: ridistribuire o linkare

Cosa dice la legge.

- Il programma elettorale è un'opera dell'ingegno del partito. La riproduzione integrale non rientra nell'art. 70, che copre "riassunto, citazione o riproduzione di brani o di parti di opera", nei limiti giustificati dal fine di critica o discussione e purché non costituisca concorrenza all'utilizzazione economica dell'opera. Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art70
- Il deposito del programma al Ministero dell'Interno è obbligatorio (art. 14-bis DPR 361/1957, come riportato dal dossier della Camera sulle politiche 2022) e il Ministero lo pubblica in "Elezioni trasparenti" (art. 4 l. 165/2017). Fonti: https://www.camera.it/temiap/documentazione/temi/pdf/1344756.pdf e https://dait.interno.gov.it/elezioni/trasparenza
- L'estrazione di testo e dati da opere legittimamente accessibili è consentita a chiunque, salvo riserva espressa del titolare, con conservazione delle copie "per il tempo necessario" all'estrazione (art. 70-quater l. 633/1941, introdotto dal d.lgs. 177/2021). Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art70quater

Regole operative.

1. Non committare i PDF integrali dei programmi nel repo e non servirli dal sito. Linkare la copia su "Elezioni trasparenti" e, quando esiste, la pagina del partito.
2. Per ogni programma registrare nei dati: URL ufficiale, URL del partito, data di prelievo, hash SHA-256 del file, link a una copia di archivio (Wayback Machine). Così il progetto resta verificabile anche se il file sparisce, senza ospitarlo.
3. Il testo estratto dai PDF serve per lavorare (classificare, cercare, citare) e non va pubblicato integralmente: l'art. 70-quater copre l'estrazione, non la ripubblicazione. Se si vuole tenerlo nel repo per riproducibilità, va messo in una cartella non pubblicata dal sito e con avviso di licenza (vedi sezione 4). Punto da verificare con un legale, perché "per il tempo necessario" mal si concilia con un archivio git permanente.
4. Se un partito pubblica il programma con una licenza aperta (succede di rado), annotarla nei dati: in quel caso la ridistribuzione diventa possibile per quel singolo documento.
5. Chiedere il permesso scritto al partito solo se si vuole davvero ospitare il PDF. Senza risposta, vale la regola 1.

## 3. Citazioni testuali

Cosa dice la legge.

- Art. 70, c. 1, l. 633/1941: riassunto, citazione e riproduzione di brani sono liberi "per uso di critica o di discussione, nei limiti giustificati da tali fini e purché non costituiscano concorrenza all'utilizzazione economica dell'opera". Il c. 3 impone di indicare sempre titolo dell'opera, autore ed editore quando risultano dall'originale. Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art70
- Art. 65: gli articoli di attualità di carattere economico, politico o religioso possono essere riprodotti in altri giornali, anche telematici, salvo riserva espressa, con indicazione di fonte, data e autore. Art. 66: i discorsi su argomenti di interesse politico tenuti in pubblico possono essere riprodotti "nei limiti giustificati dallo scopo informativo" in riviste e giornali anche telematici, citando fonte, autore, data e luogo. Fonti: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art65 e https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art66
- La legge non fissa un numero massimo di parole. Il limite è funzionale: quanto basta a discutere e confrontare.

Regole operative.

1. Ogni citazione dal programma riporta: partito o lista, titolo del documento, anno, pagina, link alla fonte. Formato suggerito: "Partito X, Programma elettorale 2027, p. 12". Fonte: art. 70, c. 3.
2. Una citazione deve essere incorniciata da contenuto proprio (sintesi, confronto per tema, nota di contesto). La pagina non può essere una sequenza di brani incollati. Fonte: art. 70, c. 1 ("critica o discussione").
3. Limite prudenziale: per ogni tema e per ogni partito, poche frasi (indicativamente non oltre 300 parole complessive per scheda tematica di partito), e mai un capitolo intero. Il numero non è di legge: serve a restare dentro "i limiti giustificati".
4. Citare testualmente, senza modificare il testo. Le omissioni si segnalano con parentesi quadre. Questo tutela anche dall'accusa di travisamento, più pericolosa del copyright per un sito non partigiano.
5. Le sintesi vanno scritte in parole proprie, con rimando alla pagina. Una parafrasi stretta di lunghi tratti è una riproduzione mascherata.
6. Per discorsi pubblici e dichiarazioni (comizi, interviste) valgono gli art. 65 e 66: riproducibili nei limiti informativi, sempre con fonte, data e luogo.

## 4. Licenza dei dati del progetto

Cosa dicono le licenze.

- CC-BY-SA 4.0 licenzia diritto d'autore e diritto sui generis sulle banche dati (sez. 1 e 4). Chi applica la licenza deve possedere i diritti necessari; non copre marchi, brevetti, diritti morali né diritti di terzi (sez. 2.b). Chi riutilizza deve attribuire, indicare le modifiche e rilasciare le elaborazioni con la stessa licenza (sez. 3.a e 3.b). Fonte: https://creativecommons.org/licenses/by-sa/4.0/legalcode.it
- AGPL-3.0 si applica al "Programma" (software e "other kinds of works", preambolo). La sez. 13 obbliga chi modifica il programma e lo fa usare via rete a offrire il sorgente corrispondente. Non è pensata per dataset e testi. Fonte: https://www.gnu.org/licenses/agpl-3.0.html (testo verificato sul file LICENSE.md del repo plausible/analytics, identico)
- Il diritto sui generis sulle banche dati (art. 102-bis l. 633/1941) nasce quando il costitutore ha fatto investimenti rilevanti; dura 15 anni e vieta estrazione e reimpiego di parti sostanziali. Vale per elezio come costitutore, non per i programmi dei partiti (che non sono banche dati). Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1941-04-22;633~art102bis

Regole operative.

1. Dichiarare tre regimi distinti nel README e in un file LICENSE-DATA: codice AGPL-3.0; dati originali di elezio (sintesi, classificazioni tematiche, domande e pesi del quiz, struttura e metadati) CC-BY-SA 4.0; citazioni, loghi e contrassegni dei rispettivi titolari, riprodotti ai sensi degli art. 70, 65 e 66 l. 633/1941 ed esclusi dalla licenza CC.
2. Nei file dati separare in campi distinti il testo citato (con fonte e pagina) dal testo scritto da elezio, così chi riusa i dati sa cosa è CC-BY-SA e cosa no.
3. Scegliere tra CC-BY-SA e CC-BY con un ADR. La clausola ShareAlike protegge da chi vorrebbe chiudere i dati, ma frena il riuso da parte di giornali e progetti con altre licenze. Per un progetto che vuole essere citato e ripreso, CC-BY 4.0 è spesso più efficace; CC-BY-SA è coerente con lo spirito AGPL del codice. Decisione di progetto, non legale.
4. Indicare in README come attribuire ("elezio, CC-BY-SA 4.0, link") per rendere la condizione di attribuzione (sez. 3.a) facile da rispettare.

## 5. Privacy: quiz nel browser, informativa, banner

Cosa dicono le fonti.

- Le Linee guida del Garante del 10 giugno 2021 (doc. web 9677876) distinguono cookie tecnici (nessun consenso), analytics equiparabili ai tecnici a condizioni precise (par. 7.2) e cookie di profilazione (consenso). Se sono presenti solo cookie tecnici o strumenti analoghi, l'informazione può stare nella home page o nell'informativa generale, senza banner (par. 6.1). Anche per i soli cookie tecnici il titolare deve dare un'informativa, che può essere inclusa in quella generale (par. 5). Le linee guida si applicano anche a tecniche diverse dai cookie, compreso il fingerprinting e gli identificatori passivi (par. 3). Fonte: https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/9677876
- Le Linee guida EDPB 2/2023 (versione 2.0, 7 ottobre 2024) chiariscono che l'art. 5(3) della direttiva ePrivacy si applica quando un'entità istruisce il terminale a inviare informazioni, per esempio con codice JavaScript che manda richieste con i dati mirati (par. 32-33); l'uso di header come lo user agent per fingerprinting può ricadere nell'art. 5(3) (par. 43); il tracciamento basato sul solo IP ricade nell'art. 5(3) quando l'IP proviene dal terminale dell'utente (par. 54-55); l'applicabilità dell'articolo non implica che serva il consenso, perché possono valere le esenzioni (par. 56). Fonte: https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22023-technical-scope-art-53-eprivacy-directive_en
- GitHub Pages registra l'indirizzo IP dei visitatori a fini di sicurezza, anche se non loggati. Fonte: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages (sezione "Data collection"). Qualsiasi altro hosting fa lo stesso.
- Il GDPR considera dato personale ogni informazione relativa a una persona identificabile (art. 4, n. 1) e l'informativa va resa quando si raccolgono dati (art. 13). Le opinioni politiche sono una categoria particolare (art. 9). Fonte: https://eur-lex.europa.eu/eli/reg/2016/679/oj/ita

Regole operative.

1. Il quiz resta interamente nel browser. Nessuna risposta, nessun risultato, nessun identificativo lasciano il dispositivo. Questa è la condizione che rende vero tutto il resto.
2. Il risultato del quiz è un'opinione politica (art. 9 GDPR). Non inviarlo mai a servizi terzi: niente eventi analytics con il partito risultante, niente URL con il risultato nei parametri, niente "condividi il risultato" che passa dal server di qualcun altro con dati in chiaro. Se si vuole la condivisione, generare l'immagine o il testo nel browser.
3. Niente banner cookie finché il sito non usa cookie, local storage persistente, fingerprinting o terze parti che tracciano. Fonte: Linee guida 2021, par. 6.1.
4. Se si salva il progresso del quiz in localStorage, è "memorizzazione" ai sensi dell'art. 5(3) ePrivacy (EDPB 2/2023, par. 35-36), ma rientra nell'esenzione per lo strumento strettamente necessario a un servizio richiesto dall'utente (Linee guida 2021, cookie tecnici). Va citato nell'informativa e non deve contenere il risultato in forma rileggibile da altri script. Preferire sessionStorage, che si svuota alla chiusura.
5. Pubblicare comunque un'informativa privacy breve, in italiano semplice, con: titolare (nome e contatto), hosting e il fatto che registra gli IP per sicurezza (con link alla privacy del provider), strumento di analytics usato e cosa raccoglie, assenza di cookie, diritti dell'interessato e diritto di reclamo al Garante. Fonti: art. 13 GDPR; Linee guida 2021, par. 5 e 8.
6. Nessuna risorsa di terze parti caricata dalle pagine (font, script, embed video, mappe), salvo lo script di analytics scelto. Ogni richiesta verso un dominio esterno trasmette l'IP del visitatore a un soggetto che poi va descritto nell'informativa.
7. Non raccogliere e-mail o moduli finché non c'è un backend e una base giuridica dichiarata. Un form "segnala un errore" può puntare a GitHub Issues o a un indirizzo e-mail, con avviso che si sta uscendo dal sito.

## 6. Analytics senza cookie: confronto e scelta

Condizioni del Garante per analytics senza consenso (Linee guida 2021, par. 7.2): potere identificativo ridotto (per IPv4 mascherare almeno la quarta componente), statistiche aggregate riferite al singolo sito, fornitore terzo che non incrocia i dati con altri né li trasmette ad altri. Il provvedimento del 9 giugno 2022 su Google Analytics (reg. n. 224, doc. web 9782890) aggiunge che l'IP troncato resta pseudonimo se chi lo riceve può arricchirlo, e che il trasferimento verso gli USA senza garanzie è illecito. Fonte: https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/9782890

Dal 10 luglio 2023 esiste la decisione di adeguatezza EU-US Data Privacy Framework (decisione 2023/1795), confermata dal Tribunale UE nella causa T-553/23 (Latombe) il 3 settembre 2025: i trasferimenti verso aziende statunitensi certificate sono ammessi. Fonte: https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/eu-us-data-transfers_en. Per un progetto piccolo è comunque più semplice scegliere un fornitore europeo e non dover ragionare di trasferimenti.

Confronto (dati dalla documentazione ufficiale, verificati il 2026-10-27).

| | Plausible Cloud | Umami Cloud | Cloudflare Web Analytics | GoatCounter (hosted) |
|---|---|---|---|---|
| Cookie / storage nel browser | Nessuno ("no cookies, browser cache or local storage") | Nessuno nel tracker | Nessuno; il beacon non accede a storage | Nessuno per il contatore |
| Come conta i visitatori | Hash giornaliero di dominio + IP + user agent + salt; salt ruotato e cancellato ogni 24 ore; IP e UA grezzi mai memorizzati | Hash di website id + IP + user agent + salt; salt ruotato di default ogni mese; IP non salvato come campo | Non conta visitatori unici: "visit" = pageview con referrer esterno; IP scartato al data center più vicino | Combina sito + IP + UA in un ID casuale tenuto in memoria al massimo 8 ore; IP e UA non memorizzati; dati aggregati per giorno |
| Dove stanno i dati | UE ("visitor data does not leave the EU") | Non dichiarato; subprocessor quasi tutti USA (Vercel, AWS, Cloudflare), Hetzner UE e ClickHouse USA/UE | Elaborazione nel data center più vicino, può essere fuori dal paese di origine; titolare USA | Hetzner, Finlandia e Germania; gestore con sede in Irlanda |
| Eventi personalizzati ("quiz completato") | Sì: `plausible('Quiz completato', {props: {...}})` più goal in dashboard | Sì: `data-umami-event` o `umami.track('nome')` | No ("Not yet") | Sì: `goatcounter.count({path: 'quiz-completato', event: true})` |
| Costo | Starter 9 $/mese per 10k pageview; prova 30 giorni; nessun free tier | Hobby gratuito: 100k eventi/mese, 1 sito, 6 mesi di retention; Pro 20 $/mese | Gratuito su tutti i piani | Gratuito per "reasonable public usage"; donazioni; self-host facile |
| Licenza software | AGPL-3.0 (Community Edition self-host, richiede circa 2 GB RAM) | MIT | Proprietario | EUPL-1.2 (leggermente modificata) |
| Sampling / retention | Nessun sampling dichiarato | 6 mesi nel piano Hobby | Dati non campionati 7 giorni, poi aggregati al 10%; 6 mesi consultabili | Dati aggregati; singole visualizzazioni disattivate di default |
| Fonti | https://plausible.io/data-policy, https://plausible.io/#pricing, https://plausible.io/docs/custom-event-goals | https://docs.umami.is/docs/faq, https://docs.umami.is/docs/metric-definitions, https://umami.is/pricing, https://umami.is/subprocessors, https://umami.is/privacy | https://developers.cloudflare.com/web-analytics/ (faq, data-origin), https://blog.cloudflare.com/privacy-first-web-analytics/ | https://www.goatcounter.com/help/privacy, https://www.goatcounter.com/help/gdpr, https://www.goatcounter.com/help/events, https://github.com/arp242/goatcounter (LICENSE) |

Lettura rispetto alle regole italiane.

- Tutti e quattro evitano cookie e storage. Il punto delicato è l'uso di IP e user agent per derivare l'identificativo: per EDPB 2/2023 (par. 43 e 54-55) questo può ricadere nell'art. 5(3) ePrivacy, ma non implica di per sé il consenso (par. 56); per il Garante (par. 7.2) l'analytics è equiparabile ai tecnici se il potere identificativo è ridotto e i dati restano aggregati. Plausible (salt 24 ore, IP mai memorizzato) e GoatCounter (ID in memoria 8 ore, solo aggregati) riducono il potere identificativo più dell'esempio del Garante (mascherare l'ultimo ottetto). Umami con salt mensile è più debole; la documentazione stessa avverte che "non garantisce un anonimato assoluto".
- Cloudflare è il più radicale sulla privacy ma non serve allo scopo: senza eventi non si conta "quiz completato", e la retention a 6 mesi con sampling rende fragili i confronti.
- Umami Cloud è gratuito e completo, ma la catena di subprocessor è statunitense e la sede dei data center non è dichiarata: andrebbe verificata la certificazione DPF di ogni fornitore e scritto nell'informativa. Troppo lavoro per un volontario.
- Plausible è il più maturo e il più documentato (valutazione legale indipendente dello studio Simpliant pubblicata sul loro blog, con base giuridica nel legittimo interesse e art. 5(3) non applicabile per assenza di memorizzazione: https://plausible.io/blog/legal-assessment-gdpr-eprivacy). Costa 9 $/mese, quasi metà del budget.

Scelta consigliata.

1. GoatCounter in hosting (goatcounter.com) come scelta iniziale: zero costo, server in UE, nessun cookie, dati aggregati, eventi supportati, codice EUPL. Limiti da accettare: un solo manutentore, nessuna proprietà sugli eventi, dashboard essenziale, nessun DPA formale pubblicato (da chiedere, vedi sezione 7).
2. Se serve qualcosa di più solido (DPA, proprietà sugli eventi, affidabilità in campagna elettorale), passare a Plausible Cloud Starter (9 $/mese) oppure a Plausible Community Edition su un VPS europeo da 2 GB (circa 5 euro/mese, ma con aggiornamenti e backup a carico del manutentore).
3. Qualunque sia lo strumento: eventi solo di conteggio ("quiz_avviato", "quiz_completato", "confronto_aperto", con al massimo il tema come proprietà), mai il risultato, mai le risposte, mai identificatori. Script self-hosted se il fornitore lo consente, per ridurre i blocchi degli ad-blocker e le richieste a terzi.
4. Documentare nell'informativa: nome del fornitore, cosa raccoglie, dove sono i dati, assenza di cookie, link alla sua privacy policy.
5. Rivalutare prima dell'inizio della campagna elettorale: picchi di traffico possono superare il "reasonable usage" di GoatCounter o i 10k pageview di Plausible Starter.

## 7. Par condicio e normativa elettorale

Cosa dicono le fonti.

- La legge 28/2000 regola l'accesso ai mezzi di informazione per la comunicazione politica. I destinatari degli obblighi sono le emittenti radiotelevisive (art. 2) e gli editori di quotidiani e periodici per i messaggi politici elettorali (art. 7). Nessun articolo menziona siti internet. Fonti: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2000-02-22;28~art2 e https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2000-02-22;28~art7
- L'art. 8 vieta a chiunque di "rendere pubblici o, comunque, diffondere" i risultati di sondaggi sull'esito delle elezioni e sugli orientamenti di voto nei quindici giorni precedenti il voto; fuori dal divieto, ogni sondaggio pubblicato deve avere la nota informativa (committente, campione, metodo, data) ed essere depositato sul sito della Presidenza del Consiglio. Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2000-02-22;28~art8
- Il regolamento AGCOM per le politiche 2022 (delibera 299/22/CONS, art. 1) si applica "nei confronti dell'emittenza privata [...] e della stampa quotidiana e periodica"; il Titolo VI (art. 28) si rivolge solo alle piattaforme di condivisione video e ai social network, con misure di autoregolamentazione e il rispetto degli art. 8 e 9 della legge 28/2000. Fonte: https://www.agcom.it/sites/default/files/migration/delibera/Delibera%20299-22-CONS.pdf
- Il silenzio elettorale (art. 9 l. 212/1956) vieta nel giorno precedente e in quelli del voto comizi, riunioni di propaganda in luoghi pubblici e nuove affissioni; nei giorni del voto ogni propaganda entro 200 metri dai seggi. Riguarda la propaganda, non l'informazione. Fonte: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1956-02-04;212~art9
- Il regolamento (UE) 2024/900 sulla trasparenza della pubblicità politica riguarda messaggi diffusi dietro remunerazione o in campagne di pubblicità politica, con esclusioni per contenuti editoriali e opinioni personali. Un sito informativo gratuito che confronta programmi non dovrebbe rientrarvi, ma il testo non è stato letto integralmente in questa ricerca (vedi sezione 8). Fonte: https://eur-lex.europa.eu/eli/reg/2024/900/oj/ita

Regole operative.

1. Elezio non è destinatario della legge 28/2000 né dei regolamenti AGCOM. Nessun obbligo formale di spazi paritari, nessuna comunicazione all'Autorità. Adottare comunque la parità come regola interna: stessa struttura di scheda e stesso spazio per ogni lista presente in "Elezioni trasparenti", ordine neutro (alfabetico o casuale per sessione), nessuna lista esclusa per scelta editoriale.
2. Non pubblicare sondaggi, neppure "indicativi". Non aggregare né pubblicare i risultati del quiz ("il 40% degli utenti è più vicino a X"): sarebbe presentabile come orientamento di voto e cadrebbe nel divieto dell'art. 8 nei 15 giorni prima del voto; fuori da quel periodo richiederebbe la nota informativa, che per un quiz non è possibile fornire. Il quiz non è un sondaggio solo finché le risposte non vengono raccolte.
3. Non ospitare messaggi dei partiti, banner elettorali o contenuti a pagamento. Questo tiene elezio fuori dall'art. 7 l. 28/2000 e dal regolamento 2024/900.
4. Nel giorno di silenzio e nei giorni del voto il sito può restare online con contenuti informativi. Per prudenza, nessuna pubblicazione di contenuti nuovi di taglio valutativo in quei giorni.
5. Mantenere una pagina "Metodo" che spiega come vengono scelti i temi, le citazioni e i pesi del quiz. Non è un obbligo di legge: è la difesa migliore contro l'accusa di parzialità.
6. Descrivere il quiz come "orientamento sui programmi", mai come "per chi votare". La distanza dal termine "sondaggio" è sostanziale, non solo lessicale.

## 8. Da verificare con un legale

1. Conservazione nel repo del testo estratto dai PDF: l'art. 70-quater ammette copie "per il tempo necessario" all'estrazione; un archivio git permanente, anche non pubblicato, potrebbe eccedere. Serve un parere su come trattare l'archivio di lavoro (cartella privata, cancellazione dopo la pubblicazione delle sintesi, o licenza diversa).
2. Quantità ammissibile di citazioni per scheda: il limite "giustificato dai fini" dell'art. 70 non ha soglie numeriche. Il tetto di 300 parole per tema e partito è una convenzione interna da confermare.
3. Loghi: confermare che la riproduzione del contrassegno su un sito non commerciale resti fuori dall'uso "nell'attività economica" (art. 20 CPI) anche se il progetto accetta donazioni o ha sponsor tecnici.
4. GoatCounter: verificare se il gestore offre un accordo di trattamento (art. 28 GDPR) o se, data la natura aggregata dei dati, il rapporto può essere qualificato diversamente. Stessa domanda per Plausible, che un DPA lo pubblica.
5. Qualificazione di elezio come titolare rispetto agli IP registrati dall'hosting (GitHub Pages, Cloudflare Pages o altro): chi è titolare e chi responsabile, e cosa scrivere nell'informativa.
6. Regolamento (UE) 2024/900: confermare che un sito gratuito e non partigiano che pubblica confronti tra programmi non rientri nella definizione di "pubblicità politica", in particolare se riceve donazioni o se condivide contenuti sui social.
7. Se in futuro si pubblicano statistiche aggregate sull'uso del quiz (anche solo "quante persone l'hanno completato"), verificare che non siano assimilabili a un sondaggio ai sensi dell'art. 8 l. 28/2000 e della delibera AGCOM 256/10/CSP.
8. Diritto sui generis: se il dataset di elezio viene costruito anche con dati provenienti da altre banche dati (per esempio risultati elettorali o finanziamenti dal Ministero o dalla Camera), verificare le condizioni di riuso di ciascuna fonte prima di applicare la CC-BY-SA all'insieme.

## Fonti consultate

Normativa italiana (normattiva.it)
- Legge 633/1941, art. 5, 65, 66, 70, 70-quater, 102-bis
- D.lgs. 30/2005 (Codice della proprietà industriale), art. 20 e 21
- Legge 28/2000, art. 1, 2, 7, 8
- Legge 212/1956, art. 9
- Legge 165/2017, art. 4
- DPR 361/1957, art. 14 e 14-bis (testo non raggiungibile per articolo su normattiva; contenuto verificato tramite il dossier della Camera dei deputati "Elezioni politiche 25 settembre 2022")

Autorità
- Garante privacy, Linee guida cookie e altri strumenti di tracciamento, 10 giugno 2021, doc. web 9677876
- Garante privacy, provvedimento 9 giugno 2022 n. 224 (Google Analytics), doc. web 9782890
- EDPB, Guidelines 2/2023 on the technical scope of Art. 5(3) ePrivacy Directive, versione 2.0, 7 ottobre 2024
- AGCOM, delibera 299/22/CONS, 3 agosto 2022
- Ministero dell'Interno, sezione "Elezioni trasparenti", https://dait.interno.gov.it/elezioni/trasparenza
- Commissione europea, EU-US Data Privacy Framework (decisione 2023/1795); Tribunale UE, causa T-553/23, 3 settembre 2025

Licenze
- CC BY-SA 4.0, testo legale in italiano
- GNU AGPL-3.0 (testo FSF, verificato sul file LICENSE.md di plausible/analytics)
- Umami: MIT; GoatCounter: EUPL-1.2 modificata (file LICENSE nei rispettivi repository GitHub)

Documentazione dei fornitori
- Plausible: data policy, pricing, custom events, legal assessment (Simpliant)
- Umami: FAQ, metric definitions, pricing, privacy policy, subprocessors, track events
- Cloudflare Web Analytics: FAQ, data origin, blog "privacy-first web analytics"
- GoatCounter: privacy, GDPR, events, home page (prezzi)
- GitHub Pages: "What is GitHub Pages", sezione Data collection
