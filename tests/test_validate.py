import json
from datetime import date
from pathlib import Path

from src.download import leggi_csv
from src.validate import normalizza_data, normalizza_valore, valida

DATI = Path(__file__).resolve().parent.parent / "data"


def carica_manifest() -> dict:
    testo = (DATI / "manifest.json").read_text(encoding="utf-8")
    return json.loads(testo)


def carica_righe() -> list:
    return leggi_csv(DATI / "rilevazioni_2025.csv")


def test_normalizza_data_iso():
    assert normalizza_data("2025-03-14T00:00:00.000") == date(2025, 3, 14)


def test_normalizza_data_formato_italiano():
    assert normalizza_data("14/03/2025 00:00") == date(2025, 3, 14)


def test_normalizza_valore_con_punto():
    assert normalizza_valore("12.4") == 12.4


def test_normalizza_valore_con_virgola():
    assert normalizza_valore("12,4") == 12.4


def test_scarta_le_righe_non_validate():
    righe = carica_righe()
    manifest = carica_manifest()

    valide, _ = valida(righe)

    assert len(valide) == manifest["righe_valide_attese"]


def test_scarta_le_righe_in_taratura():
    """Cinque righe marcate NA con un valore plausibile.

    Sensore 10001, dall'8 al 12 settembre: era in taratura, trasmetteva, e
    il dato non e' validato. Scartare i valori negativi le lascia passare
    tutte, perche' il valore e' positivo. Solo la colonna Stato le
    riconosce.
    """
    righe = carica_righe()

    valide, _ = valida(righe)

    in_taratura = []
    for rilevazione in valide:
        stesso_sensore = rilevazione["id_sensore"] == "10001"
        nel_periodo = date(2025, 9, 8) <= rilevazione["data"] <= date(2025, 9, 12)
        if stesso_sensore and nel_periodo:
            in_taratura.append(rilevazione)

    assert in_taratura == []


def test_scarta_le_righe_malformate():
    righe = carica_righe()
    manifest = carica_manifest()

    _, scarti = valida(righe)

    malformate = []
    for scarto in scarti:
        if "campi mancanti" in scarto:
            malformate.append(scarto)

    assert len(malformate) == manifest["righe_malformate"]


def test_produce_dizionari_con_le_chiavi_attese():
    righe = carica_righe()

    valide, _ = valida(righe)

    assert list(valide[0].keys()) == [
        "id_sensore", "nome_stazione", "data", "valore",
    ]


def test_ogni_riga_finisce_in_valide_o_in_scarti():
    """Attesa derivata dal manifest, non inventata.

    Il manifest lo scrive il generatore contando i dati veri. Un numero
    scritto a mano in un assert non ha nessuna fonte.
    """
    righe = carica_righe()
    manifest = carica_manifest()

    valide, scarti = valida(righe)

    assert len(valide) == manifest["righe_valide_attese"]
    assert len(valide) + len(scarti) == manifest["righe_totali"]


def test_i_valori_con_virgola_diventano_float():
    """Nessuna guardia skip: se il dato manca, il test deve fallire.

    Una guardia skip disattiva il test proprio nel caso in cui
    servirebbe.
    """
    righe = carica_righe()

    con_virgola = []
    for riga in righe:
        if riga.get("Valore") is not None and "," in riga["Valore"]:
            con_virgola.append(riga)

    assert len(con_virgola) > 0

    valide, _ = valida(con_virgola)
    assert len(valide) > 0
    for rilevazione in valide:
        assert isinstance(rilevazione["valore"], float)


def test_valida_non_muta_l_input():
    """Rete di sicurezza contro le mutazioni silenziose.

    Serve qui e servira' ancora alla L9, quando un refactor proporra' di
    ordinare in place.
    """
    righe = carica_righe()

    prima = []
    for riga in righe:
        prima.append(dict(riga))

    valida(righe)
    valida(righe)

    assert righe == prima
