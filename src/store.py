"""Salva le rilevazioni su SQLite.

Una sola tabella, denormalizzata: porta con se' inquinante, unita' di
misura e comune, cosi' che il risultato della lezione 8 resti inciso anche
nel database e non si possa piu' perdere.

Il vincolo UNIQUE non e' decorazione. E' un controllo che non viene
dall'AI e non viene dai test: viene dallo schema, e scatta anche quando
tutto il resto e' distratto.
"""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS rilevazioni (
    id            INTEGER PRIMARY KEY,
    id_sensore    TEXT NOT NULL,
    inquinante    TEXT NOT NULL,
    unita_misura  TEXT NOT NULL,
    comune        TEXT NOT NULL,
    data          TEXT NOT NULL,
    valore        REAL NOT NULL,
    UNIQUE (id_sensore, data)
);
"""


def crea_schema(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def inserisci(conn: sqlite3.Connection, rilevazioni: list, anagrafica: dict) -> int:
    """Inserisce le rilevazioni arricchite con i dati dell'anagrafica."""
    righe = []
    for rilevazione in rilevazioni:
        sensore = anagrafica[rilevazione["id_sensore"]]
        righe.append((
            rilevazione["id_sensore"],
            sensore["inquinante"],
            sensore["unita_misura"],
            sensore["comune"],
            rilevazione["data"].isoformat(),
            rilevazione["valore"],
        ))

    conn.executemany(
        "INSERT INTO rilevazioni "
        "(id_sensore, inquinante, unita_misura, comune, data, valore) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        righe,
    )
    conn.commit()
    return len(righe)
