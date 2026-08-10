"""Scarica e legge il CSV delle rilevazioni di qualita' dell'aria."""

import csv
import urllib.request
from pathlib import Path

CODIFICA_SORGENTE = "cp1252"

NOMI_COLONNE = [
    "IdSensore", "NomeStazione", "Data", "Valore", "Stato", "idOperatore",
]


def scarica_csv(url: str, destinazione: Path) -> Path:
    """Scarica il file all'URL indicato e lo salva senza decodificarlo.

    Salvare i byte grezzi e' deliberato: la decodifica e' una decisione
    separata, e sbagliarla qui la nasconderebbe.
    """
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as risposta:
        destinazione.write_bytes(risposta.read())
    return destinazione


def leggi_csv(percorso: Path) -> list:
    """Legge il CSV e restituisce una riga per dizionario.

    La codifica e' cp1252 e non latin-1: l'en dash di
    "Brescia - Villaggio Sereno" in latin-1 non esiste. latin-1 non
    solleverebbe eccezione, corromperebbe in silenzio.
    """
    contenuto = percorso.read_bytes().decode(CODIFICA_SORGENTE)
    return list(csv.DictReader(contenuto.splitlines()))
