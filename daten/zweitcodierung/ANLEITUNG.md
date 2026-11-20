# Blinde Zweitcodierung der Trefferstichprobe

Ziel: Die Einstufung der Treffer (A Preisniveau, S sektoraler Preis, M übertragene Bedeutung) unabhängig wiederholen und die Übereinstimmung messen.

## Inhalt

- `prompt_zweitcodierung.md`: der vollständige Prompt mit 50 Treffern, ohne die Erstcodierung. Darin stehen alle 21 Fälle, die bei der Erstcodierung als S oder M galten, plus 29 zufällig gezogene A-Fälle. Die Reihenfolge ist gemischt.
- `schluessel.csv`: Zuordnung der Kennungen zur Stichprobe und die Erstcodierung. Diese Datei nicht in den Chat geben.

## Ablauf je Lauf

1. Neuen Chat öffnen, ohne Projekt, ohne Erinnerungen, am besten im anonymen oder temporären Modus.
2. Den ganzen Inhalt von `prompt_zweitcodierung.md` einfügen und abschicken.
3. Die Antwort (CSV-Codeblock) als `lauf1.csv` in diesen Ordner legen, beim nächsten Lauf `lauf2.csv` usw.
4. Nach zwei oder drei Läufen: `python skripte/zweitcodierung_auswerten.py`.

## Hinweis für den Text

Läufe desselben Modells sind keine unabhängigen menschlichen Codierer. Sie zeigen, ob die Einstufung stabil ist, nicht ob ein Mensch genauso urteilen würde. Am stärksten ist ein Lauf mit einem anderen Modell oder einem Menschen.
