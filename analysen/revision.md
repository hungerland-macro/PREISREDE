# Prüfungen nach den Gutachten vom 25.11.2026

Kurzbericht zu den Rechnungen, die in die überarbeitete Fassung eingegangen sind. Skripte: `skripte/schaetzung_revision.py`, `skripte/wortfelder.py`.

## Modell

Spalte 2 der ersten Fassung (Veränderungen, Anstieg und Rückgang getrennt, Bruch 1990) ist ersetzt. Ihre Konstante ab 1990 (−0,253) ließ sich nicht als Trend lesen. Rückgänge gingen dort mit negativem Vorzeichen ein. Neu ist ein Niveaumodell mit Vorjahreswert (Fehlerkorrekturform), in dem ein Bruch Niveau und Steigung verschiebt.

## Ergebnisse

| Prüfung | Langfristwert bei 2 % vor → ab Bruch | Steigung zusätzlich ab Bruch (p) |
|---|---|---|
| Bruch 1999 | 70 → 34 | 0,240 (0,000) |
| Bruch 1990 | 76 → 33 | 0,142 (0,110) |
| Bruch 2002 (vom Test gewählt, p = 0,001) | 70 → 30 | 0,256 (0,000) |
| Index aller Haushalte, 1964–2025 | 74 → 34 | 0,232 (0,000) |
| nur Redetext | 82 → 45 | 0,255 (0,000) |
| ohne 2021–23 | 70 → 29 | 0,138 (0,099) |
| ohne 1951–52 und 2021–23 | 73 → 30 | 0,125 (0,119) |
| ohne 1951–52 und 2021–23, Bruch 1990 | 79 → 29 | −0,008 (0,883) |

Das halbierte Grundniveau hält in allen Fällen. Die steilere Reaktion nach dem Bruch hängt an 2022.

## Nenner und Placebos

Median in Jahren mit Rate unter 3 %, ab 1999 im Verhältnis zu davor:

| Feld | Protokoll | nur Redetext |
|---|---:|---:|
| Preisniveau | 0,42 | 0,49 |
| Arbeitslosigkeit | 0,74 | 0,98 |
| Haushalt | 0,67 | 0,86 |
| Wachstum | 0,73 | 0,92 |
| Verteidigung | 0,74 | 0,86 |
| Energiepreise, Preisbremsen | 3,89 | 5,06 |
| Geldpolitik, Zins | 1,27 | 1,54 |
| Wechselkurs, Aufwertung | 0,40 | 0,41 |
| Preis- und Lohnsteuerung | 0,15 | 0,15 |

Gemessen an Arbeitslosigkeit, Haushalt und Wachstum bleibt der Niveaubruch gesichert (Protokoll ohne die Episoden p = 0,04; Redetext p = 0,01).

## Weitere Punkte

- Nach dem Schub: 2025 lag die Reihe beim 2,4-Fachen des Mittels 2015–2020. Die Aussage der ersten Fassung, das Parlament vergesse schneller als Haushalte, ist gestrichen.
- Kappa der Trefferstichprobe: 0,90 mit allen, 0,88 ohne die blinde Claude-Codierung, 0,93 unter ChatGPT, Gemini und DeepSeek allein.
- Das Inflationsausgleichsgesetz fällt unter dieselbe Prüfung wie die Prämie (Suchmuster `inflationsausgleich…`).
- 1969 erreichten Aufwertung und Wechselkurs 259 Treffer je Million Wörter, vor dem Sprung der Preisrede 1970.
- Schwelle: zum Absatz herabgestuft (Mindestbesetzung, p = 0,14).
- Menschliche Codierung: Bogen in `daten/handcodierung/`, Ergebnis steht aus.

## Vollständigkeit (Modellprüfung, 25.11.2026)

54 Stellen, blind bewertet von Gemini, Claude, DeepSeek, Grok und ChatGPT (`daten/handcodierung/modelle/`, gespeichert sind Kennung und Kategorie). Fleiss' Kappa 0,96.

- Teil A, 27 Treffer des Wortfelds: 24 meinen das Preisniveau (89 %).
- Teil B, 27 Stellen mit allgemeinen Preiswörtern ohne Treffer: 1 meint das Preisniveau (Teuerungszulagen, 1953; 95-%-Intervall 0,1 % bis 19 %).
- Hochrechnung 1949–2025: 23.475 Treffer, davon rund 20.900 richtig; 131.098 Stellen ohne Treffer, davon geschätzt rund 4.900 zum Preisniveau. Vollständigkeit rund 81 %, Spanne etwa 46 % bis nahezu 100 %.
- Die übersehene Stelle liegt vor 1990; in den 12 Stellen ab 2000 keine. Kein Hinweis, dass das Wortfeld nach dem Bruch mehr verfehlt.

## Zweite Gutachtenrunde (25.11.2026), Skript `skripte/schaetzung_runde2.py`

- Inflationsgedächtnis: Höchstrate der letzten zehn Jahre ohne Einfluss (−0,018, p = 0,52); Niveau ab Bruch −0,82 (p < 0,001). Mit Zehnjahresmittel ebenso.
- Ruhige Jahre ohne vorherigen Schub: 1953–1969 Median 64, 1999–2025 Median 26 (Verhältnis 0,40); mittlere Rate 1,6 % gegen 1,4 %.
- Langfristverhältnis ab/vor Bruch (Spalte 1, 90-%-Band): 1 % 0,28 [0,17–0,38]; 2 % 0,49 [0,36–0,73]; 3 % 0,88 [0,55–1,86]; darüber nicht unterscheidbar.
- Ohne Preisstabilität und Geldwertstabilität sowie ohne 1990–1998: Niveau ab Bruch −0,81 (p < 0,001). Ruhige Jahre 1990–1998: Median 39.
- Nach 2022: Modell erwartet 2025 den Wert 68 (beobachtet 47), 2026 den Wert 50 (beobachtet 50). Kein Überhang.
- Breusch-Godfrey p = 0,70 / 0,18 / 0,32 (1 bis 3 Lags). LR-Konfidenzmenge des Bruchjahrs (Eo & Morley 2015): 1999–2004.
- Verbreitung: Anteil der Sitzungen mit Treffer unverändert um 60 % (Sitzungen wurden länger); Anteil der Reden ab 300 Wörtern mit Treffer in ruhigen Jahren 4,5 % (1951–1998) gegen 1,8 % (1999–2020), `daten/verbreitung_reden.csv`.
- Partei-Jahr-Panel mit Partei- und Jahreseffekten: Regierungsstatus −0,145 (p = 0,002), Änderung ab 1999 +0,109 (p = 0,45). Ruhige Jahre: CDU/CSU 82 → 36, SPD 73 → 26, FDP 74 → 43.
- Anfragen auf einen Absatz gekürzt, Abbildung 3 entfällt. Modell heißt jetzt Anpassungsmodell.
