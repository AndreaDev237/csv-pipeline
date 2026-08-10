import json
from pathlib import Path

from src.download import leggi_csv

DATI = Path(__file__).resolve().parent.parent / "data"


def carica_manifest() -> dict:
    """Helper, non fixture: una fixture pytest richiede un decoratore."""
    testo = (DATI / "manifest.json").read_text(encoding="utf-8")
    return json.loads(testo)


def carica_righe() -> list:
    return leggi_csv(DATI / "rilevazioni_2025.csv")


def test_legge_tutte_le_righe():
    manifest = carica_manifest()
    righe = carica_righe()

    assert len(righe) == manifest["righe_totali"]


def test_conserva_i_nomi_di_stazione_accentati():
    righe = carica_righe()
    stazioni = []
    for riga in righe:
        if riga["NomeStazione"] not in stazioni:
            stazioni.append(riga["NomeStazione"])

    assert "Cantù - Via Meucci" in stazioni
    assert "Brescia – Villaggio Sereno" in stazioni


def test_le_chiavi_sono_quelle_del_file():
    righe = carica_righe()
    chiavi = list(righe[0].keys())

    assert chiavi == [
        "IdSensore", "NomeStazione", "Data", "Valore", "Stato", "idOperatore",
    ]
