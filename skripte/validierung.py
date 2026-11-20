#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prüft das Wortfeld Preisniveau auf dem Korpus CPP-BT.

1. Zählt die Treffer neu und vergleicht sie mit daten/plenum_jahr.csv.
2. Zerlegt die Treffer je Jahr nach Wortstamm und weist Komposita aus, die nur
   mittelbar das Preisniveau meinen (Inflationsausgleich..., Inflation Reduction Act).
3. Zieht je Jahrzehnt eine Zufallsstichprobe von Treffern mit Kontext zum Lesen
   (Precision des Wortfelds).
4. Zählt ein Placebo-Wortfeld (Bundeswehr, Verteidigung), das nicht von der
   Inflation abhängen sollte.

Aufruf: python validierung.py PFAD/CPP-BT_2026-01-17_DE_CSV_Plenarprotokolle_Gesamt.zip
"""

import csv
import io
import os
import random
import re
import sys
import zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU, RX_WORT  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
RX_MITTELBAR = re.compile(r"\binflationsausgleich\w*|\binflation\s+reduction\s+act\b", re.IGNORECASE)
RX_PLACEBO = re.compile(r"\b(?:bundeswehr\w*|verteidigung\w*)\b", re.IGNORECASE)
JE_JAHRZEHNT = 20
random.seed(20261120)


def main(zip_pfad):
    csv.field_size_limit(2 ** 31 - 1)
    jahr = defaultdict(lambda: Counter())
    stamm = defaultdict(Counter)
    kandidaten = defaultdict(list)          # Jahrzehnt -> (jahr, protokoll, kontext)
    gesehen = Counter()
    with zipfile.ZipFile(zip_pfad) as z:
        f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
        for r in csv.DictReader(f):
            j = int(r["sitzung_jahr"])
            t = r["text"] or ""
            c = jahr[j]
            c["protokolle"] += 1
            c["woerter"] += len(RX_WORT.findall(t))
            treffer = list(RX_NIVEAU.finditer(t))
            c["niveau"] += len(treffer)
            c["mittelbar"] += len(RX_MITTELBAR.findall(t))
            c["placebo"] += len(RX_PLACEBO.findall(t))
            for m in treffer:
                w = m.group(0).lower()
                stamm[j][re.sub(r"(inflation|preis\w{4}|geld\w{5}|kaufkraft|lebenshaltung|teuerung|deflation|stagflation).*", r"\1", w)] += 1
                d = j // 10 * 10
                gesehen[d] += 1          # Reservoir-Stichprobe, gleichmäßig über das Jahrzehnt
                k = len(kandidaten[d]) if len(kandidaten[d]) < JE_JAHRZEHNT else random.randrange(gesehen[d])
                if k < JE_JAHRZEHNT:
                    a, b = max(0, m.start() - 160), min(len(t), m.end() + 160)
                    eintrag = (j, r["protokoll_nr"], m.group(0), re.sub(r"\s+", " ", t[a:b]))
                    if len(kandidaten[d]) < JE_JAHRZEHNT:
                        kandidaten[d].append(eintrag)
                    else:
                        kandidaten[d][k] = eintrag

    alt = {int(r["jahr"]): r for r in csv.DictReader(open(os.path.join(DATEN, "plenum_jahr.csv"),
                                                          encoding="utf-8-sig"), delimiter=";")}
    with open(os.path.join(DATEN, "validierung_jahr.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahr", "protokolle", "woerter", "treffer_preisniveau", "davon_mittelbar",
                    "preisniveau_ohne_mittelbar_je_mio", "placebo_je_mio", "abweichung_zu_plenum_jahr"])
        for j in sorted(jahr):
            c = jahr[j]
            mio = c["woerter"] / 1e6
            diff = c["niveau"] - int(alt[j]["treffer_preisniveau"]) if j in alt else ""
            w.writerow([j, c["protokolle"], c["woerter"], c["niveau"], c["mittelbar"],
                        round((c["niveau"] - c["mittelbar"]) / mio, 1), round(c["placebo"] / mio, 1), diff])

    with open(os.path.join(DATEN, "validierung_stichprobe.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahrzehnt", "jahr", "protokoll", "treffer", "kontext", "urteil"])
        for d in sorted(kandidaten):
            for j, p, tr, k in sorted(kandidaten[d]):
                w.writerow([d, j, p, tr, k, ""])

    with open(os.path.join(DATEN, "validierung_staemme.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahr", "stamm", "treffer"])
        for j in sorted(stamm):
            for s, n in stamm[j].most_common():
                w.writerow([j, s, n])
    print("fertig")


if __name__ == "__main__":
    main(sys.argv[1])
