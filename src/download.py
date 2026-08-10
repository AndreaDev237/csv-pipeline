"""Scarica e legge il CSV delle rilevazioni.

Versione attesa dall'AI, da confermare in registrazione. Contiene l'errore #1.
"""

import csv
import urllib.request
from pathlib import Path


def scarica_csv(url: str, destinazione: Path) -> Path:
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as risposta:
        destinazione.write_bytes(risposta.read())
    return destinazione


def leggi_csv(percorso: Path) -> list:
    contenuto = percorso.read_bytes().decode("utf-8")
    return list(csv.DictReader(contenuto.splitlines()))
