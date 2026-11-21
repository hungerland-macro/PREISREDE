#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
plenum_worte.py
===============
Misst, wie oft im Plenum des Bundestages ueber Preise geredet wurde, Jahr fuer
Jahr von 1949 bis heute.

Grundlage ist das Corpus der Plenarprotokolle des Deutschen Bundestages
(CPP-BT) von Sean Fobbe, Fassung 2026-09-19, Lizenz CC0, 4.653 Protokolle als CSV in einem
ZIP-Archiv (rund 830 MB, nicht Teil dieses Repos). Das Skript laedt das Archiv
einmalig von Zenodo, liest es ohne Entpacken, zaehlt je Protokoll die Woerter
und die Treffer zweier Wortfelder und schreibt zwei Tabellen.

Ausgabe im Zielordner:
  plenum_jahr.csv         Jahr, Protokolle, Woerter, Treffer, Treffer je Mio. Woerter
  plenum_protokolle.csv   je Protokoll eine Zeile mit denselben Groessen

ABHAENGIGKEIT: keine, nur die Standardbibliothek.

AUFRUF:
    python plenum_worte.py --out ../daten
    python plenum_worte.py --zip PFAD/CPP-BT_2026-09-19_DE_CSV_Plenarprotokolle_Gesamt.zip
"""

import argparse
import csv
import io
import os
import re
import sys
import urllib.request
import zipfile
from collections import defaultdict

ZENODO = "https://zenodo.org/records/22844952/files/"
ARCHIV = "CPP-BT_2026-09-19_DE_CSV_Plenarprotokolle_Gesamt.zip"
QUELLE = ZENODO + ARCHIV + "?download=1"

# Wortfelder. Gesucht wird im laufenden Text: nur Woerter, die das Preisniveau
# als Gesamtgroesse oder seine Messung meinen.
FELD_NIVEAU = [
    r"inflation\w*", r"deflation\w*", r"stagflation\w*",
    r"geldentwertung\w*", r"geldwertstabilit\w+", r"geldwertsicherung\w*",
    r"preisniveau\w*", r"preisstabilit\w+", r"preisauftrieb\w*",
    r"kaufkraftverlust\w*", r"kaufkraftschwund\w*",
    r"lebenshaltungskosten", r"preissteigerungsrate\w*",
    r"(?<![sS])teuerungsrate\w*", r"(?<![sS])teuerungswelle\w*",
]
FELD_MESSUNG = [
    r"preisindex\w*", r"verbraucherpreisindex\w*", r"preisstatistik\w*",
    r"warenkorb\w*", r"lebenshaltungsindex\w*", r"indexziffer\w*",
]
RX_NIVEAU = re.compile(r"\b(?:" + "|".join(FELD_NIVEAU) + r")\b", re.IGNORECASE)
RX_MESSUNG = re.compile(r"\b(?:" + "|".join(FELD_MESSUNG) + r")\b", re.IGNORECASE)
RX_JAHR = re.compile(r"(?:^|\D)((?:19|20)\d{2})(?:\D|$)")
RX_WORT = re.compile(r"\w+", re.UNICODE)


def laden(ziel):
    """Laedt das Archiv, wenn es noch nicht im Ordner liegt."""
    if os.path.exists(ziel) and os.path.getsize(ziel) > 10_000_000:
        print(f"[i] Archiv liegt schon vor: {ziel}")
        return ziel
    print(f"[.] Lade {ARCHIV} von Zenodo, rund 830 MB. Das dauert.")
    with urllib.request.urlopen(QUELLE) as r, open(ziel, "wb") as out:
        gesamt = int(r.headers.get("Content-Length") or 0)
        geladen = 0
        while True:
            block = r.read(1024 * 512)
            if not block:
                break
            out.write(block)
            geladen += len(block)
            if gesamt:
                sys.stdout.write(f"\r    {geladen / 1e6:7.0f} von {gesamt / 1e6:.0f} MB")
                sys.stdout.flush()
    print("\n[ok] geladen.")
    return ziel


def spalten_finden(kopf, erste_zeilen):
    """Bestimmt Datums- und Textspalte, ohne auf feste Namen zu bauen."""
    tief = {n.lower(): i for i, n in enumerate(kopf)}
    datum_i = None
    for name in ("datum", "date", "sitzungsdatum", "datum_sitzung"):
        if name in tief:
            datum_i = tief[name]
            break
    text_i = None
    for name in ("text", "volltext", "inhalt", "sitzungsverlauf", "body"):
        if name in tief:
            text_i = tief[name]
            break
    if text_i is None and erste_zeilen:               # laengstes Feld gewinnt
        laenge = [0] * len(kopf)
        for z in erste_zeilen:
            for i, w in enumerate(z[:len(kopf)]):
                laenge[i] += len(w or "")
        text_i = laenge.index(max(laenge))
    if datum_i is None and erste_zeilen:              # Spalte mit Jahreszahl
        for i in range(len(kopf)):
            werte = [z[i] for z in erste_zeilen if i < len(z)]
            if werte and all(RX_JAHR.search(w or "") for w in werte):
                datum_i = i
                break
    return datum_i, text_i


def jahr_aus(wert):
    m = RX_JAHR.search(wert or "")
    return int(m.group(1)) if m else None


def auswerten(zip_pfad, out_dir):
    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    je_jahr = defaultdict(lambda: {"prot": 0, "woerter": 0, "niveau": 0, "messung": 0})
    zeilen = []

    with zipfile.ZipFile(zip_pfad) as z:
        namen = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not namen:
            sys.exit("[!] Im Archiv liegt keine CSV-Datei.")
        for nr, name in enumerate(sorted(namen), 1):
            print(f"[.] {nr}/{len(namen)}: {name}")
            with z.open(name) as roh:
                strom = io.TextIOWrapper(roh, encoding="utf-8", errors="replace", newline="")
                kopfzeile = strom.readline()
                trenn = max([",", ";", "\t"], key=kopfzeile.count)
                strom.seek(0)
                leser = csv.reader(strom, delimiter=trenn)
                try:
                    kopf = next(leser)
                except StopIteration:
                    continue
                probe = []
                for _ in range(5):
                    try:
                        probe.append(next(leser))
                    except StopIteration:
                        break
                datum_i, text_i = spalten_finden(kopf, probe)
                if text_i is None:
                    print("    [!] keine Textspalte erkannt, uebersprungen.")
                    continue
                for zeile in list(probe) + list(leser):
                    if text_i >= len(zeile):
                        continue
                    text = zeile[text_i] or ""
                    jahr = (jahr_aus(zeile[datum_i])
                            if datum_i is not None and datum_i < len(zeile) else None)
                    if jahr is None:
                        jahr = jahr_aus(" ".join(zeile[:4]))
                    if jahr is None:
                        continue
                    woerter = len(RX_WORT.findall(text))
                    n = len(RX_NIVEAU.findall(text))
                    m = len(RX_MESSUNG.findall(text))
                    e = je_jahr[jahr]
                    e["prot"] += 1
                    e["woerter"] += woerter
                    e["niveau"] += n
                    e["messung"] += m
                    zeilen.append([jahr, woerter, n, m])

    pfad_jahr = os.path.join(out_dir, "plenum_jahr.csv")
    with open(pfad_jahr, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahr", "protokolle", "woerter", "treffer_preisniveau",
                    "treffer_messung", "preisniveau_je_mio_woerter",
                    "messung_je_mio_woerter"])
        for j in sorted(je_jahr):
            e = je_jahr[j]
            mio = e["woerter"] / 1e6 if e["woerter"] else 0
            w.writerow([j, e["prot"], e["woerter"], e["niveau"], e["messung"],
                        f"{e['niveau'] / mio:.1f}".replace(".", ",") if mio else "",
                        f"{e['messung'] / mio:.1f}".replace(".", ",") if mio else ""])

    pfad_prot = os.path.join(out_dir, "plenum_protokolle.csv")
    with open(pfad_prot, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["jahr", "woerter", "treffer_preisniveau", "treffer_messung"])
        w.writerows(zeilen)
    print(f"\n[ok] {len(zeilen)} Protokolle ausgewertet: {pfad_jahr}, {pfad_prot}")


def main():
    ap = argparse.ArgumentParser(description="Preiswoerter in den Plenarprotokollen zaehlen.")
    ap.add_argument("--zip", default=None, help="schon geladenes Archiv")
    ap.add_argument("--out", default=".", help="Zielordner der Tabellen")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pfad = args.zip or laden(os.path.join(args.out, ARCHIV))
    auswerten(pfad, args.out)


if __name__ == "__main__":
    main()
