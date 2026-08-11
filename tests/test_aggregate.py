from datetime import date
from pathlib import Path

from src.aggregate import (
    carica_anagrafica, media_mensile, ordina_per_data, rimuovi_duplicati,
)

DATI = Path(__file__).resolve().parent.parent / "data"


def carica_anagrafica_di_prova() -> dict:
    return carica_anagrafica(DATI / "stazioni.csv")


def rilevazione(id_sensore: str, stazione: str, giorno: date, valore: float) -> dict:
    return {
        "id_sensore": id_sensore,
        "nome_stazione": stazione,
        "data": giorno,
        "valore": valore,
    }


def test_anagrafica_carica_dodici_sensori():
    anagrafica = carica_anagrafica_di_prova()

    assert len(anagrafica) == 12
    assert anagrafica["10004"]["inquinante"] == "CO"
    assert anagrafica["10004"]["unita_misura"] == "mg/m³"
    assert anagrafica["10001"]["unita_misura"] == "µg/m³"


def test_la_chiave_include_inquinante_e_unita():
    anagrafica = carica_anagrafica_di_prova()
    rilevazioni = [
        rilevazione("10001", "Milano - Viale Marche", date(2025, 1, 5), 40.0),
        rilevazione("10002", "Milano - Viale Marche", date(2025, 1, 5), 60.0),
    ]

    medie = media_mensile(rilevazioni, anagrafica)

    assert sorted(medie.keys()) == [
        "Milano|NO2|µg/m³|2025-01",
        "Milano|PM10|µg/m³|2025-01",
    ]


def test_non_mescola_unita_diverse_dello_stesso_comune():
    """PM10 in ug/m3 e CO in mg/m3 non si mediano insieme.

    La media uscirebbe comunque, e sarebbe un numero senza significato.
    """
    anagrafica = carica_anagrafica_di_prova()
    rilevazioni = [
        rilevazione("10003", "Brescia – Villaggio Sereno", date(2025, 1, 5), 50.0),
        rilevazione("10004", "Brescia – Villaggio Sereno", date(2025, 1, 5), 1.0),
    ]

    medie = media_mensile(rilevazioni, anagrafica)

    assert medie["Brescia|PM10|µg/m³|2025-01"] == 50.0
    assert medie["Brescia|CO|mg/m³|2025-01"] == 1.0
    assert 25.5 not in medie.values()


def test_rimuove_i_duplicati_esatti():
    una = rilevazione("10001", "Milano - Viale Marche", date(2025, 1, 5), 40.0)
    rilevazioni = [una, dict(una), dict(una)]

    assert len(rimuovi_duplicati(rilevazioni)) == 1


def test_rimuovi_duplicati_conserva_la_prima_occorrenza():
    prima = rilevazione("10001", "Milano - Viale Marche", date(2025, 1, 5), 40.0)
    seconda = rilevazione("10001", "Milano - Viale Marche", date(2025, 1, 5), 99.9)

    uniche = rimuovi_duplicati([prima, seconda])

    assert uniche == [prima]


def test_ordina_per_data_non_muta_l_input():
    tarda = rilevazione("10001", "Milano - Viale Marche", date(2025, 6, 1), 40.0)
    prima = rilevazione("10001", "Milano - Viale Marche", date(2025, 1, 1), 20.0)
    rilevazioni = [tarda, prima]

    ordinate = ordina_per_data(rilevazioni)

    assert ordinate == [prima, tarda]
    assert rilevazioni == [tarda, prima]
