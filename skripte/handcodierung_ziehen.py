#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zieht die Stichprobe für die menschliche Codierung.

Teil A (Präzision): 30 zufällige Treffer des Wortfelds Preisniveau, drei je Jahrzehnt.
Teil B (Vollständigkeit): 30 zufällige Stellen mit allgemeinen Preiswörtern
(Preis..., Teuerung, teurer, Kosten des Lebens), die das Wortfeld NICHT trifft, drei je Jahrzehnt.
Gefragt wird jeweils: Meint die Stelle das allgemeine Preisniveau oder die Inflation?
Reihenfolge gemischt, Teil nicht sichtbar; der Schlüssel liegt getrennt.
Aufruf: python handcodierung_ziehen.py PFAD/CPP-BT_..._Plenarprotokolle_Gesamt.zip
"""
import csv, io, os, random, re, sys, zipfile
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_NIVEAU  # noqa: E402

ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "daten", "handcodierung")
RX_ALLG = re.compile(r"\b(?:\w*preis\w*|teuerung\w*|teurer\w*|verteuer\w*|lebenshaltung\w*)\b", re.I)
JE = 3
random.seed(20261125)


def main(pfad):
    csv.field_size_limit(2 ** 31 - 1)
    res = {"A": defaultdict(list), "B": defaultdict(list)}
    gesehen = {"A": defaultdict(int), "B": defaultdict(int)}
    z = zipfile.ZipFile(pfad)
    f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
    for r in csv.DictReader(f):
        j = int(r["sitzung_jahr"])
        if j > 2025:
            continue
        t = r["text"] or ""
        d = j // 10 * 10
        niveau = [(m.start(), m.end()) for m in RX_NIVEAU.finditer(t)]
        kand = {"A": niveau, "B": [(m.start(), m.end()) for m in RX_ALLG.finditer(t)
                                   if not any(a - 300 < m.start() < b + 300 for a, b in niveau)]}
        for teil, liste in kand.items():
            for a, b in liste:
                gesehen[teil][d] += 1
                k = random.randrange(gesehen[teil][d])
                if len(res[teil][d]) < JE or k < JE:
                    x, y = max(0, a - 250), min(len(t), b + 250)
                    e = (j, r["protokoll_nr"] if "protokoll_nr" in r else "", re.sub(r"\s+", " ", t[x:y]), t[a:b])
                    if len(res[teil][d]) < JE:
                        res[teil][d].append(e)
                    else:
                        res[teil][d][k] = e
    alle = [(teil, *e) for teil in res for d in res[teil] for e in res[teil][d]]
    random.shuffle(alle)
    os.makedirs(ZIEL, exist_ok=True)
    with open(os.path.join(ZIEL, "codierbogen.csv"), "w", newline="", encoding="utf-8-sig") as o, \
         open(os.path.join(ZIEL, "schluessel.csv"), "w", newline="", encoding="utf-8") as s:
        w, ws = csv.writer(o, delimiter=";"), csv.writer(s, delimiter=";")
        w.writerow(["id", "jahr", "textstelle", "preisniveau_ja_nein", "anmerkung"])
        ws.writerow(["id", "teil", "jahr", "protokoll", "suchwort"])
        for i, (teil, j, p, ctx, wort) in enumerate(alle, 1):
            w.writerow([i, j, ctx, "", ""])
            ws.writerow([i, teil, j, p, wort])
    print("fertig", len(alle))


if __name__ == "__main__":
    main(sys.argv[1])
