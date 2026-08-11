"""Genera il dataset didattico del Modulo 4.

Deterministico: stesso seed, stesso file, stessi difetti nelle stesse righe.
I numeri di riga citati nelle lezioni dipendono da questa proprieta'.

La struttura ricalca i dataset open data di ARPA Lombardia. Il file delle
misure e' un "export arricchito" con la colonna NomeStazione: realistico, e
necessario perche' la struttura ARPA pura non contiene testo, quindi non
avrebbe dove innescare l'errore di encoding.
"""

import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20250101

INTESTAZIONE_ANAGRAFICA = [
    "IdSensore", "NomeTipoSensore", "UnitaMisura", "IdStazione",
    "NomeStazione", "Quota", "Provincia", "Comune", "Storico",
    "DataStart", "DataStop", "lat", "lng",
]

SENSORI = [
    {"id": "10001", "inquinante": "PM10",  "unita": "µg/m³", "stazione": "Milano - Viale Marche",              "id_stazione": "501", "comune": "Milano",  "provincia": "MI", "quota": "122", "lat": "45.5012", "lng": "9.1934",  "data_stop": ""},
    {"id": "10002", "inquinante": "NO2",   "unita": "µg/m³", "stazione": "Milano - Viale Marche",              "id_stazione": "501", "comune": "Milano",  "provincia": "MI", "quota": "122", "lat": "45.5012", "lng": "9.1934",  "data_stop": ""},
    {"id": "10003", "inquinante": "PM10",  "unita": "µg/m³", "stazione": "Brescia – Villaggio Sereno",    "id_stazione": "502", "comune": "Brescia", "provincia": "BS", "quota": "149", "lat": "45.5089", "lng": "10.2011", "data_stop": ""},
    {"id": "10004", "inquinante": "CO",    "unita": "mg/m³",      "stazione": "Brescia – Villaggio Sereno",    "id_stazione": "502", "comune": "Brescia", "provincia": "BS", "quota": "149", "lat": "45.5089", "lng": "10.2011", "data_stop": ""},
    {"id": "10005", "inquinante": "PM10",  "unita": "µg/m³", "stazione": "Cantù - Via Meucci",            "id_stazione": "503", "comune": "Cantù",   "provincia": "CO", "quota": "369", "lat": "45.7401", "lng": "9.1330",  "data_stop": ""},
    {"id": "10006", "inquinante": "NO2",   "unita": "µg/m³", "stazione": "Cantù - Via Meucci",            "id_stazione": "503", "comune": "Cantù",   "provincia": "CO", "quota": "369", "lat": "45.7401", "lng": "9.1330",  "data_stop": ""},
    {"id": "10007", "inquinante": "PM2.5", "unita": "µg/m³", "stazione": "Monza - Parco",                      "id_stazione": "504", "comune": "Monza",   "provincia": "MB", "quota": "165", "lat": "45.6011", "lng": "9.2712",  "data_stop": ""},
    {"id": "10008", "inquinante": "O3",    "unita": "µg/m³", "stazione": "Monza - Parco",                      "id_stazione": "504", "comune": "Monza",   "provincia": "MB", "quota": "165", "lat": "45.6011", "lng": "9.2712",  "data_stop": ""},
    {"id": "10009", "inquinante": "PM10",  "unita": "µg/m³", "stazione": "Bergamo - Via Garibaldi",            "id_stazione": "505", "comune": "Bergamo", "provincia": "BG", "quota": "249", "lat": "45.6983", "lng": "9.6773",  "data_stop": ""},
    {"id": "10010", "inquinante": "CO",    "unita": "mg/m³",      "stazione": "Bergamo - Via Garibaldi",            "id_stazione": "505", "comune": "Bergamo", "provincia": "BG", "quota": "249", "lat": "45.6983", "lng": "9.6773",  "data_stop": ""},
    {"id": "10011", "inquinante": "PM2.5", "unita": "µg/m³", "stazione": "Cremona - Via Fatebenefratelli",     "id_stazione": "506", "comune": "Cremona", "provincia": "CR", "quota": "45",  "lat": "45.1335", "lng": "10.0227", "data_stop": ""},
    {"id": "10012", "inquinante": "O3",    "unita": "µg/m³", "stazione": "Cremona - Via Fatebenefratelli",     "id_stazione": "506", "comune": "Cremona", "provincia": "CR", "quota": "45",  "lat": "45.1335", "lng": "10.0227", "data_stop": "2025-06-30"},
]

# inquinante -> (minimo, massimo, mese di picco)
RANGE_INQUINANTI = {
    "PM10":  (12.0, 95.0, 1),
    "PM2.5": (6.0, 62.0, 1),
    "NO2":   (8.0, 72.0, 12),
    "O3":    (18.0, 125.0, 7),
    "CO":    (0.2, 2.1, 1),
}

PRIMO_GIORNO = date(2025, 1, 1)
ULTIMO_GIORNO = date(2025, 12, 31)

# Righe (1-based, intestazione esclusa) tagliate a meta': avranno 4 campi
# invece di 6. csv.reader non protesta, restituisce liste corte.
# Quattro e non cinque: con cinque campi sopravviverebbe anche Stato, che e'
# fra i campi che la validazione controlla, e la riga passerebbe per valida.
CAMPI_NELLE_RIGHE_MALFORMATE = 4
RIGHE_MALFORMATE = [512, 1043, 1877, 2461, 3122, 3890, 4201]

# Sensori il cui blocco proviene dal "secondo export": date in formato
# italiano e decimali con la virgola.
SENSORI_SECONDO_EXPORT = {"10007", "10008", "10009", "10010", "10011", "10012"}

QUOTA_NON_DISPONIBILI = 0.04
GUASTO_10004 = (date(2025, 3, 3), date(2025, 3, 14))
NUMERO_DUPLICATI = 23

# Righe marcate NA che conservano un valore plausibile: sensore in taratura
# o in verifica, che continua a trasmettere ma il cui dato non e' validato.
# Senza queste righe, scartare i valori negativi darebbe lo stesso risultato
# che leggere la colonna Stato, e la differenza fra i due criteri sarebbe
# invisibile. Sui dati reali quella differenza esiste.
TARATURA_10001 = (date(2025, 9, 8), date(2025, 9, 12))
VALORE_IN_TARATURA = 44.7

NOMI_COLONNE_MISURE = (
    "IdSensore", "NomeStazione", "Data", "Valore", "Stato", "idOperatore",
)


def scrivi_anagrafica(destinazione: Path) -> None:
    """Scrive l'anagrafica dei sensori in UTF-8, pulita.

    L'anagrafica e' l'unico appiglio semantico dello studente: se fosse
    sporca anche questa, non avrebbe un punto fermo da cui ragionare.
    """
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    with destinazione.open("w", encoding="utf-8", newline="") as f:
        scrittore = csv.writer(f)
        scrittore.writerow(INTESTAZIONE_ANAGRAFICA)
        for sensore in SENSORI:
            scrittore.writerow([
                sensore["id"],
                sensore["inquinante"],
                sensore["unita"],
                sensore["id_stazione"],
                sensore["stazione"],
                sensore["quota"],
                sensore["provincia"],
                sensore["comune"],
                "N",
                "2015-01-01",
                sensore["data_stop"],
                sensore["lat"],
                sensore["lng"],
            ])


def _giorni_dell_anno(fino_a: date = ULTIMO_GIORNO) -> list[date]:
    giorni = []
    corrente = PRIMO_GIORNO
    while corrente <= fino_a:
        giorni.append(corrente)
        corrente += timedelta(days=1)
    return giorni


def _valore_stagionale(
    giorno: date, minimo: float, massimo: float, mese_di_picco: int, rng: random.Random
) -> float:
    """Onda annuale con picco nel mese indicato, piu' rumore giornaliero."""
    distanza_dal_picco = (giorno.month - mese_di_picco) % 12
    if distanza_dal_picco > 6:
        distanza_dal_picco = 12 - distanza_dal_picco
    quota_stagionale = math.cos(math.pi * distanza_dal_picco / 6) * 0.5 + 0.5
    rumore = rng.uniform(-0.12, 0.12)
    posizione = min(1.0, max(0.0, quota_stagionale + rumore))
    return round(minimo + posizione * (massimo - minimo), 1)


def genera_misure() -> list[dict]:
    """Genera le misure pulite, ordinate per sensore e data.

    I difetti vengono iniettati dopo, da inietta_difetti().
    """
    rng = random.Random(SEED)
    misure = []
    for sensore in SENSORI:
        minimo, massimo, mese_di_picco = RANGE_INQUINANTI[sensore["inquinante"]]
        fine = date.fromisoformat(sensore["data_stop"]) if sensore["data_stop"] else ULTIMO_GIORNO
        for giorno in _giorni_dell_anno(fine):
            misure.append({
                "id_sensore": sensore["id"],
                "nome_stazione": sensore["stazione"],
                "data": giorno,
                "valore": _valore_stagionale(giorno, minimo, massimo, mese_di_picco, rng),
                "stato": "VA",
                "id_operatore": "1",
            })
    return misure


def inietta_difetti(misure: list[dict]) -> tuple[list[dict], dict]:
    """Sporca le misure e restituisce il manifest dei conteggi attesi.

    Ogni difetto esiste per far scattare una lezione precisa. Nessuno e'
    casuale, e le posizioni sono stabili fra esecuzioni.
    """
    rng = random.Random(SEED + 1)
    misure = [dict(m) for m in misure]

    # Difetto: valori non disponibili marcati -9999 / NA.
    inizio_guasto, fine_guasto = GUASTO_10004
    for m in misure:
        in_guasto = (
            m["id_sensore"] == "10004" and inizio_guasto <= m["data"] <= fine_guasto
        )
        if in_guasto or rng.random() < QUOTA_NON_DISPONIBILI:
            m["valore"] = -9999
            m["stato"] = "NA"

    # Difetto: duplicati esatti da ritrasmissione del datalogger.
    # Solo sul sensore 10009, che parte a riga 2921: inserire righe prima
    # della 731 sposterebbe la prima riga non-ASCII, che il copione della
    # L4 cita per numero.
    candidati = [i for i, m in enumerate(misure) if m["id_sensore"] == "10009"]
    da_duplicare = sorted(rng.sample(candidati, NUMERO_DUPLICATI))
    for scostamento, indice in enumerate(da_duplicare):
        misure.insert(indice + scostamento + 1, dict(misure[indice + scostamento]))

    # Difetto: taratura. Righe marcate NA che conservano un valore plausibile.
    # Rompono la coincidenza fra "valore negativo" e "dato non valido", su cui
    # l'AI si appoggia. Applicate dopo il ciclo precedente per non essere
    # sovrascritte dal -9999.
    inizio_taratura, fine_taratura = TARATURA_10001
    in_taratura = 0
    for m in misure:
        if m["id_sensore"] == "10001" and inizio_taratura <= m["data"] <= fine_taratura:
            if m["valore"] == -9999:
                m["valore"] = VALORE_IN_TARATURA
            m["stato"] = "NA"
            in_taratura += 1

    return misure, _calcola_manifest(misure, in_taratura)


def _calcola_manifest(misure: list[dict], in_taratura: int) -> dict:
    """Deriva i conteggi dai dati finali, non da contatori incrementali.

    I contatori incrementali sbagliano: i duplicati vengono inseriti dopo
    l'iniezione dei valori non disponibili, quindi un duplicato di una riga
    NA non finisce nel conteggio. E una riga malformata puo' essere anche
    NA, e verrebbe sottratta due volte.

    La validazione scarta una riga malformata per "campi mancanti" prima
    ancora di guardare Stato, quindi le due categorie non vanno sommate:
    vanno contate senza sovrapposizione.
    """
    malformate = set(RIGHE_MALFORMATE)
    non_valide = 0
    non_valide_non_malformate = 0
    for numero_riga, m in enumerate(misure, start=1):
        if m["stato"] == "VA":
            continue
        non_valide += 1
        if numero_riga not in malformate:
            non_valide_non_malformate += 1

    return {
        "righe_totali": len(misure),
        "righe_non_valide": non_valide,
        "righe_in_taratura": in_taratura,
        "righe_malformate": len(malformate),
        "righe_duplicate": NUMERO_DUPLICATI,
        "righe_valide_attese": (
            len(misure) - len(malformate) - non_valide_non_malformate
        ),
        "prima_riga_non_ascii": 731,
    }


def _formatta_data(giorno: date, id_sensore: str) -> str:
    if id_sensore in SENSORI_SECONDO_EXPORT:
        return giorno.strftime("%d/%m/%Y 00:00")
    return giorno.strftime("%Y-%m-%dT00:00:00.000")


def _formatta_valore(valore: float, id_sensore: str) -> str:
    testo = str(valore)
    if id_sensore in SENSORI_SECONDO_EXPORT:
        return testo.replace(".", ",")
    return testo


def _quota(campo: str) -> str:
    """Racchiude il campo fra virgolette, come fa l'export ARPA reale.

    Il quoting non e' cosmetico: i valori del secondo export usano la
    virgola decimale, e senza virgolette spezzerebbero il conteggio dei
    campi. Nessun campo contiene virgolette, quindi non serve escaping.
    """
    return f'"{campo}"'


def scrivi_misure(misure: list[dict], manifest: dict, destinazione: Path) -> None:
    """Scrive il CSV delle misure in cp1252 e il manifest accanto.

    Non usa csv.writer: le righe malformate devono avere cinque campi
    invece di sei, e un writer corretto non lo permetterebbe.
    """
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    da_troncare = set(RIGHE_MALFORMATE)

    linee = [",".join(_quota(nome) for nome in NOMI_COLONNE_MISURE)]
    for numero_riga, m in enumerate(misure, start=1):
        campi = [
            m["id_sensore"],
            m["nome_stazione"],
            _formatta_data(m["data"], m["id_sensore"]),
            _formatta_valore(m["valore"], m["id_sensore"]),
            m["stato"],
            m["id_operatore"],
        ]
        if numero_riga in da_troncare:
            campi = campi[:CAMPI_NELLE_RIGHE_MALFORMATE]
        linee.append(",".join(_quota(c) for c in campi))

    # Fine riga LF e non CRLF: git normalizza comunque i CRLF in commit, e
    # il file scaricato dallo studente sarebbe diverso da quello generato.
    # Nessuna lezione dipende dalle fine riga; il segnale "export Excel" lo
    # porta gia' la codifica cp1252.
    destinazione.write_bytes(("\n".join(linee) + "\n").encode("cp1252"))

    percorso_manifest = destinazione.parent / "manifest.json"
    percorso_manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> None:
    radice = Path(__file__).resolve().parent.parent / "data"
    scrivi_anagrafica(radice / "stazioni.csv")
    misure, manifest = inietta_difetti(genera_misure())
    scrivi_misure(misure, manifest, radice / "rilevazioni_2025.csv")
    print(f"Scritti {manifest['righe_totali']} record in {radice}")


if __name__ == "__main__":
    main()
