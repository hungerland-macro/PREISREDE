#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abbildungen 1 bis 3 der Note "Wann das Parlament über Preise spricht".

Liest plenum_jahr.csv (Preiswörter im Plenum), anfragen_jahr.csv (codierte
Anfragen) und inflation.csv (VPI-Jahresrate). Schreibt je Abbildung PDF, PNG
(300 dpi) und SVG. Im SVG bleibt die Schrift als Text erhalten, damit Word,
PowerPoint oder Illustrator sie mit Arial Narrow setzen, auch wenn diese Schrift
beim Rendern fehlt. Ist Arial Narrow installiert, nutzt das Skript sie direkt.

Aufruf: python abbildungen.py [Ausgabeordner]
"""

import csv
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
CM = 1 / 2.54
FARBE = ["#002060", "#0070C0", "#00B0F0", "#51154A", "#7030A0", "#D86DCD", "#47D359"]
GITTER, NULL = "#BFBFBF", "#FF0000"
SCHRIFTEN = ["Arial Narrow", "Liberation Sans Narrow", "DejaVu Sans Condensed"]
LETZTES_JAHR = 2025          # Korpus CPP-BT endet am 17.01.2026


def schrift_waehlen():
    da = {f.name for f in font_manager.fontManager.ttflist}
    for s in SCHRIFTEN:
        if s in da:
            return s
    return "DejaVu Sans"


def zahl(s):
    s = (s or "").strip().replace(",", ".")
    return float(s) if s not in ("", "NA") else None


def lies(name):
    with open(os.path.join(HIER, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def daten():
    plenum = {int(r["jahr"]): zahl(r["preisniveau_je_mio_woerter"]) for r in lies("plenum_jahr.csv")
              if int(r["jahr"]) <= LETZTES_JAHR}
    infl = {int(r["jahr"]): zahl(r["vpi_rate"]) for r in lies("inflation.csv")}
    anf = {int(r["jahr"]): r for r in lies("anfragen_jahr.csv") if int(r["jahr"]) <= LETZTES_JAHR}
    return plenum, infl, anf


def fenster(jahre, zaehler, nenner, breite=5):
    """Zentriertes Fenster: Summe der Treffer je 1000 Anfragen im Fenster."""
    h, out = breite // 2, []
    for i in range(len(jahre)):
        lo, hi = max(0, i - h), min(len(jahre), i + h + 1)
        z = sum(zaehler[jahre[k]] for k in range(lo, hi))
        n = sum(nenner[jahre[k]] for k in range(lo, hi))
        out.append(1000.0 * z / n if n else 0.0)
    return out


def komma(x):
    return f"{x:g}".replace(".", ",")


def achsen(ax, ax2, gr, yl, yr, einh_l, einh_r):
    for sp in list(ax.spines.values()) + list(ax2.spines.values()):
        sp.set_visible(False)
    for a in (ax, ax2):
        a.tick_params(length=0, labelsize=gr, pad=2)
    ax.yaxis.tick_left()
    ax2.yaxis.tick_right()
    ax.set_yticks(yl)
    ax2.set_yticks(yr)
    ax.set_yticklabels([komma(v) for v in yl[:-1]] + [f"{komma(yl[-1])} {einh_l}"])
    ax2.set_yticklabels([komma(v) for v in yr[:-1]] + [f"{komma(yr[-1])} {einh_r}"])
    for y in yl:
        ax.axhline(y, color=GITTER, lw=0.25, zorder=0)
    for x in range(1950, 2030, 10):
        ax.axvline(x, color="#F2F2F2", lw=0.25, zorder=0)
    ax.set_xlim(1949, LETZTES_JAHR)
    ax.set_xticks(list(range(1950, 2030, 10)))
    ax.set_xticklabels([str(j) for j in range(1950, 2030, 10)])


def legende(ax, linien, gr):
    ax.legend(linien, [l.get_label() for l in linien], loc="lower left",
              bbox_to_anchor=(-0.02, 1.0), ncol=1, frameon=False, fontsize=gr,
              handlelength=1.1, borderpad=0, handletextpad=0.4, labelspacing=0.15)


def speichern(fig, ziel, name, schrift):
    fig.patch.set_facecolor("white")
    for ext in ("pdf", "png", "svg"):
        pfad = os.path.join(ziel, f"{name}.{ext}")
        fig.savefig(pfad, dpi=300 if ext == "png" else None)
        if ext == "svg":     # Schriftfamilie im SVG fest auf Arial Narrow setzen
            t = open(pfad, encoding="utf-8").read()
            t = re.sub(r"font-family:\s*'?[^;'\"]+'?", "font-family: 'Arial Narrow', 'Liberation Sans Narrow', sans-serif", t)
            t = re.sub(r'font-family="[^"]+"', "font-family=\"'Arial Narrow', 'Liberation Sans Narrow', sans-serif\"", t)
            open(pfad, "w", encoding="utf-8").write(t)
    plt.close(fig)


def abbildung1(plenum, infl, ziel, schrift, b=15.0, h=6.0, gr=8, lw=3.5):
    jahre = sorted(plenum)
    xi = [j for j in sorted(infl) if j <= LETZTES_JAHR]
    fig, ax = plt.subplots(figsize=(b * CM, h * CM))
    ax2 = ax.twinx()
    ax.set_ylim(-333, 444)            # Null beider Achsen auf gleicher Höhe
    ax2.set_ylim(-7.5, 10)            # Platz für 1950 (-6,4 %)
    achsen(ax, ax2, gr, [0, 100, 200, 300, 400], [-6, -3, 0, 3, 6, 9], "je Mio. Wörter", "%")
    ax2.axhline(0, color=NULL, lw=0.25, zorder=1)
    p1, = ax2.plot(xi, [infl[j] for j in xi], color=FARBE[0], lw=lw, zorder=3,
                   solid_capstyle="round", label="Inflationsrate, Jahresdurchschnitt (rechts)")
    p2, = ax.plot(jahre, [plenum[j] for j in jahre], color=FARBE[2], lw=lw, zorder=2,
                  solid_capstyle="round", label="Preiswörter im Plenum (links)")
    legende(ax, [p1, p2], gr)
    fig.subplots_adjust(left=0.20, right=0.94, top=0.80, bottom=0.10)
    speichern(fig, ziel, "Abb1_Plenum_Inflation", schrift)


def abbildung2(plenum, anf, ziel, schrift, b=15.0, h=6.0, gr=8, lw=3.5):
    """Jahreswerte als Säulen: Die Reihe ist dünn (17 Anfragen), ein gleitendes
    Fenster würde die Treffer von 1971/72 in die Jahre 1973/74 verschmieren."""
    jahre = sorted(plenum)
    ja = sorted(anf)
    werte = [1000.0 * (int(anf[j]["preisniveau"]) + int(anf[j]["messung"]))
             / int(anf[j]["anfragen_gesamt"]) for j in ja]
    fig, ax = plt.subplots(figsize=(b * CM, h * CM))
    ax2 = ax.twinx()
    ax.set_ylim(0, 11.1)
    ax2.set_ylim(0, 444)
    achsen(ax, ax2, gr, [0, 2.5, 5, 7.5, 10], [0, 100, 200, 300, 400], "je 1000 Anfragen", "je Mio. Wörter")
    ax.bar(ja, werte, width=0.8, color=FARBE[3], zorder=3,
           label="Anfragen zu Preisniveau und Messung, je Jahr (links)")
    p1, = ax2.plot(jahre, [plenum[j] for j in jahre], color=FARBE[2], lw=lw, zorder=2,
                   solid_capstyle="round", label="Preiswörter im Plenum (rechts)")
    from matplotlib.patches import Patch
    p2 = Patch(color=FARBE[3], label="Anfragen zu Preisniveau und Messung, je Jahr (links)")
    legende(ax, [p1, p2], gr)
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    fig.subplots_adjust(left=0.20, right=0.80, top=0.80, bottom=0.10)
    speichern(fig, ziel, "Abb2_Instrumente", schrift)


def abbildung3(infl, anf, ziel, schrift, b=15.0, h=6.0, gr=8, lw=3.5):
    ja = sorted(anf)
    nenner = {j: int(anf[j]["anfragen_gesamt"]) for j in ja}
    ms = {j: int(anf[j]["preisniveau"]) + int(anf[j]["messung"]) for j in ja}
    e = {j: int(anf[j]["einzelne_preise"]) for j in ja}
    xi = [j for j in sorted(infl) if j <= LETZTES_JAHR]
    fig, ax = plt.subplots(figsize=(b * CM, h * CM))
    ax2 = ax.twinx()
    ax.set_ylim(-10, 13.33)
    ax2.set_ylim(-7.5, 10)
    achsen(ax, ax2, gr, [0, 4, 8, 12], [-6, -3, 0, 3, 6, 9], "je 1000 Anfragen", "%")
    ax2.axhline(0, color=NULL, lw=0.25, zorder=1)
    p1, = ax2.plot(xi, [infl[j] for j in xi], color=FARBE[0], lw=lw, zorder=4,
                   solid_capstyle="round", label="Inflationsrate, Jahresdurchschnitt (rechts)")
    p2, = ax.plot(ja, fenster(ja, e, nenner), color=FARBE[2], lw=lw, zorder=2,
                  solid_capstyle="round", label="Anfragen zu einzelnen Preisen (links)")
    p3, = ax.plot(ja, fenster(ja, ms, nenner), color=FARBE[3], lw=lw, zorder=3,
                  solid_capstyle="round", label="Anfragen zu Preisniveau und Messung (links)")
    legende(ax, [p1, p2, p3], gr)
    fig.subplots_adjust(left=0.20, right=0.94, top=0.74, bottom=0.10)
    speichern(fig, ziel, "Abb3_Anfragen_nach_Art", schrift)


def datenmappe(plenum, infl, anf, ziel):
    """Zahlen hinter den Abbildungen als xlsx, ein Blatt je Abbildung."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    ja = sorted(anf)
    nenner = {j: int(anf[j]["anfragen_gesamt"]) for j in ja}
    ms = {j: int(anf[j]["preisniveau"]) + int(anf[j]["messung"]) for j in ja}
    e = {j: int(anf[j]["einzelne_preise"]) for j in ja}
    f_ms, f_e = dict(zip(ja, fenster(ja, ms, nenner))), dict(zip(ja, fenster(ja, e, nenner)))
    jahre = sorted(plenum)
    wb = Workbook()
    blaetter = [
        ("Abb1", ["Jahr", "Preiswörter je Mio. Wörter", "Inflationsrate in %"],
         [[j, plenum[j], infl.get(j)] for j in jahre]),
        ("Abb2", ["Jahr", "Preiswörter je Mio. Wörter", "Anfragen zu Preisniveau und Messung je 1000 Anfragen"],
         [[j, plenum[j], round(1000 * ms[j] / nenner[j], 2) if j in ja else None] for j in jahre]),
        ("Abb3", ["Jahr", "Anfragen zu einzelnen Preisen je 1000, Fünfjahresfenster",
                  "Anfragen zu Preisniveau und Messung je 1000, Fünfjahresfenster", "Inflationsrate in %"],
         [[j, round(f_e[j], 2) if j in ja else None, round(f_ms[j], 2) if j in ja else None, infl.get(j)]
          for j in jahre]),
    ]
    ws = wb.active
    for i, (name, kopf, zeilen) in enumerate(blaetter):
        ws = ws if i == 0 else wb.create_sheet()
        ws.title = name
        ws.append(kopf)
        for c in ws[1]:
            c.font = Font(bold=True)
        for z in zeilen:
            ws.append(z)
    q = wb.create_sheet("Quellen")
    for z in [["Plenum", "Fobbe, S. (2026), CPP-BT, Version 2026-01-17, Zenodo, doi:10.5281/zenodo.18177196, CC0; eigene Zählung"],
              ["Anfragen", "Deutscher Bundestag, DIP, Abruf 01.11.2026; eigene Codierung"],
              ["Inflation bis 1991", "Statistisches Bundesamt, Lange Reihen ab 1948 (12/2022), Preisindex für die Lebenshaltung, 4-Personen-Haushalte von Arbeitern und Angestellten mit mittlerem Einkommen, früheres Bundesgebiet"],
              ["Inflation ab 1992", "Statistisches Bundesamt, VPI Deutschland 2020 = 100, über Bundesbank BBDP1.A.DE.N.VPI.C.A00000.I20.A"]]:
        q.append(z)
    wb.save(os.path.join(ziel, "Abbildungen_Daten.xlsx"))


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "..", "abbildungen")
    os.makedirs(ziel, exist_ok=True)
    schrift = schrift_waehlen()
    plt.rcParams["font.family"] = schrift
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plenum, infl, anf = daten()
    abbildung1(plenum, infl, ziel, schrift)
    abbildung2(plenum, anf, ziel, schrift)
    abbildung3(infl, anf, ziel, schrift)
    datenmappe(plenum, infl, anf, ziel)
    print(f"Schrift: {schrift}. Abbildungen in {ziel}")
    if schrift != "Arial Narrow":
        print("Hinweis: Arial Narrow nicht gefunden. PDF/PNG nutzen Ersatzschrift, "
              "die SVG-Dateien verlangen Arial Narrow beim Öffnen.")
