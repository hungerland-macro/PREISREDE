#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verbreitung: Anteil der Reden (ohne Präsidium, ab 300 Wörter) mit mindestens einem Preisniveau-Treffer,
je Jahr, 1949-2021 (Open Discourse). Ausgabe daten/verbreitung_reden.csv.
Aufruf: python verbreitung_reden.py PFAD/speeches.feather"""
import csv, os, sys
from collections import Counter, defaultdict
import pyarrow.feather as feather
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU, RX_WORT  # noqa: E402
t = feather.read_table(sys.argv[1], columns=["speech_content", "position_short", "date"])
c = defaultdict(Counter)
for txt, pos, d in zip(*(t.column(k).to_pylist() for k in ("speech_content", "position_short", "date"))):
    if d is None or pos == "Presidium of Parliament":
        continue
    txt = txt or ""
    if len(RX_WORT.findall(txt)) < 300:
        continue
    c[d.year]["reden"] += 1
    c[d.year]["mit_treffer"] += bool(RX_NIVEAU.search(txt))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "verbreitung_reden.csv"), "w", newline="") as o:
    w = csv.writer(o, delimiter=";"); w.writerow(["jahr", "reden", "mit_treffer", "anteil"])
    for j in sorted(c):
        w.writerow([j, c[j]["reden"], c[j]["mit_treffer"], round(c[j]["mit_treffer"] / c[j]["reden"], 4)])
print("fertig")
