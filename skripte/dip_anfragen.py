#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
dip_anfragen.py
===============
Zieht alle Kleinen und Grossen Anfragen des Bundestages ueber die DIP-Schnittstelle
und baut daraus je Jahr den Nenner (alle Anfragen) und die Trefferliste
(Titel mit Preis- oder Inflationswort, historisches Vokabular eingeschlossen).

Ausgabe: index.csv (Treffer mit Titel und Drucksache), jahr.csv (Nenner je Jahr).
Die Treffer wurden danach von Hand codiert, siehe ../daten/anfragen_codierung.csv.

ABHAENGIGKEIT: pip install requests
AUFRUF: python dip_anfragen.py --out ./korpus_preise [--apikey KEY]
Der voreingestellte Schluessel ist der oeffentliche Schluessel, den der Bundestag
unter https://dip.bundestag.de/ueber-dip/hilfe/api veroeffentlicht; er wird
regelmaessig erneuert.
"""

import argparse
import csv
import os
import re
import sys
import time
from collections import defaultdict

import requests

API = "https://search.dip.bundestag.de/api/v1"
PUBLIC_KEY = "R2BZaee.DjdCyihKZMf8AOjtScubP2EVydegzjmBIQ"
PAUSE, TIMEOUT, MAX_SEITEN = 0.2, 60, 8000
TYPEN = ["Kleine Anfrage", "Große Anfrage"]
KERN_FENSTER = 60

CORE = ["inflation", "deflation", "disinflation", "stagflation", "inflationaer", "inflationär",
        "verbraucherpreis", "preisstabilität", "preisniveau", "preisauftrieb", "kaufkraft",
        "lebenshaltungskosten", "geldentwertung", "geldwertstabilität", "geldwert", "warenkorb"]
HIST = ["lebenshaltung", "preisindex", "kaufkraftverlust", "kaufkraftschwund",
        "geldwertsicherung", "waehrungsverfall", "währungsverfall", "preissteigerung",
        "preiserhöhung", "preisanstieg", "preisentwicklung", "preisstopp", "preiskontrolle",
        "preisueberwachung", "preisüberwachung", "preisbindung", "preisgesetz",
        "preisstatistik", "preiserhebung", "preismessung", "preisbeobachtung",
        "qualitätsbereinigung", "hedonisch", "wertsicherungsklausel", "indexklausel",
        "gleitklausel", "stabilitätspolitik", "geldwertstabil", "scheingewinn",
        "inflationsgewinn", "importierte inflation", "weltinflation"]
ACR = re.compile(r"\b(vpi|hvpi|cpi)\b", re.IGNORECASE)
TEUERUNG = re.compile(r"(?<![sS])teuerung", re.IGNORECASE)   # nicht Besteuerung, Steuerung
EXCLUDE = ["kaufkraftparität"]


def treffer(titel):
    low = (titel or "").lower()
    if any(b in low for b in EXCLUDE):
        return None, False
    hits = [(low.find(k), k) for k in CORE + HIST if k in low]
    m = TEUERUNG.search(titel or "")
    if m:
        hits.append((m.start(), "preisbegriff"))
    m = ACR.search(titel or "")
    if m:
        hits.append((m.start(), m.group(1).lower()))
    if not hits:
        return None, False
    pos, kw = min(hits)
    return kw, pos < KERN_FENSTER


def seiten(sess, params, key):
    params, letzter = dict(params), None
    for _ in range(MAX_SEITEN):
        for versuch in range(4):
            r = sess.get(f"{API}/drucksache", params={**params, "apikey": key, "format": "json"},
                         timeout=TIMEOUT)
            if r.status_code == 200:
                break
            if r.status_code == 401:
                sys.exit("HTTP 401: API-Schluessel abgelaufen, aktuellen mit --apikey uebergeben.")
            time.sleep(5)
        else:
            sys.exit(f"HTTP {r.status_code}")
        data = r.json()
        docs = data.get("documents") or []
        yield from docs
        cur = data.get("cursor")
        if not docs or cur is None or cur == letzter:
            return
        letzter = params["cursor"] = cur
        time.sleep(PAUSE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./korpus_preise")
    ap.add_argument("--apikey", default=PUBLIC_KEY)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sess = requests.Session()
    gesamt, zeilen = defaultdict(int), []
    for typ in TYPEN:
        print(f"[.] {typ}")
        for d in seiten(sess, {"f.zuordnung": "BT", "f.drucksachetyp": typ}, a.apikey):
            j = (d.get("datum") or "")[:4]
            if not j:
                continue
            gesamt[(j, typ)] += 1
            kw, kern = treffer(d.get("titel"))
            if kw:
                u = d.get("urheber")
                u = "; ".join(x.get("titel", "") for x in u) if isinstance(u, list) else (u or "")
                zeilen.append([d.get("datum", ""), "Frage", typ, d.get("dokumentnummer", ""),
                               u, d.get("titel", ""), kw, "ja" if kern else "nein"])
    with open(os.path.join(a.out, "index.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["datum", "rolle", "drucksachetyp", "dokumentnummer", "urheber", "titel",
                    "stichwort", "kern"])
        w.writerows(sorted(zeilen))
    with open(os.path.join(a.out, "jahr.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahr", "drucksachetyp", "anfragen_gesamt"])
        for j in sorted({j for j, _ in gesamt}):
            for t in TYPEN:
                if gesamt.get((j, t)):
                    w.writerow([j, t, gesamt[(j, t)]])
            w.writerow([j, "alle Anfragen", sum(v for (jj, _), v in gesamt.items() if jj == j)])
    print(f"[ok] {len(zeilen)} Treffer, Ausgabe in {a.out}")


if __name__ == "__main__":
    main()
