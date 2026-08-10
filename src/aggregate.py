"""Aggrega le rilevazioni.

Versione attesa dall'AI, da confermare in registrazione. Contiene l'errore #4.
"""


def media_mensile(rilevazioni: list) -> dict:
    gruppi = {}
    for rilevazione in rilevazioni:
        mese = rilevazione["data"].strftime("%Y-%m")
        chiave = rilevazione["nome_stazione"] + "|" + mese
        if chiave not in gruppi:
            gruppi[chiave] = []
        gruppi[chiave].append(rilevazione["valore"])

    medie = {}
    for chiave in gruppi:
        valori = gruppi[chiave]
        medie[chiave] = sum(valori) / len(valori)
    return medie
