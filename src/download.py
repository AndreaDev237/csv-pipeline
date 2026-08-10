"""Scarica e legge il CSV delle rilevazioni."""

import csv
import urllib.request
from pathlib import Path


def scarica_csv(url: str, destinazione: Path) -> Path:
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as risposta:
        destinazione.write_bytes(risposta.read())
    return destinazione


def leggi_csv(percorso: Path) -> list:
    """Legge il CSV in cp1252.

    Non latin-1: l'en dash di "Brescia - Villaggio Sereno" in latin-1 non
    esiste. latin-1 non solleverebbe eccezione, corromperebbe in silenzio.
    """
    contenuto = percorso.read_bytes().decode("cp1252")
    return list(csv.DictReader(contenuto.splitlines()))
