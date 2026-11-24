#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Führt fraktionen_od.csv (1949-2021) und fraktionen_cpp.csv (2022-2026) zusammen.

Regierung und Opposition je Jahr; ab 2022 nach Koalitionsfraktionen am Jahresende
(Reden "ohne Fraktion", meist Regierungsmitglieder ohne Mandatsangabe, bleiben dort außen vor).
Ausgabe: daten/regierung_opposition.csv und abbildungen/Abb_Fraktionen.(pdf|png|svg).
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abbildungen_latex import plt, CM, INK, GRAU, rahmen, titel, speichern, komma  # noqa: E402
import abbildungen_latex as al

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
al.ZIEL = os.path.join(DATEN, "..", "abbildungen")
NAME = {"BÜNDNIS 90/DIE GRÜNEN": "Grüne", "DIE LINKE": "Linke/PDS"}
KOAL = {2022: {"SPD", "Grüne", "FDP"}, 2023: {"SPD", "Grüne", "FDP"}, 2024: {"SPD", "Grüne"},
        2025: {"CDU/CSU", "SPD"}, 2026: {"CDU/CSU", "SPD"}}
OPP = {"CDU/CSU", "SPD", "FDP", "Grüne", "Linke/PDS", "AfD", "BSW"}

z = {}
for r in csv.DictReader(open(os.path.join(DATEN, "fraktionen_od.csv"), encoding="utf-8"), delimiter=";"):
    j = int(r["jahr"])
    if j > 2021 or r["seite"] not in ("Regierung", "Opposition"):
        continue
    k = z.setdefault((j, r["seite"]), [0, 0]); k[0] += int(r["treffer_preisniveau"]); k[1] += int(r["woerter"])
for r in csv.DictReader(open(os.path.join(DATEN, "fraktionen_cpp.csv"), encoding="utf-8"), delimiter=";"):
    j = int(r["jahr"]); f = NAME.get(r["fraktion"], r["fraktion"])
    if j < 2022 or f not in OPP:
        continue
    s = "Regierung" if f in KOAL[j] else "Opposition"
    k = z.setdefault((j, s), [0, 0]); k[0] += int(r["treffer_preisniveau"]); k[1] += int(r["woerter"])
rate = {k: 1e6 * t / w for k, (t, w) in z.items() if w}
with open(os.path.join(DATEN, "regierung_opposition.csv"), "w", newline="", encoding="utf-8") as o:
    w = csv.writer(o, delimiter=";"); w.writerow(["jahr", "regierung_je_mio", "opposition_je_mio", "quelle"])
    for j in range(1949, 2027):
        w.writerow([j, round(rate.get((j, "Regierung"), 0), 1), round(rate.get((j, "Opposition"), 0), 1),
                    "Open Discourse" if j <= 2021 else "CPP-BT Reden"])

J = list(range(1949, 2026))
fig, (a, b) = plt.subplots(2, 1, figsize=(15 * CM, 8.6 * CM), sharex=True, gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.38})
o_, r_ = [rate[(j, "Opposition")] for j in J], [rate[(j, "Regierung")] for j in J]
a.plot(J, o_, color=INK, lw=1.1); a.plot(J, r_, color=GRAU, lw=1.1)
for s, c in (("Opposition", INK), ("Regierung", GRAU)):
    a.plot([2026], [rate[(2026, s)]], "o", ms=3.2, mfc="white", mec=c, mew=0.9)
top = max(o_ + r_)
rahmen(a, 0, top, [0, 300, 600, 900], xlab=False)
titel(a, "Preiswörter in Reden", "je Mio. Wörter")
a.annotate("Opposition", (1973, rate[(1973, "Opposition")]), xytext=(-4, 0), textcoords="offset points", ha="right", fontsize=7.5, color=INK)
a.annotate("Regierung\nund Koalition", (1981, rate[(1981, "Regierung")]), xytext=(4, 14), textcoords="offset points", fontsize=7.5, color=GRAU)
q = [rate[(j, "Opposition")] / rate[(j, "Regierung")] for j in J]
b.axhline(1, color=GRAU, lw=0.5)
b.plot(J, q, color=INK, lw=1.1)
rahmen(b, 0, 3.5, [0, 1, 2, 3], d=0)
titel(b, "Verhältnis Opposition zu Regierung", "1 = gleich viel")
speichern(fig, "Abb_Fraktionen")
print({j: (round(rate[(j,'Opposition')]), round(rate[(j,'Regierung')])) for j in (1951,1973,1974,1981,1992,2022,2023,2025,2026)})
