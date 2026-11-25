#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zählt jedes Muster des Wortfelds Preisniveau einzeln je Jahr (Protokolle CPP-BT).
Erlaubt Reihen ohne einzelne Begriffe, etwa ohne Preisstabilität und Geldwertstabilität.
Ausgabe: daten/wortfeld_terme.csv. Aufruf: python wortfeld_terme.py PFAD/CPP-BT_..._Plenarprotokolle_Gesamt.zip"""
import csv, io, os, re, sys, zipfile
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import FELD_NIVEAU, RX_WORT  # noqa: E402
RX = [(m, re.compile(r"\b(?:" + m + r")\b", re.I)) for m in FELD_NIVEAU]
DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
csv.field_size_limit(2 ** 31 - 1)
c = defaultdict(Counter)
z = zipfile.ZipFile(sys.argv[1]); f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
for r in csv.DictReader(f):
    j = int(r["sitzung_jahr"]); t = r["text"] or ""
    c[j]["woerter"] += len(RX_WORT.findall(t))
    for m, rx in RX:
        c[j][m] += len(rx.findall(t))
with open(os.path.join(DATEN, "wortfeld_terme.csv"), "w", newline="", encoding="utf-8") as o:
    w = csv.writer(o, delimiter=";"); w.writerow(["jahr", "woerter", *[m for m, _ in RX]])
    for j in sorted(c):
        w.writerow([j, c[j]["woerter"], *[c[j][m] for m, _ in RX]])
print("fertig")
