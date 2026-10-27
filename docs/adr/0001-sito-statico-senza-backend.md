---
status: accepted
date: 2026-10-27
---

# Sito statico senza backend per v1

Una persona sola con circa 130 ore totali fino ad aprile 2027 e meno di 20 euro al mese non può mantenere un backend, un database e la loro sicurezza. v1 è quindi un sito generato staticamente: i contenuti (schede, affermazioni del quiz, posizioni dei partiti) vivono come file in git e si modificano via pull request, il quiz è calcolato interamente nel browser e nessuna risposta viene salvata. Questo elimina ops, costi, GDPR sui dati del quiz e la maggior parte della superficie d'attacco.

## Considered options

- Backend con database (FastAPI o route API più Postgres), come proposto dalla ricerca di settore: scartato perché il costo di manutenzione non entra nel budget di ore e perché nessuna funzione del nucleo v1 lo richiede.
- CMS headless per la redazione: scartato perché c'è un solo redattore e git con pull request basta.

## Consequences

Ricerca semantica, account utente, salvataggio dei risultati e contributi esterni via form restano fuori finché questa decisione non viene superata. Se un componente riusato (per esempio il motore del quiz) richiede un server, va valutato prima di adottarlo.
