import sqlite3
from datetime import date
from pathlib import Path

import pytest

from src.aggregate import carica_anagrafica
from src.store import crea_schema, inserisci

DATI = Path(__file__).resolve().parent.parent / "data"


def apri_database() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    crea_schema(conn)
    return conn


def carica_anagrafica_di_prova() -> dict:
    return carica_anagrafica(DATI / "stazioni.csv")


def rilevazione(id_sensore: str, giorno: date, valore: float) -> dict:
    return {
        "id_sensore": id_sensore,
        "nome_stazione": "irrilevante per il database",
        "data": giorno,
        "valore": valore,
    }


def test_lo_schema_crea_la_tabella():
    conn = apri_database()

    nomi = []
    for riga in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        nomi.append(riga[0])

    assert "rilevazioni" in nomi


def test_inserisce_e_conta():
    conn = apri_database()
    anagrafica = carica_anagrafica_di_prova()
    rilevazioni = [
        rilevazione("10001", date(2025, 1, 5), 40.0),
        rilevazione("10004", date(2025, 1, 5), 1.8),
    ]

    inserite = inserisci(conn, rilevazioni, anagrafica)

    assert inserite == 2


def test_la_tabella_conserva_inquinante_e_unita():
    """Il risultato della L8 resta inciso anche nel database."""
    conn = apri_database()
    anagrafica = carica_anagrafica_di_prova()

    inserisci(conn, [rilevazione("10004", date(2025, 1, 5), 1.8)], anagrafica)

    riga = conn.execute(
        "SELECT inquinante, unita_misura, comune FROM rilevazioni"
    ).fetchone()

    assert riga == ("CO", "mg/m³", "Brescia")


def test_il_database_rifiuta_i_duplicati():
    """Un controllo che non viene dall'AI ne' dai test: viene dallo schema."""
    conn = apri_database()
    anagrafica = carica_anagrafica_di_prova()
    una = rilevazione("10001", date(2025, 1, 5), 40.0)

    inserisci(conn, [una], anagrafica)

    with pytest.raises(sqlite3.IntegrityError):
        inserisci(conn, [una], anagrafica)


def test_le_date_sono_salvate_in_iso():
    conn = apri_database()
    anagrafica = carica_anagrafica_di_prova()

    inserisci(conn, [rilevazione("10001", date(2025, 3, 14), 40.0)], anagrafica)

    riga = conn.execute("SELECT data FROM rilevazioni").fetchone()

    assert riga[0] == "2025-03-14"
