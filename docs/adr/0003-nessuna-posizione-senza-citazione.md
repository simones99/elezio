---
status: accepted
date: 2026-10-27
---

# Nessuna posizione senza citazione

Il progetto ha un solo revisore, quindi la sua credibilità non può poggiare su un comitato o sulla validazione dei partiti. Poggia invece su una regola verificabile da chiunque: una scheda non attribuisce a un partito nessuna posizione che non sia sostenuta da una citazione testuale di un documento fonte, con il riferimento alla pagina. Le bozze generate da un LLM non fanno eccezione: una citazione che non si trova nel documento invalida la scheda. Quando un documento fonte non copre un tema, la scheda dice che la posizione è assente invece di inferirla.

## Consequences

La pipeline deve controllare automaticamente che ogni citazione esista nel testo estratto. Le posizioni del quiz derivano dalle schede, quindi ereditano le stesse citazioni. Il costo è che alcune schede resteranno "posizione assente" anche quando un partito ha una posizione nota per altre vie: è accettato.
