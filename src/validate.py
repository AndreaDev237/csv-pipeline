"""Normalizza e valida le righe grezze.

Formati corretti. Il criterio di validita' e' ancora il segno del valore:
sede dell'errore #2.
"""

from datetime import datetime

FORMATO_ITALIANO = "%d/%m/%Y %H:%M"


def normalizza_data(grezzo: str):
    """Accetta l'ISO del primo export e il formato italiano del secondo."""
    try:
        return datetime.fromisoformat(grezzo).date()
    except ValueError:
        return datetime.strptime(grezzo, FORMATO_ITALIANO).date()


def normalizza_valore(grezzo: str) -> float:
    """Accetta il punto decimale e la virgola del locale italiano."""
    return float(grezzo.replace(",", "."))


def valida(righe: list) -> tuple:
    valide = []
    scarti = []
    for numero_riga, riga in enumerate(righe, start=1):
        valore = normalizza_valore(riga["Valore"])
        if valore < 0:
            scarti.append(f"riga {numero_riga}: valore negativo")
            continue
        valide.append({
            "id_sensore": riga["IdSensore"],
            "nome_stazione": riga["NomeStazione"],
            "data": normalizza_data(riga["Data"]),
            "valore": valore,
        })
    return valide, scarti
