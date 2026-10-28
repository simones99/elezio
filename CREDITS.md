# Crediti

elezio riusa il più possibile lavoro open source e dati pubblici esistenti. Questo file elenca ogni componente riusato, cosa ne è stato preso e sotto quale licenza. La stessa lista, in forma leggibile, va nella pagina `/crediti` del sito.

Regole per aggiungere una voce:

- una riga per componente, nella sezione giusta, nel momento in cui entra nel repository o nel sito;
- versione o data esatta del materiale preso, e link alla sua fonte;
- se si copia un file di terze parti, il testo della sua licenza va accanto al file copiato (per esempio `sito/public/vendor/LICENSE-open-election-compass.txt`);
- materiale senza licenza non si copia: al massimo si cita come ispirazione nell'ultima sezione;
- lo stato dice se la voce è già nel repository (`incluso`), solo sul branch di un prototipo (`prototipo`) o decisa ma non ancora integrata (`previsto`).

## Codice

| Componente | Link | Licenza | Cosa è stato preso | Stato |
| --- | --- | --- | --- | --- |
| Open Election Compass, client 2.0.0-alpha.5 | https://github.com/open-election-compass/client | GPL-3.0 | Bundle UMD `open-election-compass.umd.min.js` self-hostato per il quiz di orientamento, senza modifiche (ADR 0006, ADR 0007) | previsto |
| Open Election Compass, UI 0.14.0 | https://github.com/open-election-compass/ui | GPL-3.0 (dichiarata nel registro npm) | Inclusa nel bundle del client, non presa a parte | previsto |

## Font

| Componente | Link | Licenza | Cosa è stato preso | Stato |
| --- | --- | --- | --- | --- |
| Cinzel, di Natanael Gama | https://github.com/NDISCOVER/Cinzel | SIL Open Font License 1.1 | File variabile, sottoinsieme latino in WOFF2, per le capitali dei titoli | prototipo |
| Archivo, di Omnibus-Type | https://github.com/Omnibus-Type/Archivo | SIL Open Font License 1.1 | File variabile, sottoinsieme latino in WOFF2, per il testo | prototipo |

## Fotografie

| Foto | Link | Licenza | Cosa è stato preso | Stato |
| --- | --- | --- | --- | --- |
| Seggio vicino al Colosseo (Roma), video del Parlamento europeo, rif. I257607 | https://multimedia.europarl.europa.eu/en/video/european-elections-2024-ambiance-shots-of-polling-station-near-the-colosseum-in-the-historical-city-center-of-rome-italy_I257607 | © Unione europea, 2024, nota legale del Parlamento europeo | 8 fotogrammi tra 2:47,6 e 2:50,8, ritagliati e posterizzati in duotono, per la copertina animata della home | prototipo |
| Corridoio ambulatori, Ospedale Santa Maria della Misericordia (Rovigo), di Threecharlie | https://commons.wikimedia.org/wiki/File:Ospedale_Santa_Maria_della_Misericordia,_interno,_corridoio_ambulatori_quinto_piano_(Rovigo)_01.jpg | CC BY-SA 4.0 | Miniatura da 1920 px, in duotono inchiostro-carta e ritagliata, come copertina di prova del tema Sanità | prototipo |

## Dati e documenti fonte

| Fonte | Link | Condizioni | Cosa è stato preso | Stato |
| --- | --- | --- | --- | --- |
| Ministero dell'Interno, Elezioni trasparenti, politiche 2022 | https://dait.interno.gov.it/elezioni/trasparenza/elezioni-politiche-2022 | Documenti pubblicati per legge (art. 4 l. 165/2017); diritti dei rispettivi partiti | Programmi depositati, solo come link con hash e citazioni brevi con pagina; contrassegni a fini identificativi | prototipo |

## Ispirazione

Progetti letti e studiati, da cui non è stato copiato codice né dati.

| Progetto | Link | Licenza | Cosa ha ispirato |
| --- | --- | --- | --- |
| Mat-O-Wahl | https://github.com/msteudtn/Mat-O-Wahl | GPL-3.0 | Piano di riserva per il quiz, metodo di punteggio con risposta neutrale |
| Stemwijzert | https://github.com/ERRuijs/Stemwijzert | nessuna | Idea della modalità cieca: proposte anonime, partiti rivelati alla fine |
| Electio Italia | https://github.com/Electio-org/italia | nessuna | Rimando per i risultati elettorali storici |
