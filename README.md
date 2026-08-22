# csv-pipeline

Progetto fil rouge del Modulo 4 — Vibe coding con Python.

Scarica un CSV di rilevazioni di qualita' dell'aria, lo valida, lo aggrega
e lo salva su SQLite. Solo standard library.

## Come si naviga

La storia git e' lineare. Ogni lezione ha due tag:

    git checkout l04-start
    git checkout l04-end
    git diff l04-start l04-end

Il modulo mostra **un solo errore dell'AI**, alla lezione 7, e ha un tag
dedicato. Il diff fra lo stato sbagliato e la correzione e' esso stesso
materiale didattico: non serve riguardare il video per ricordare cosa e'
successo.

    git diff l07-bug-mutazione l07-end -- src/aggregate.py

| Tag | Lezione | Cosa contiene |
|---|---|---|
| `l04-start` | 4 | c'e' il dataset, non c'e' codice |
| `l04-prima-versione` | 4 | download che assume UTF-8: il file e' cp1252 |
| `l04-end` | 4 | encoding corretto, codice leggibile |
| `l05-start` | 5 | = `l04-end` |
| `l05-formati` | 5 | due formati di data e virgola decimale gestiti |
| `l05-end` | 5 | validazione completa |
| `l06-start` | 6 | = `l05-end` |
| `l06-end` | 6 | suite pytest |
| `l07-start` | 7 | = `l06-end` |
| `l07-bug-mutazione` | 7 | **il bug: `list.sort()` muta la lista del chiamante** |
| `l07-end` | 7 | aggregazione e refactor, bug corretto |
| `l08-start` | 8 | = `l07-end` |
| `l08-end` | 8 | SQLite con vincolo UNIQUE, CLI |
| `l09-start` | 9 | = `l08-end`. La lezione 9 non scrive codice |

Ogni `lNN-end` coincide con `l(NN+1)-start`: la storia e' lineare e i tag sono
due nomi per lo stesso commit.

**Nota sui messaggi di commit.** I tag seguono la numerazione attuale delle
lezioni. I messaggi di commit portano ancora quella di una versione precedente
del modulo, a undici lezioni, e sono sfasati di uno o due. **Fidati del tag, non
del messaggio.**

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

## Il bug della lezione 7

Il modulo mostra un solo errore dell'AI, ed e' questo:

    git diff l07-bug-mutazione l07-end -- src/aggregate.py

Chiesto di rendere il codice piu' efficiente, l'assistente propone
`lista.sort()` al posto di `sorted(lista)`. E' davvero piu' efficiente:
evita di allocare una copia. Ma ordina la lista del chiamante, che non e'
sua. Il test di integrita' scritto alla lezione 6 lo cattura alla seconda
chiamata.

Il suggerimento e' corretto sul piano richiesto e sbagliato su un piano
che non era stato nominato. E' il motivo per cui il modulo insiste sulla
regola "so spiegarlo".

## Il dataset e' sporco di proposito

Codifica cp1252, date in due formati, virgole decimali, righe troncate,
valori sentinella `-9999`, duplicati da ritrasmissione. Non sono trappole
per l'AI: sono i difetti che hanno i dati veri, e trattarli e' il lavoro.

Aprire il file in UTF-8 solleva `UnicodeDecodeError` alla riga 731. E' il
traceback su cui lavora la lezione 5.
