#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zählt mehrere Wortfelder je Jahr in drei Textgrundlagen (Prüfungen der Revision).

Grundlagen:
  protokolle  CPP-BT Plenarprotokolle, ganzer Text einschließlich Anlagen (wie die Hauptreihe)
  od          Open Discourse, nur Redetext, 1949-2021
  cppreden    CPP-BT Reden-Datensatz, nur Redetext, 2013-2026

Wortfelder: Preisniveau (wie plenum_worte.py), Messung, Placebos für andere Makrothemen
(Arbeitslosigkeit, Haushalt, Wachstum, Bundeswehr/Verteidigung), Energiepreise und
Entlastung, Geldpolitik und Zins, Wechselkurs/importierte Inflation, Inflationsausgleich.
Ausgabe: daten/wortfelder_<grundlage>.csv (Jahr, Wörter, Treffer je Feld).

Aufruf: python wortfelder.py protokolle PFAD/CPP-BT_..._Plenarprotokolle_Gesamt.zip
        python wortfelder.py od PFAD/speeches.feather
        python wortfelder.py cppreden PFAD/CPP-BT_..._Reden_Gesamt.zip
"""
import csv, io, os, re, sys, zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU, RX_MESSUNG, RX_WORT  # noqa: E402

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten")
F = lambda *m: re.compile(r"\b(?:" + "|".join(m) + r")\b", re.I)
FELDER = {
    "preisniveau": RX_NIVEAU,
    "messung": RX_MESSUNG,
    "arbeitslosigkeit": F(r"arbeitslos\w*", r"erwerbslos\w*", r"beschäftigungslos\w*"),
    "haushalt": F(r"bundeshaushalt\w*", r"haushaltsdefizit\w*", r"staatsverschuldung\w*", r"neuverschuldung\w*", r"haushaltsplan\w*"),
    "wachstum": F(r"wirtschaftswachstum\w*", r"konjunktur\w*", r"rezession\w*", r"bruttoinlandsprodukt\w*", r"sozialprodukt\w*"),
    "verteidigung": F(r"bundeswehr\w*", r"verteidigung\w*"),
    "energiepreise": F(r"energiepreis\w*", r"strompreis\w*", r"gaspreis\w*", r"ölpreis\w*", r"heizölpreis\w*", r"benzinpreis\w*",
                       r"heizkosten\w*", r"\w*preisbremse\w*", r"entlastungspaket\w*", r"tankrabatt\w*"),
    "geldpolitik": F(r"geldpolitik\w*", r"leitzins\w*", r"nullzins\w*", r"niedrigzins\w*", r"negativzins\w*", r"anleihekäuf\w*",
                     r"anleihekauf\w*", r"zinspolitik\w*", r"diskontsatz\w*", r"geldmenge\w*"),
    "wechselkurs": F(r"aufwertung\w*", r"importiert\w*\s+inflation\w*", r"wechselkurs\w*", r"dollarkurs\w*"),
    "stabilitaetsinstrumente": F(r"konzertiert\w*\s+aktion\w*", r"stabilitätsgesetz\w*", r"preisstopp\w*", r"preiskontroll\w*",
                                 r"lohnleitlini\w*", r"orientierungsdat\w*", r"preisüberwachung\w*", r"preisbindung\w*"),
    "inflationsausgleich": F(r"inflationsausgleich\w*"),
}


def zaehle(c, j, t):
    c[j]["woerter"] += len(RX_WORT.findall(t))
    for k, rx in FELDER.items():
        c[j][k] += len(rx.findall(t))


def main(art, pfad):
    c = defaultdict(Counter)
    csv.field_size_limit(2 ** 31 - 1)
    if art == "od":
        import pyarrow.feather as feather
        tab = feather.read_table(pfad, columns=["speech_content", "date"])
        for t, d in zip(tab.column("speech_content").to_pylist(), tab.column("date").to_pylist()):
            if d is not None:
                zaehle(c, d.year, t or "")
    else:
        z = zipfile.ZipFile(pfad)
        f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
        feld = "text" if art == "protokolle" else "rede_text"
        for r in csv.DictReader(f):
            zaehle(c, int(r["sitzung_jahr"]), r[feld] or "")
    with open(os.path.join(DATEN, f"wortfelder_{art}.csv"), "w", newline="", encoding="utf-8") as o:
        w = csv.writer(o, delimiter=";")
        w.writerow(["jahr", "woerter", *FELDER])
        for j in sorted(c):
            w.writerow([j, c[j]["woerter"], *(c[j][k] for k in FELDER)])
    print("fertig", art)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
