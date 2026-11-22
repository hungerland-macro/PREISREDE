#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abbildungen der LaTeX-Fassung: kleine Vielfache statt zweiter Achse (Tufte).

Jede Abbildung hat Felder mit gemeinsamer Zeitachse; jede Größe hat ihre eigene
Skala in ihrer eigenen Einheit. Daten-Tinte schwarz, Kontext grau, direkte
Beschriftung statt Legende, Achsen nur über den Datenbereich (range frame).
Das laufende Jahr 2026 (Januar bis September) steht als hohler Punkt.

Schrift: TeX Gyre Heros Condensed (frei, metrisch nahe an Helvetica Condensed;
Ersatz für Arial Narrow). Ausgabe als PDF mit eingebetteter Schrift.

Aufruf: python abbildungen_latex.py [Ausgabeordner]
"""

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(HIER, "..", "daten")
ZIEL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "..", "latex", "abbildungen")
LAUFEND = (2026, 2.6)        # Jan.–Sep. 2026, VPI gegen Vorjahreszeitraum (Bundesbank BBDP1, Monatswerte)
EREIGNISSE = [(1957.56, "1"), (1967.43, "2"), (1973.21, "3"), (1979.0, "4"), (1990.75, "5"),
              (1999.0, "6"), (2008.7, "7"), (2020.17, "8"), (2022.15, "9")]
CM = 1 / 2.54
INK, GRAU, HELL = "#111111", "#8c8c8c", "#d9d9d9"

for f in font_manager.findSystemFonts():
    if "texgyreheroscn" in f.lower():
        font_manager.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "TeX Gyre Heros Cn", "font.size": 8, "axes.linewidth": 0.5,
    "axes.edgecolor": GRAU, "xtick.color": GRAU, "ytick.color": GRAU, "xtick.labelcolor": INK,
    "ytick.labelcolor": INK, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "pdf.fonttype": 42, "axes.unicode_minus": False,
})


def lies(name):
    with open(os.path.join(DATEN, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def zahl(s):
    return float(s.replace(",", "."))


def komma(v, d=0):
    return f"{v:.{d}f}".replace(".", ",").replace("-", "−")


P = {int(r["jahr"]): zahl(r["preisniveau_je_mio_woerter"]) for r in lies("plenum_jahr.csv")}
I = {int(r["jahr"]): float(r["vpi_rate"]) for r in lies("inflation.csv")}
A = {int(r["jahr"]): r for r in lies("anfragen_jahr.csv")}
JP = [j for j in sorted(P) if j <= 2025]
JI = [j for j in sorted(I) if j <= 2025]
JA = [j for j in sorted(A) if j <= 2025]


def rahmen(ax, y0, y1, ticks, d=0, x0=1949, x1=2026, xlab=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_bounds(y0, y1)
    ax.spines["bottom"].set_bounds(x0, x1)
    ax.set_yticks(ticks)
    ax.set_yticklabels([komma(t, d) for t in ticks])
    ax.set_xlim(1947.5, 2027.5)
    ax.set_xticks([1949, 1960, 1973, 1990, 1999, 2010, 2022])
    if not xlab:
        ax.tick_params(labelbottom=False)


def titel(ax, text, einheit):
    """Fetter Titel, daneben die Einheit in Grau; die Einheit beginnt dort, wo der Titel endet."""
    t = ax.text(0.0, 1.05, text, transform=ax.transAxes, fontsize=9, fontweight="bold", color=INK, va="bottom")
    fig = ax.figure
    fig.canvas.draw()
    bb = t.get_window_extent().transformed(ax.transAxes.inverted())
    ax.text(bb.x1 + 0.008, 1.05, einheit, transform=ax.transAxes, fontsize=8, color=GRAU, va="bottom")


def ereignisse(axes, oben):
    for x, n in EREIGNISSE:
        for ax in axes:
            ax.axvline(x, color=HELL, lw=0.6, ls=(0, (2, 2)), zorder=0, ymax=1.0)
        oben.plot([x, x], [1.0, 1.19], transform=oben.get_xaxis_transform(), color=HELL, lw=0.6, ls=(0, (2, 2)), clip_on=False, zorder=0)
        oben.annotate(n, xy=(x, 1.2), xycoords=("data", "axes fraction"), xytext=(-3.5 if n == "8" else 3.5 if n == "9" else 0, 0),
                      textcoords="offset points", ha="center", va="bottom", fontsize=6.5, color=GRAU)
    for ax in axes:
        for x, n in EREIGNISSE:
            pass
    oben.annotate("", xy=(0, 1.2), xycoords="axes fraction")


def speichern(fig, name):
    os.makedirs(ZIEL, exist_ok=True)
    fig.savefig(os.path.join(ZIEL, name + ".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(ZIEL, name + ".png"), dpi=300, bbox_inches="tight", pad_inches=0.02)
    with plt.rc_context({"svg.fonttype": "path"}):  # Schrift als Pfade: sieht überall gleich aus, auch ohne installierte Schrift
        fig.savefig(os.path.join(ZIEL, name + ".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def abb1():
    fig, (a, b) = plt.subplots(2, 1, figsize=(15 * CM, 9.2 * CM), sharex=True,
                               gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.38})
    a.plot(JP, [P[j] for j in JP], color=INK, lw=1.1, solid_joinstyle="round")
    a.plot([LAUFEND[0]], [P[2026]], "o", ms=3.2, mfc="white", mec=INK, mew=0.9)
    rahmen(a, 0, 372, [0, 100, 200, 300, 372], xlab=False)
    titel(a, "Preiswörter im Plenum", "je Mio. Wörter")
    for j, dx, dy in ((1973, -4, 4), (2022, -4, 4)):
        a.annotate(f"{j}: {komma(P[j])}", (j, P[j]), xytext=(dx, dy), textcoords="offset points", ha="right", fontsize=7.5, color=INK)
    a.annotate(f"2017: {komma(P[2017], 1)}", (2017, P[2017]), xytext=(-3, 10), textcoords="offset points", ha="right", fontsize=7.5, color=INK)
    a.annotate(f"Jan.–Sep. 2026: {komma(P[2026])}", (2026, P[2026]), xytext=(4, -3), textcoords="offset points", ha="left", va="top", fontsize=7.5, color=INK)
    b.annotate(f"Jan.–Sep. 2026: {komma(LAUFEND[1], 1)}", (2026, LAUFEND[1]), xytext=(4, -3), textcoords="offset points", ha="left", va="top", fontsize=7.5, color=INK)
    b.axhline(0, color=GRAU, lw=0.5)
    b.plot(JI, [I[j] for j in JI], color=INK, lw=1.1, solid_joinstyle="round")
    b.plot([LAUFEND[0]], [LAUFEND[1]], "o", ms=3.2, mfc="white", mec=INK, mew=0.9)
    rahmen(b, -6.4, 7.6, [-6, -3, 0, 3, 6], x0=1950)
    titel(b, "Inflationsrate", "% gegenüber Vorjahr")
    b.annotate("Währungsreform,\nKorea-Boom", (1951, 7.6), xytext=(5, -2), textcoords="offset points", fontsize=7, color=GRAU, va="top")
    ereignisse([a, b], a)
    speichern(fig, "Abb1_Plenum_Inflation")


def abb2():
    fig, (a, b) = plt.subplots(2, 1, figsize=(15 * CM, 8.6 * CM), sharex=True,
                               gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.38})
    a.plot(JP, [P[j] for j in JP], color=INK, lw=1.1)
    rahmen(a, 0, 372, [0, 100, 200, 300, 372], xlab=False)
    titel(a, "Preiswörter im Plenum", "je Mio. Wörter")
    a.axvspan(1972.5, 1975.5, color="#f0f0f0", lw=0, zorder=0)
    a.annotate("1973 bis 1975:\nkeine Anfrage", (1975.6, 300), fontsize=7, color=GRAU, va="top")
    w = [1000 * (int(A[j]["preisniveau"]) + int(A[j]["messung"])) / int(A[j]["anfragen_gesamt"]) for j in JA]
    b.bar(JA, w, width=0.75, color=INK, lw=0)
    b.axvspan(1972.5, 1975.5, color="#f0f0f0", lw=0, zorder=0)
    rahmen(b, 0, 8.5, [0, 2, 4, 6, 8])
    titel(b, "Anfragen zu Preisniveau und Messung", "je 1000 Anfragen des Jahres")
    speichern(fig, "Abb2_Instrumente")


def fenster(z, n, breite=5):
    h, out = breite // 2, []
    for i in range(len(JA)):
        lo, hi = max(0, i - h), min(len(JA), i + h + 1)
        out.append(1000 * sum(z[JA[k]] for k in range(lo, hi)) / sum(n[JA[k]] for k in range(lo, hi)))
    return out


def abb3():
    n = {j: int(A[j]["anfragen_gesamt"]) for j in JA}
    ms = {j: int(A[j]["preisniveau"]) + int(A[j]["messung"]) for j in JA}
    e = {j: int(A[j]["einzelne_preise"]) for j in JA}
    fig, (a, b) = plt.subplots(2, 1, figsize=(15 * CM, 8.6 * CM), sharex=True,
                               gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.38})
    ye, ym = fenster(e, n), fenster(ms, n)
    a.plot(JA, ye, color=INK, lw=1.1)
    a.plot(JA, ym, color=GRAU, lw=1.1)
    rahmen(a, 0, 12, [0, 4, 8, 12], xlab=False)
    titel(a, "Anfragen nach Gegenstand", "je 1000 Anfragen, gleitendes Fünfjahresmittel")
    a.annotate("einzelne Preise\nund Preisrecht", (1957, ye[JA.index(1957)]), xytext=(8, -2), textcoords="offset points", fontsize=7.5, color=INK, va="top")
    a.annotate("Preisniveau und Messung", (1972, ym[JA.index(1972)]), xytext=(6, 8), textcoords="offset points", fontsize=7.5, color=GRAU)
    b.axhline(0, color=GRAU, lw=0.5)
    b.plot(JI, [I[j] for j in JI], color=INK, lw=1.1)
    rahmen(b, -6.4, 7.6, [-6, -3, 0, 3, 6], x0=1950)
    titel(b, "Inflationsrate", "% gegenüber Vorjahr")
    speichern(fig, "Abb3_Anfragen_nach_Art")


if __name__ == "__main__":
    abb1()
    abb2()
    abb3()
    print("Abbildungen in", ZIEL)
