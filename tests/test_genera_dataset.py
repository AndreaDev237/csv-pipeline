import csv
import json
from datetime import date
from pathlib import Path

from tools.genera_dataset import (
    RANGE_INQUINANTI,
    RIGHE_MALFORMATE,
    SENSORI,
    genera_misure,
    inietta_difetti,
    scrivi_anagrafica,
    scrivi_misure,
)


# --- anagrafica ---------------------------------------------------------


def test_anagrafica_ha_dodici_sensori(tmp_path: Path):
    destinazione = tmp_path / "stazioni.csv"
    scrivi_anagrafica(destinazione)

    with destinazione.open(encoding="utf-8", newline="") as f:
        righe = list(csv.DictReader(f))

    assert len(righe) == 12


def test_anagrafica_ha_le_colonne_arpa(tmp_path: Path):
    destinazione = tmp_path / "stazioni.csv"
    scrivi_anagrafica(destinazione)

    with destinazione.open(encoding="utf-8", newline="") as f:
        intestazione = next(csv.reader(f))

    assert intestazione == [
        "IdSensore", "NomeTipoSensore", "UnitaMisura", "IdStazione",
        "NomeStazione", "Quota", "Provincia", "Comune", "Storico",
        "DataStart", "DataStop", "lat", "lng",
    ]


def test_sensore_10012_e_dismesso_a_meta_anno(tmp_path: Path):
    destinazione = tmp_path / "stazioni.csv"
    scrivi_anagrafica(destinazione)

    with destinazione.open(encoding="utf-8", newline="") as f:
        per_id = {r["IdSensore"]: r for r in csv.DictReader(f)}

    assert per_id["10012"]["DataStop"] == "2025-06-30"
    assert per_id["10001"]["DataStop"] == ""


def test_anagrafica_e_utf8_e_contiene_accenti(tmp_path: Path):
    destinazione = tmp_path / "stazioni.csv"
    scrivi_anagrafica(destinazione)

    testo = destinazione.read_text(encoding="utf-8")

    assert "Cantù" in testo
    assert "Brescia – Villaggio Sereno" in testo


def test_le_unita_di_misura_non_sono_omogenee(tmp_path: Path):
    """Il CO in mg/m3 e' il fulcro dell'errore #4: deve esistere."""
    destinazione = tmp_path / "stazioni.csv"
    scrivi_anagrafica(destinazione)

    with destinazione.open(encoding="utf-8", newline="") as f:
        unita = {r["UnitaMisura"] for r in csv.DictReader(f)}

    assert unita == {"µg/m³", "mg/m³"}


# --- misure pulite ------------------------------------------------------


def test_conteggio_righe_per_sensore():
    misure = genera_misure()
    per_sensore = {}
    for m in misure:
        per_sensore[m["id_sensore"]] = per_sensore.get(m["id_sensore"], 0) + 1

    assert per_sensore["10001"] == 365
    assert per_sensore["10012"] == 181  # dismesso il 2025-06-30


def test_totale_misure():
    assert len(genera_misure()) == 11 * 365 + 181


def test_misure_ordinate_per_sensore_e_data():
    misure = genera_misure()
    chiavi = [(m["id_sensore"], m["data"]) for m in misure]

    assert chiavi == sorted(chiavi)


def test_valori_nel_range_dell_inquinante():
    misure = genera_misure()
    per_id = {s["id"]: s["inquinante"] for s in SENSORI}

    for m in misure:
        minimo, massimo, _ = RANGE_INQUINANTI[per_id[m["id_sensore"]]]
        assert minimo <= m["valore"] <= massimo


def test_il_co_e_due_ordini_di_grandezza_sotto_il_pm10():
    """Se questa proprieta' cade, l'errore #4 smette di essere visibile."""
    misure = genera_misure()
    co = [m["valore"] for m in misure if m["id_sensore"] == "10004"]
    pm10 = [m["valore"] for m in misure if m["id_sensore"] == "10001"]

    assert max(co) < min(pm10)


def test_generazione_deterministica():
    assert genera_misure() == genera_misure()


def test_prima_e_ultima_data():
    misure = genera_misure()

    assert misure[0]["data"] == date(2025, 1, 1)
    assert misure[364]["data"] == date(2025, 12, 31)


# --- iniezione difetti --------------------------------------------------


def test_i_valori_non_disponibili_sono_marcati_na():
    misure, _ = inietta_difetti(genera_misure())
    non_validi = [m for m in misure if m["stato"] == "NA"]

    assert len(non_validi) > 0


def test_il_sensore_10004_ha_un_guasto_di_dodici_giorni_consecutivi():
    misure, _ = inietta_difetti(genera_misure())
    guasti = [m["data"] for m in misure
              if m["id_sensore"] == "10004" and m["stato"] == "NA"]
    consecutivi = [d for d in guasti if date(2025, 3, 3) <= d <= date(2025, 3, 14)]

    assert len(consecutivi) == 12


def test_i_duplicati_sono_esatti_e_contati():
    misure, manifest = inietta_difetti(genera_misure())
    viste = set()
    duplicati = 0
    for m in misure:
        chiave = (m["id_sensore"], m["data"])
        if chiave in viste:
            duplicati += 1
        viste.add(chiave)

    assert duplicati == 23
    assert manifest["righe_duplicate"] == 23


def test_le_righe_malformate_sono_in_posizioni_note():
    _, manifest = inietta_difetti(genera_misure())

    assert manifest["righe_malformate"] == len(RIGHE_MALFORMATE)
    assert RIGHE_MALFORMATE == [512, 1043, 1877, 2461, 3122, 3890, 4201]


def test_il_manifest_conta_le_righe_non_valide_come_stanno_nel_file():
    """Il conteggio va derivato dai dati finali, non da contatori.

    I duplicati vengono inseriti dopo l'iniezione dei valori non
    disponibili: un contatore incrementale non vede il duplicato di una
    riga NA e sbaglia di uno.
    """
    misure, manifest = inietta_difetti(genera_misure())
    non_valide_reali = sum(1 for m in misure if m["stato"] != "VA")

    assert manifest["righe_non_valide"] == non_valide_reali


def test_il_manifest_non_sottrae_due_volte_le_righe_malformate():
    """Una riga malformata puo' essere anche NA: va contata una volta sola."""
    misure, manifest = inietta_difetti(genera_misure())
    malformate = set(RIGHE_MALFORMATE)
    scartate = sum(
        1 for numero, m in enumerate(misure, start=1)
        if numero in malformate or m["stato"] != "VA"
    )

    assert manifest["righe_totali"] == len(misure)
    assert manifest["righe_valide_attese"] == len(misure) - scartate


def test_la_prima_riga_non_ascii_e_la_731():
    _, manifest = inietta_difetti(genera_misure())

    assert manifest["prima_riga_non_ascii"] == 731


def test_le_righe_in_taratura_sono_na_con_valore_plausibile():
    """Senza queste righe l'errore #2 non e' osservabile.

    Filtrare su valore >= 0 le lascia passare tutte, perche' il valore e'
    plausibile: solo la colonna Stato dice che non sono validate.
    """
    misure, manifest = inietta_difetti(genera_misure())
    taratura = [
        m for m in misure
        if m["id_sensore"] == "10001"
        and date(2025, 9, 8) <= m["data"] <= date(2025, 9, 12)
    ]

    assert len(taratura) == 5
    assert manifest["righe_in_taratura"] == 5
    assert all(m["stato"] == "NA" for m in taratura)
    assert all(m["valore"] > 0 for m in taratura)


# --- scrittura file -----------------------------------------------------


def test_il_file_misure_e_cp1252_e_non_utf8(tmp_path: Path):
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    grezzo = destinazione.read_bytes()

    assert b"\x96" in grezzo  # en dash di "Brescia - Villaggio Sereno"
    assert b"\xf9" in grezzo  # u con accento grave di "Cantu"
    try:
        grezzo.decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("il file deve rompersi se decodificato in UTF-8")


def test_intestazione_con_casing_incoerente(tmp_path: Path):
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    prima_riga = destinazione.read_bytes().split(b"\n")[0].decode("cp1252")

    assert prima_riga == (
        '"IdSensore","NomeStazione","Data","Valore","Stato","idOperatore"'
    )


def test_due_formati_di_data_convivono(tmp_path: Path):
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    with destinazione.open(encoding="cp1252", newline="") as f:
        righe = list(csv.DictReader(f))

    date_iso = [r["Data"] for r in righe if r["IdSensore"] == "10001"]
    date_excel = [r["Data"] for r in righe if r["IdSensore"] == "10008"]

    assert all(d.endswith("T00:00:00.000") for d in date_iso)
    assert all("/" in d for d in date_excel)


def test_virgola_decimale_solo_nel_secondo_export(tmp_path: Path):
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    with destinazione.open(encoding="cp1252", newline="") as f:
        righe = list(csv.DictReader(f))

    valori_primo = [r["Valore"] for r in righe if r["IdSensore"] == "10001"]
    valori_secondo = [r["Valore"] for r in righe if r["IdSensore"] == "10008"]

    assert not any("," in v for v in valori_primo)
    assert any("," in v for v in valori_secondo)


def test_le_righe_malformate_perdono_anche_stato(tmp_path: Path):
    """Quattro campi e non cinque.

    Con cinque campi sopravvivrebbe Stato, che e' fra quelli controllati
    dalla validazione, e la riga passerebbe per valida.
    """
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    with destinazione.open(encoding="cp1252", newline="") as f:
        righe = list(csv.reader(f))[1:]  # esclusa l'intestazione

    for numero_riga in RIGHE_MALFORMATE:
        assert len(righe[numero_riga - 1]) == 4


def test_le_righe_malformate_lette_come_dizionari_hanno_stato_nullo(tmp_path: Path):
    """E' cosi' che le vede la validazione: Stato assente, non stringa vuota."""
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    with destinazione.open(encoding="cp1252", newline="") as f:
        righe = list(csv.DictReader(f))

    for numero_riga in RIGHE_MALFORMATE:
        assert righe[numero_riga - 1]["Stato"] is None


def test_il_manifest_viene_scritto_accanto_al_csv(tmp_path: Path):
    destinazione = tmp_path / "rilevazioni.csv"
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, destinazione)

    scritto = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))

    assert scritto == manifest
