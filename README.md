# csv-pipeline

Progetto fil rouge del Modulo 4 — Vibe coding con Python.

Scarica un CSV di rilevazioni di qualita' dell'aria, lo valida, lo aggrega
e lo salva su SQLite. Solo standard library.

## Come si naviga

La storia git e' lineare. Ogni lezione ha due tag:

    git checkout l04-start
    git checkout l04-end
    git diff l04-start l04-end

Gli stati generati dall'AI che contengono un errore hanno un tag dedicato:

    git checkout l04-ai-sbagliata

Il diff fra lo stato sbagliato e la correzione e' esso stesso materiale
didattico: non serve riguardare il video per ricordare cosa e' successo.

    git diff l06-ai-sbagliata l06-end -- src/validate.py

| Tag | Lezione | Cosa contiene |
|---|---|---|
| `l04-start` | 4 | c'e' il dataset, non c'e' codice |
| `l04-ai-sbagliata` | 4 | download che assume UTF-8 |
| `l04-end` | 4 | encoding cp1252 |
| `l05-end` | 5 | leggibilita', nessun cambio di comportamento |
| `l06-ai-sbagliata` | 6 | validazione che filtra sul segno del valore |
| `l06-formati` | 6 | due formati di data e virgola decimale corretti |
| `l06-end` | 6 | il criterio e' la colonna Stato |
| `l07-ai-sbagliata` | 7 | test che non possono fallire |
| `l07-end` | 7 | attese derivate dal manifest |
| `l08-ai-sbagliata` | 8 | medie che mescolano inquinanti e unita' |
| `l08-end` | 8 | inquinante e unita' nella chiave |
| `l09-ai-sbagliata` | 9 | ordinamento in place che muta l'input |
| `l09-end` | 9 | rifiutato il suggerimento, accettata la comprehension |
| `l10-end` | 10 | SQLite con vincolo UNIQUE, CLI |

## Come si esegue

    python -m src.cli --output rilevazioni.db

## Come si testa

    pytest

## Il dataset

Generato, non scaricato. La struttura ricalca i dataset open data di ARPA
Lombardia (`Dati sensori aria`, `Stazioni qualita' dell'aria`), verificati
su dati live il 2026-08-10.

    python tools/genera_dataset.py

Il generatore e' seedato: stessa esecuzione, stessi difetti nelle stesse
righe. I numeri di riga citati nelle lezioni dipendono da questa proprieta'.

## Cosa aspettarsi eseguendo

    python -m src.cli --output rilevazioni.db

    Righe lette:       4219
    Scartate:          206
    Duplicati rimossi: 21
    Inserite:          3992
    Aggregati:         138 combinazioni comune/inquinante/mese

Ventuno duplicati e non ventitre': il generatore ne inserisce 23, ma due
di quelle righe erano marcate NA e la validazione le ha gia' scartate
prima della deduplica. 4219 meno 206 fa 4013 valide, 4013 meno 21 fa 3992.

## Condizioni di registrazione

Da compilare alla registrazione. Gli output degli strumenti AI cambiano nel
tempo: se ottieni una risposta diversa da quella del video, non hai
sbagliato, e' cambiato il modello.

| | |
|---|---|
| Data di registrazione | DA COMPILARE |
| GitHub Copilot | versione estensione DA COMPILARE, piano gratuito |
| Codex | modello DA COMPILARE, piano DA COMPILARE |
| Claude Code | versione DA COMPILARE, piano DA COMPILARE |
| Python | DA COMPILARE |

## Stato di questo repository

Il codice e i test sono completi e la storia git e' costruita. Gli stati
marcati "versione attesa, da confermare in registrazione" sono il
riferimento del piano, **non output reali degli strumenti AI**: vanno
sostituiti con cio' che gli strumenti producono davvero durante la
registrazione. La cartella `prompts/` e' ancora vuota per questo motivo.
