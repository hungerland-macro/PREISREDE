#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preiswörter nach Fraktion und nach Regierung und Opposition, 1949 bis 2021.

Grundlage: Open Discourse (Richter et al., Harvard Dataverse, doi:10.7910/DVN/FIKIBO,
speeches.feather, Version 4), Reden mit Fraktion und Funktion des Redners.
Gezählt wird das Wortfeld Preisniveau wie in plenum_worte.py.

Regierungsseite: Reden von Mitgliedern der Bundesregierung (Funktion Minister oder
Kanzler) und von Abgeordneten der Koalitionsfraktionen am Tag der Rede. Reden des
Präsidiums und ohne Fraktion zählen weder zur Regierung noch zur Opposition.

Ausgabe: daten/fraktionen_od.csv (Jahr, Gruppe, Seite, Reden, Wörter, Treffer).
Aufruf: python fraktionen_od.py PFAD/speeches.feather PFAD/factions.tab
"""

import csv
import datetime as dt
import os
import sys
from collections import defaultdict

import pyarrow.feather as feather

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU, RX_WORT  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")

# Koalitionen nach Kabinettsbildung und Austritten (Bundesregierung, Kabinette seit 1949).
KOALITIONEN = [
    ("1949-09-20", {"CDU/CSU", "FDP", "DP"}),
    ("1953-10-20", {"CDU/CSU", "FDP", "DP", "GB/BHE"}),
    ("1955-07-12", {"CDU/CSU", "FDP", "DP"}),            # BHE verlässt die Koalition
    ("1956-02-23", {"CDU/CSU", "DP", "FVP"}),            # FDP verlässt die Koalition, FVP bleibt
    ("1957-10-29", {"CDU/CSU", "DP"}),
    ("1960-07-01", {"CDU/CSU"}),                         # DP-Minister treten zur CDU über
    ("1961-11-14", {"CDU/CSU", "FDP"}),
    ("1966-10-28", {"CDU/CSU"}),                         # FDP-Minister treten zurück
    ("1966-12-01", {"CDU/CSU", "SPD"}),
    ("1969-10-22", {"SPD", "FDP"}),
    ("1982-09-17", {"SPD"}),                             # FDP-Minister treten zurück
    ("1982-10-01", {"CDU/CSU", "FDP"}),
    ("1998-10-27", {"SPD", "Grüne"}),
    ("2005-11-22", {"CDU/CSU", "SPD"}),
    ("2009-10-28", {"CDU/CSU", "FDP"}),
    ("2013-12-17", {"CDU/CSU", "SPD"}),
    ("2021-12-08", {"SPD", "Grüne", "FDP"}),
]
GRUPPE = {"CDU/CSU": "CDU/CSU", "SPD": "SPD", "FDP": "FDP", "Grüne": "Grüne", "DIE LINKE.": "Linke/PDS",
          "PDS": "Linke/PDS", "AfD": "AfD"}


def koalition(d: dt.date) -> set:
    k = KOALITIONEN[0][1]
    for von, parteien in KOALITIONEN:
        if d >= dt.date.fromisoformat(von):
            k = parteien
    return k


def main(feather_pfad, fraktionen_pfad):
    fr = {}
    with open(fraktionen_pfad, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            fr[int(r["id"])] = r["abbreviation"]
    t = feather.read_table(feather_pfad, columns=["speech_content", "faction_id", "position_short", "date"])
    c = defaultdict(lambda: [0, 0, 0])
    for txt, fid, pos, d in zip(*(t.column(k).to_pylist() for k in ("speech_content", "faction_id", "position_short", "date"))):
        if d is None:
            continue
        txt = txt or ""
        f_ = fr.get(fid, "not found")
        regierung = pos in ("Minister", "Chancellor", "Secretary of State")
        if pos == "Presidium of Parliament":
            seite = "Präsidium"
        elif regierung or f_ in koalition(d):
            seite = "Regierung"
        elif f_ in ("not found", "Fraktionslos", "Gast"):
            seite = "ohne Zuordnung"
        else:
            seite = "Opposition"
        gruppe = GRUPPE.get(f_, "andere" if f_ not in ("not found", "Gast") else "ohne Fraktion")
        k = (d.year, gruppe, seite)
        c[k][0] += 1
        c[k][1] += len(RX_WORT.findall(txt))
        c[k][2] += len(RX_NIVEAU.findall(txt))
    with open(os.path.join(DATEN, "fraktionen_od.csv"), "w", newline="", encoding="utf-8") as o:
        w = csv.writer(o, delimiter=";")
        w.writerow(["jahr", "gruppe", "seite", "reden", "woerter", "treffer_preisniveau"])
        for k, v in sorted(c.items()):
            w.writerow([*k, *v])
    print("fertig")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
