#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zählt alternative Preiswörter (Preissteigerung, Teuerung, steigende/hohe Preise,
Preiserhöhung, Preisanstieg) je Jahr, um zu prüfen, ob sich der Wortgebrauch nach
1990 vom Wortfeld weg verschoben hat. Aufruf: python alternativwoerter.py PFAD/cpp.zip"""
import csv,io,re,sys,zipfile
from collections import Counter,defaultdict
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plenum_worte import RX_WORT
csv.field_size_limit(2**31-1)
ALT=re.compile(r"\b(?:preissteigerung(?:en)?|(?<![sS])teuerung(?:en)?|steigende[nm]?\s+preis\w*|preiserhöhung\w*|preisanstieg\w*|hohe[nm]?\s+preis\w*)\b",re.I)
c=defaultdict(Counter)
z=zipfile.ZipFile(sys.argv[1]); f=io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8',newline='')
for r in csv.DictReader(f):
    j=int(r['sitzung_jahr']); t=r['text'] or ''
    c[j]['w']+=len(RX_WORT.findall(t)); c[j]['alt']+=len(ALT.findall(t))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daten', 'validierung_alternativwoerter.csv'), 'w') as o:
    o.write('jahr;woerter;treffer_alternativ;alternativ_je_mio\n')
    for j in sorted(c): o.write(f"{j};{c[j]['w']};{c[j]['alt']};{c[j]['alt']/c[j]['w']*1e6:.1f}\n")
