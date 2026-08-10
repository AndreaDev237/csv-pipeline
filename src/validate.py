"""Normalizza e valida le righe grezze del CSV delle rilevazioni."""

from datetime import datetime

FORMATO_ITALIANO = "%d/%m/%Y %H:%M"
STATO_VALIDO = "VA"
CAMPI_ATTESI = ["IdSensore", "NomeStazione", "Data", "Valore", "Stato"]


def normalizza_data(grezzo: str):
    """Accetta l'ISO del primo export e il formato italiano del secondo."""
    try:
        return datetime.fromisoformat(grezzo).date()
    except ValueError:
        return datetime.strptime(grezzo, FORMATO_ITALIANO).date()


def normalizza_valore(grezzo: str) -> float:
    """Accetta il punto decimale e la virgola del locale italiano."""
    return float(grezzo.replace(",", "."))


def campi_mancanti(riga: dict) -> bool:
    """Vero se manca uno dei campi che servono a costruire la rilevazione.

    Le righe troncate in trasmissione arrivano con meno campi:
    csv.DictReader mette None al posto di quelli che mancano, senza
    segnalare niente.
    """
    for campo in CAMPI_ATTESI:
        if riga.get(campo) is None:
            return True
    return False


def valida(righe: list) -> tuple:
    """Separa le rilevazioni utilizzabili dagli scarti, con il motivo.

    Il criterio di validita' e' la colonna Stato, non il segno del valore.
    Filtrare i negativi sembra equivalente, e su quasi tutto il file lo e':
    -9999 e Stato "NA" vanno insieme. Ma un sensore in taratura trasmette
    un valore plausibile ed e' comunque marcato non valido. Il filtro sul
    segno lo accetta. Funzionava per coincidenza.
    """
    valide = []
    scarti = []

    for numero_riga, riga in enumerate(righe, start=1):
        if campi_mancanti(riga):
            scarti.append(f"riga {numero_riga}: campi mancanti")
            continue
        if riga["Stato"] != STATO_VALIDO:
            scarti.append(f"riga {numero_riga}: stato {riga['Stato']}")
            continue
        valide.append({
            "id_sensore": riga["IdSensore"],
            "nome_stazione": riga["NomeStazione"],
            "data": normalizza_data(riga["Data"]),
            "valore": normalizza_valore(riga["Valore"]),
        })

    return valide, scarti
