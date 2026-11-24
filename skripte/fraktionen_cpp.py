#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preiswörter je Fraktion, 2013 bis 2026, aus dem Reden-Datensatz des CPP-BT.

Zählt das Wortfeld Preisniveau (wie plenum_worte.py) in jeder Rede und ordnet
sie der Fraktion des Redners zu. Reden ohne Fraktion (Regierungsmitglieder ohne
Mandatsangabe, Präsidium) laufen als "ohne Fraktion". Ausgabe: daten/fraktionen_cpp.csv
mit Jahr, Fraktion, Wörtern und Treffern.

Aufruf: python fraktionen_cpp.py PFAD/CPP-BT_2026-09-19_DE_CSV_Reden_Gesamt.zip
"""

import csv
import io
import os
import sys
import zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU, RX_WORT  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")


def main(pfad):
    csv.field_size_limit(2 ** 31 - 1)
    z = zipfile.ZipFile(pfad)
    f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
    c = defaultdict(lambda: [0, 0, 0])
    for r in csv.DictReader(f):
        fr = r["redner_fraktion"]
        fr = "ohne Fraktion" if fr in ("NA", "") else fr
        t = r["rede_text"] or ""
        k = (int(r["sitzung_jahr"]), fr)
        c[k][0] += len(RX_WORT.findall(t))
        c[k][1] += len(RX_NIVEAU.findall(t))
        c[k][2] += 1
    with open(os.path.join(DATEN, "fraktionen_cpp.csv"), "w", newline="", encoding="utf-8") as o:
        w = csv.writer(o, delimiter=";")
        w.writerow(["jahr", "fraktion", "reden", "woerter", "treffer_preisniveau"])
        for (j, fr), (n, t, r) in sorted(c.items()):
            w.writerow([j, fr, r, n, t])
    print("fertig")


if __name__ == "__main__":
    main(sys.argv[1])
