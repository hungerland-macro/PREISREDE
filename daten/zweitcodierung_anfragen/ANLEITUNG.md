# Blinde Gegenprüfung der Anfragen-Codierung

Die Einteilung der 76 Anfragen in sechs Kategorien (M Preisniveau, S Messung, E einzelne Preise, N Nebenbezug, B Beschaffung, F Fehltreffer) stammt aus einem Vorschlag von Claude. Diese Prüfung wiederholt sie blind.

- `prompt_anfragen.md`: alle 76 Titel in gemischter Reihenfolge, ohne Codierung.
- `schluessel.csv`: Kennung, Drucksache, Jahr, bisherige Codierung. Nicht in den Chat geben.

Ablauf wie bei der Trefferstichprobe: Prompt in je einen frischen Chat von ChatGPT, Gemini, DeepSeek und Claude geben, Antworten als `lauf1_chatgpt.csv` usw. ablegen, dann `python skripte/zweitcodierung_auswerten.py zweitcodierung_anfragen`.

Für die Befunde zählt vor allem, ob die 17 Anfragen der Kategorien M und S stabil bleiben.
