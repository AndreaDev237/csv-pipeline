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
