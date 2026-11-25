#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wertet die blinden Modellcodierungen der 54 Stellen aus (daten/handcodierung/modelle/lauf*.csv).

Teil A = Treffer des Wortfelds: Anteil J ist die Trefferqualität (Präzision).
Teil B = Stellen mit allgemeinen Preiswörtern ohne Treffer: Anteil J sind übersehene
Preisniveau-Stellen. Daraus eine grobe Schätzung, wie viele Preisniveau-Stellen das Wortfeld verfehlt.
Aufruf: python handcodierung_auswerten.py
"""
import csv, glob, os
from collections import Counter

O = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "handcodierung")


def lies(p):
    z = [x for x in open(p, encoding="utf-8-sig") if x.strip() and not x.startswith("```")]
    return {r["id"].strip().lstrip("P").lstrip("0"): r["kategorie"].strip().upper() for r in csv.DictReader(z, delimiter=";")}


k = {r["id"]: r for r in csv.DictReader(open(os.path.join(O, "schluessel.csv")), delimiter=";")}
L = {os.path.basename(p): lies(p) for p in sorted(glob.glob(os.path.join(O, "modelle", "lauf*.csv")))}
for n, d in L.items():
    fehlt = [i for i in k if i not in d]
    a = [d[i] for i in k if k[i]["teil"] == "A" and i in d]; b = [d[i] for i in k if k[i]["teil"] == "B" and i in d]
    print(f"{n}: fehlend {fehlt}; Teil A J {a.count('J')}/{len(a)}; Teil B J {b.count('J')}/{len(b)}")
mehr = {i: Counter(d[i] for d in L.values() if i in d).most_common(1)[0][0] for i in k}
a = [mehr[i] for i in k if k[i]["teil"] == "A"]; b = [mehr[i] for i in k if k[i]["teil"] == "B"]
print(f"Mehrheit: Präzision {a.count('J')}/{len(a)}, übersehene Preisniveau-Stellen in Teil B {b.count('J')}/{len(b)}")
for i in k:
    if k[i]["teil"] == "B" and mehr[i] == "J":
        print("   übersehen:", i, k[i]["jahr"], k[i]["suchwort"])
