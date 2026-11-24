# Wer redet über Preise? Fraktionen, Regierung und Opposition, 1949–2026

Stand 24.11.2026. Nicht Teil der WD-Fassung (Längengrenze); Material für Rückfragen und eine spätere Fassung.

## Daten und Vorgehen

- 1949–2021: Open Discourse (Richter et al., Harvard Dataverse, [doi:10.7910/DVN/FIKIBO](https://doi.org/10.7910/DVN/FIKIBO)), 919.523 Redebeiträge mit Fraktion und Funktion des Redners. Skript `skripte/fraktionen_od.py`, Ergebnis `daten/fraktionen_od.csv`.
- 2013–2026: Reden-Datensatz des CPP-BT 2026-09-19. Skript `skripte/fraktionen_cpp.py`, Ergebnis `daten/fraktionen_cpp.csv`.
- Gezählt wird dasselbe Wortfeld Preisniveau wie in der Note, je Million Wörter der Reden einer Gruppe.
- Regierungsseite: Kanzler, Minister, Parlamentarische Staatssekretäre und Abgeordnete der Koalitionsfraktionen am Tag der Rede. Präsidium und Reden ohne Fraktion zählen nicht mit. Ab 2022 Koalition nach Jahresstand. Zusammenführung: `skripte/fraktionen_auswerten.py`, Reihe `daten/regierung_opposition.csv`, Grafik `abbildungen/Abb_Fraktionen.pdf`.
- Prüfung: In den Überschneidungsjahren 2016–2021 liefern beide Datensätze je Fraktion fast dieselben Treffer (z. B. CDU/CSU 2019: 22 gegen 23, AfD 2019: 34 gegen 34).

## Befunde

1. Die Opposition redet in Inflationsphasen mehr über Preise als die Regierung. 1973: Opposition 905, Regierung 263 je Mio. Wörter; 2022: 658 gegen 356.
2. In den 1970er-Jahren trägt vor allem die CDU/CSU in der Opposition das Thema: 329 je Mio. Wörter im Schnitt 1970–1989, SPD 117, FDP 166.
3. 1985–1987 kehrt sich das Verhältnis um. Die Regierung Kohl spricht mehr über Preise als die Opposition, bei Inflation nahe null und 1986 sogar sinkenden Preisen. Preisstabilität dient hier als Erfolgsmeldung.
4. Der Rückgang nach 1990 trifft alle Fraktionen. 1990–2009 liegen alle zwischen 37 (Grüne) und 69 (CDU/CSU), 2010–2021 zwischen 24 und 66. Keine einzelne Fraktion erklärt den Bruch.
5. 2022 sprechen alle Fraktionen viel über Preise, die Opposition (CDU/CSU 562, AfD 931, Linke 582) mehr als die Ampel (SPD 311, Grüne 363, FDP 438).

## Mittelwerte je Zeitraum (Treffer je Mio. Wörter)

| Fraktion | 1949–69 | 1970–89 | 1990–2009 | 2010–21 |
|---|---:|---:|---:|---:|
| CDU/CSU | 91 | 329 | 69 | 30 |
| SPD | 99 | 117 | 44 | 24 |
| FDP | 79 | 166 | 53 | 51 |
| Grüne | – | 46 | 37 | 24 |
| Linke/PDS | – | – | 65 | 35 |
| AfD | – | – | – | 66 |
| Regierungsseite | 91 | 173 | 53 | 31 |
| Opposition | 94 | 247 | 59 | 32 |

## Einordnung

Der Befund stützt die Lesart der Note: Preise sind ein Oppositionsthema, solange sie steigen. Er widerspricht der Vermutung, der Rückgang nach 1990 folge aus dem Eintritt neuer Fraktionen mit anderen Themen; auch CDU/CSU und SPD sinken auf ein Fünftel bis ein Drittel. Grenzen: Die Fraktionszuordnung in Open Discourse ist automatisch; Minister ohne Fraktionsangabe stehen über ihre Funktion auf der Regierungsseite.
