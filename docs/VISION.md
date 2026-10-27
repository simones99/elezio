# elezio: visione

Ultimo aggiornamento: 27 ottobre 2026. Mappa delle decisioni: [Mappa: elezio v1](https://github.com/simones99/elezio/issues/1).

## Perché

I programmi elettorali italiani esistono, ma quasi nessuno li legge: sono PDF lunghi, scritti per addetti ai lavori, sparsi sui siti dei partiti. elezio li rende fruibili: per tema, in linguaggio semplice, sempre con la citazione testuale e la pagina del documento originale, così che chi vota possa farsi un'idea in pochi minuti e verificarla da solo.

Il progetto ha tre scopi dichiarati, in quest'ordine: fare qualcosa di utile per chi vota, imparare costruendo un prodotto vero, e avere un progetto pubblico e verificabile sul CV del maintainer.

## Per chi

L'utente primario è l'elettore indeciso tra i 18 e i 35 anni, da telefono, che legge poco e vuole una risposta in cinque minuti. Giornalisti, insegnanti e ricercatori sono una seconda ondata, non il bersaglio di v1.

## Cosa fa v1

Tre funzioni, niente altro:

1. **Schede per tema.** Per ciascun partito in perimetro e ciascuno dei 12 temi, una scheda con sintesi semplice, proposta originale, citazione testuale, riferimento alla pagina del documento e stato di verifica.
2. **Confronto tematico.** Le schede di due o tre partiti affiancate sullo stesso tema.
3. **Quiz di orientamento.** Tra 20 e 25 affermazioni; le posizioni dei partiti derivano dalle stesse schede, con le stesse citazioni; il punteggio è spiegato in linguaggio semplice.

Perimetro v1: 10 partiti (Fratelli d'Italia, Partito Democratico, Movimento 5 Stelle, Lega, Forza Italia, Alleanza Verdi e Sinistra, Azione, Italia Viva, +Europa, Futuro Nazionale) per 12 temi, cioè 120 schede. La beta esce sui programmi delle politiche 2022; il rilascio pubblico avviene sui programmi 2027 appena vengono pubblicati.

## Principi

- **Nessuna posizione senza citazione.** Una scheda non attribuisce a un partito niente che non sia citato testualmente da un documento fonte, con la pagina. Vedi [ADR 0003](adr/0003-nessuna-posizione-senza-citazione.md).
- **Metodologia pubblica.** Criteri di inclusione dei partiti, lista dei temi, modello di punteggio del quiz, prompt e modelli usati per le bozze: tutto pubblicato nel repo e in una pagina del sito.
- **L'umano verifica, la macchina propone.** Un LLM genera bozze di sintesi ed estrae citazioni; ogni scheda pubblicata è verificata da una persona.
- **Statico prima.** Sito generato staticamente, contenuti in git, nessun backend, quiz calcolato nel browser, nessuna risposta salvata, analytics senza cookie. Vedi [ADR 0001](adr/0001-sito-statico-senza-backend.md).
- **Riuso dichiarato.** Si riusa il più possibile da progetti open source esistenti, e ogni componente riusato è citato in `CREDITS.md` e nella pagina crediti del sito.
- **Aperto.** Codice AGPL-3.0, dati CC-BY-SA 4.0 (da confermare). Vedi [ADR 0002](adr/0002-licenze-agpl-e-cc-by-sa.md).
- **Solo italiano**, solo web responsive. Niente app nativa, niente multilingua, niente account utente in v1.

## Cosa non è v1

Finanziamenti ai partiti, network map dei legami, storia e risultati elettorali, performance regionali e locali, ricerca semantica o chat sui programmi, dibattiti, modalità cieca, political compass a due dimensioni. Tutto questo è registrato come possibile sviluppo futuro nella mappa, non promesso.

## Successo

v1 è riuscita se il sito è online entro il 28 febbraio 2027 con 120 schede verificate e un quiz funzionante, e se almeno 500 persone completano il quiz entro il giorno del voto.
