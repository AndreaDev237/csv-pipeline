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
    """Restituisce una nuova lista ordinata. Non tocca l'originale.

    L'alternativa in place e' piu' efficiente, ed e' per questo che l'AI
    l'ha proposta. Ma questa funzione riceve liste di cui non e'
    proprietaria: il risparmio di un'allocazione non paga una mutazione a
    distanza.
    """
    return sorted(rilevazioni, key=chiave_ordinamento)


def media_mensile(rilevazioni: list, anagrafica: dict) -> dict:
    """Media per comune, inquinante, unita' di misura e mese.

    Inquinante e unita' fanno parte della chiave, non sono decorazione:
    senza di loro si mediano microgrammi con milligrammi.

    Il secondo ciclo e' diventato una dict comprehension: stessa
    semantica, una riga invece di quattro. Il primo resta esplicito,
    perche' accumula in liste e comprimerlo lo renderebbe illeggibile.
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

    return {
        chiave: sum(valori) / len(valori)
        for chiave, valori in gruppi.items()
    }
