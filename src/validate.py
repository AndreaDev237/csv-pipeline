"""Normalizza e valida le righe grezze.

Versione attesa dall'AI, da confermare in registrazione. Contiene l'errore #2.
"""

from datetime import datetime


def normalizza_data(grezzo: str):
    return datetime.fromisoformat(grezzo).date()


def normalizza_valore(grezzo: str) -> float:
    return float(grezzo)


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
