#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wertet die blinden Zweitcodierungen der Trefferstichprobe aus.

Erwartet im Ordner daten/zweitcodierung die Antworten als lauf1.csv, lauf2.csv, ...
(Spalten id;kategorie;sicherheit;begruendung) und den Schlüssel schluessel.csv.
Gibt je Lauf die Übereinstimmung mit der Erstcodierung und Cohens Kappa aus,
dazu Fleiss' Kappa über alle Codierer und die Fälle mit Abweichung.

Aufruf: python zweitcodierung_auswerten.py
"""

import csv
import glob
import os
from collections import Counter

ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "zweitcodierung")
KAT = ["A", "S", "M"]


def lies(pfad):
    with open(pfad, encoding="utf-8-sig") as f:
        zeilen = [z for z in f if z.strip() and not z.startswith("```")]
    return {r["id"].strip(): r["kategorie"].strip().upper()
            for r in csv.DictReader(zeilen, delimiter=";")}


def cohen(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in KAT) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def fleiss(urteile):
    """urteile: Liste je Fall mit den Kategorien aller Codierer."""
    n, k = len(urteile), len(urteile[0])
    p_j = {c: sum(u.count(c) for u in urteile) / (n * k) for c in KAT}
    p_i = [(sum(u.count(c) ** 2 for c in KAT) - k) / (k * (k - 1)) for u in urteile]
    pbar, pe = sum(p_i) / n, sum(v ** 2 for v in p_j.values())
    return (pbar - pe) / (1 - pe)


if __name__ == "__main__":
    schl = {r["id"]: r for r in csv.DictReader(open(os.path.join(ORDNER, "schluessel.csv")), delimiter=";")}
    ids = sorted(schl)
    erst = [schl[i]["urteil_erstcodierung"] for i in ids]
    laeufe = sorted(glob.glob(os.path.join(ORDNER, "lauf*.csv")))
    if not laeufe:
        raise SystemExit("Keine Dateien lauf1.csv, lauf2.csv ... im Ordner daten/zweitcodierung.")
    alle = [erst]
    for p in laeufe:
        d = lies(p)
        fehlt = [i for i in ids if i not in d]
        if fehlt:
            raise SystemExit(f"{os.path.basename(p)}: es fehlen {fehlt}")
        z = [d[i] for i in ids]
        po, kappa = cohen(erst, z)
        print(f"{os.path.basename(p)}: Übereinstimmung {po:.0%}, Cohens Kappa {kappa:.2f}, "
              f"Anteil A {z.count('A') / len(z):.0%}")
        alle.append(z)
    if len(alle) > 2:
        print(f"Fleiss' Kappa über {len(alle)} Codierer: {fleiss(list(zip(*alle))):.2f}")
    print("\nAbweichungen von der Erstcodierung:")
    for n, i in enumerate(ids):
        werte = [a[n] for a in alle[1:]]
        if any(w != erst[n] for w in werte):
            print(f"   {i} ({schl[i]['jahr']}): erst {erst[n]}, Läufe {' '.join(werte)}")
