# PREISREDE: Parlamentarische Aufmerksamkeit für Preise, 1949 bis 2025

Daten und Skripte zur Note „Wann das Parlament über Preise spricht“ (Wolf-Fabian Hungerland, eingereicht beim Wirtschaftsdienst). Der Beitrag gibt die persönliche Auffassung des Autors wieder.

## Inhalt

| Ordner | Datei | Inhalt |
|---|---|---|
| `daten` | `plenum_jahr.csv` | Protokolle, Wörter und Treffer der Wortfelder Preisniveau und Messung je Jahr, 1949 bis September 2026 |
| `daten` | `plenum_protokolle.csv` | Wörter und Treffer je Protokoll |
| `daten` | `anfragen_jahr.csv` | Kleine und Große Anfragen je Jahr (Nenner) und codierte Treffer nach Kategorie, 1952 bis 2026 |
| `daten` | `anfragen_codierung.csv` | Kategorie je Drucksache: M Preisniveau, S Messung, E einzelne Preise, N Nebenbezug, B Beschaffung des Bundes, F Fehltreffer |
| `daten` | `inflation.csv` | Inflationsrate mit Quelle je Jahr, dazu der Index aller privaten Haushalte 1963 bis 1991 für die Robustheitsrechnung |
| `skripte` | `plenum_worte.py` | Zählt die Wortfelder im Korpus CPP-BT |
| `skripte` | `dip_anfragen.py` | Zieht die Anfragen über die DIP-Schnittstelle |
| `skripte` | `schaetzung.py` | Tabellen 1 und 2, Robustheit, Bootstrap-Tests für Schwelle und Bruchjahr, Korrelationen, Placebo |
| `skripte` | `alternativwoerter.py` | Zählt Preiswörter außerhalb des Wortfelds (Prüfung auf Wechsel des Vokabulars) |
| `skripte` | `validierung.py` | Prüft das Wortfeld auf dem Korpus: Neuzählung, Komposita, Stichprobe, Placebo |
| `daten` | `validierung_*.csv` | Ergebnisse der Prüfung, Stichprobe mit Urteil (A Preisniveau, S sektoral, M übertragen) |
| `skripte` | `abbildungen_latex.py` | Abbildungen der LaTeX-Fassung (kleine Vielfache, TeX Gyre Heros Cn) |
| `latex` | `preisrede.tex`, `preisrede.pdf` | Satzfassung in LaTeX (LuaLaTeX, TeX Gyre Pagella) |
| `skripte` | `abbildungen.py` | Abbildungen 1 bis 3 als PDF, PNG und SVG |

## Quellen

- Plenum: Fobbe, S. (2026). Corpus der Plenarprotokolle des Deutschen Bundestages (CPP-BT), Version 2026-09-19, Zenodo, https://doi.org/10.5281/zenodo.22844952, Lizenz CC0. Das Archiv (rund 830 MB) liegt nicht im Repo; `plenum_worte.py` lädt es von Zenodo.
- Anfragen: Deutscher Bundestag, DIP, https://search.dip.bundestag.de/api/v1, Abruf 01.11.2026.
- Inflation: bis 1991 Statistisches Bundesamt, Lange Reihen ab 1948 (Ausgabe 12/2022), Preisindex für die Lebenshaltung der Vier-Personen-Haushalte von Arbeitern und Angestellten mit mittlerem Einkommen, früheres Bundesgebiet; ab 1992 Verbraucherpreisindex für Deutschland, 2020 = 100, über die Bundesbank-Reihe BBDP1.A.DE.N.VPI.C.A00000.I20.A.

## Nachrechnen

```bash
pip install numpy statsmodels matplotlib
cd skripte
python schaetzung.py
python abbildungen.py
```

Die Abbildungen nutzen Arial Narrow, sofern installiert. Die SVG-Dateien verlangen Arial Narrow beim Öffnen auch dann, wenn beim Rendern eine Ersatzschrift lief.

## Lizenz

Code: MIT. Eigene Daten: CC BY 4.0. Die Rohdaten des Korpus stehen unter CC0.
