"""Aggrega le rilevazioni, usando l'anagrafica per dare senso ai numeri.

Il file delle misure non dice cosa misura ne' in quale unita': quella
informazione vive solo in stazioni.csv. Aggregare senza guardarla produce
numeri puliti e privi di senso, perche' mescola microgrammi e milligrammi.
"""

import csv
from pathlib import Path


def carica_anagrafica(percorso: Path) -> dict:
    """Carica l'anagrafica dei sensori, indicizzata per IdSensore."""
    anagrafica = {}
    with percorso.open(encoding="utf-8", newline="") as f:
        for riga in csv.DictReader(f):
            anagrafica[riga["IdSensore"]] = {
                "inquinante": riga["NomeTipoSensore"],
                "unita_misura": riga["UnitaMisura"],
                "nome_stazione": riga["NomeStazione"],
                "comune": riga["Comune"],
                "provincia": riga["Provincia"],
            }
    return anagrafica


def rimuovi_duplicati(rilevazioni: list) -> list:
    """Elimina le ritrasmissioni del datalogger, conservando l'ordine."""
    viste = set()
    uniche = []
    for rilevazione in rilevazioni:
        chiave = rilevazione["id_sensore"] + "|" + rilevazione["data"].isoformat()
        if chiave not in viste:
            viste.add(chiave)
            uniche.append(rilevazione)
    return uniche


def chiave_ordinamento(rilevazione: dict):
    """Criterio di ordinamento, come funzione nominata invece che lambda."""
    return (rilevazione["data"], rilevazione["id_sensore"])


def ordina_per_data(rilevazioni: list) -> list:
    """Versione attesa dall'AI: ordina in place, evita una copia."""
    rilevazioni.sort(key=chiave_ordinamento)
    return rilevazioni


def media_mensile(rilevazioni: list, anagrafica: dict) -> dict:
    """Media per comune, inquinante, unita' di misura e mese.

    Inquinante e unita' fanno parte della chiave, non sono decorazione:
    senza di loro si mediano microgrammi con milligrammi.
    """
    gruppi = {}
    for rilevazione in rilevazioni:
        sensore = anagrafica[rilevazione["id_sensore"]]
        mese = rilevazione["data"].strftime("%Y-%m")
        chiave = (
            sensore["comune"] + "|"
            + sensore["inquinante"] + "|"
            + sensore["unita_misura"] + "|"
            + mese
        )
        if chiave not in gruppi:
            gruppi[chiave] = []
        gruppi[chiave].append(rilevazione["valore"])

    medie = {}
    for chiave in gruppi:
        valori = gruppi[chiave]
        medie[chiave] = sum(valori) / len(valori)
    return medie
