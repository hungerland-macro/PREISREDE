# Blinde Gegenprüfung der Anfragen-Codierung

Die Einteilung der 76 Anfragen in sechs Kategorien (M Preisniveau, S Messung, E einzelne Preise, N Nebenbezug, B Beschaffung, F Fehltreffer) stammt aus einem Vorschlag von Claude. Diese Prüfung wiederholt sie blind.

- `prompt_anfragen.md`: alle 76 Titel in gemischter Reihenfolge, ohne Codierung.
- `schluessel.csv`: Kennung, Drucksache, Jahr, bisherige Codierung. Nicht in den Chat geben.

Ablauf wie bei der Trefferstichprobe: Prompt in je einen frischen Chat von ChatGPT, Gemini, DeepSeek und Claude geben, Antworten als `lauf1_chatgpt.csv` usw. ablegen, dann `python skripte/zweitcodierung_auswerten.py zweitcodierung_anfragen`.

Für die Befunde zählt vor allem, ob die 17 Anfragen der Kategorien M und S stabil bleiben.

## Ergebnis (21.11.2026)

Vier Läufe (`lauf1_a` bis `lauf4_d`; zwei davon waren inhaltlich identisch). Übereinstimmung mit dem Vorschlag 91 % bis 95 %, Cohens Kappa 0,85 bis 0,92, Fleiss' Kappa über alle fünf Codierungen 0,91. Wo mindestens drei der vier Läufe anders urteilten, gilt ihre Mehrheit: 19/10749 E→B, 06/1843 E→B, 11/790 M→E, 06/2193 E→N, 16/2139 M→N. `daten/anfragen_codierung.csv` enthält die neue Kategorie und in `kategorie_vorschlag` den ursprünglichen Vorschlag. Damit zählen elf Anfragen zum Preisniveau und vier zur Messung, zusammen 15 statt 17.
