"""Orchestrazione da riga di comando."""

import argparse
import sqlite3
from pathlib import Path

from src.aggregate import (
    carica_anagrafica, media_mensile, ordina_per_data, rimuovi_duplicati,
)
from src.download import leggi_csv
from src.store import crea_schema, inserisci
from src.validate import valida

DATI = Path(__file__).resolve().parent.parent / "data"


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline rilevazioni qualita' dell'aria"
    )
    parser.add_argument("--misure", type=Path, default=DATI / "rilevazioni_2025.csv")
    parser.add_argument("--anagrafica", type=Path, default=DATI / "stazioni.csv")
    parser.add_argument("--output", type=Path, default=Path("rilevazioni.db"))
    argomenti = parser.parse_args(argv)

    righe = leggi_csv(argomenti.misure)
    valide, scarti = valida(righe)
    uniche = ordina_per_data(rimuovi_duplicati(valide))
    anagrafica = carica_anagrafica(argomenti.anagrafica)

    argomenti.output.unlink(missing_ok=True)
    conn = sqlite3.connect(argomenti.output)
    crea_schema(conn)
    inserite = inserisci(conn, uniche, anagrafica)
    conn.close()

    medie = media_mensile(uniche, anagrafica)

    print("Righe lette:      ", len(righe))
    print("Scartate:         ", len(scarti))
    print("Duplicati rimossi:", len(valide) - len(uniche))
    print("Inserite:         ", inserite)
    print("Aggregati:        ", len(medie), "combinazioni comune/inquinante/mese")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
