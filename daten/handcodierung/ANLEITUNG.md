# Handcodierung: Anleitung

Diese Codierung ist die menschliche Prüfung, die die Gutachten verlangen. Sie dauert etwa eine Stunde.

## So geht's

1. `Codierbogen.xlsx` öffnen.
2. Für jede der 54 Zeilen die Textstelle lesen. Das Suchwort steht ungefähr in der Mitte.
3. In Spalte D wählen:
   - **ja**, wenn die Stelle das allgemeine Preisniveau oder die Inflation meint, auch Kaufkraft und Lebenshaltungskosten insgesamt;
   - **nein**, wenn sie einen einzelnen Preis meint (Miete, Strom, Brot), ein Preisrecht, einen Preis im Sinn von Auszeichnung oder etwas anderes;
   - **unklar**, wenn der Ausschnitt nicht reicht.
4. Nicht nachschlagen, nicht im Internet suchen. Es zählt Ihr erster Eindruck aus dem Ausschnitt.
5. Datei speichern und hochladen oder in den Chat schicken.

## Was dahinter steckt (erst nach der Codierung lesen)

Die Hälfte der Stellen sind Treffer des Wortfelds (Prüfung der Trefferqualität), die andere Hälfte sind Stellen mit allgemeinen Preiswörtern, die das Wortfeld nicht erfasst (Prüfung der Vollständigkeit). Der Schlüssel liegt in `schluessel.csv`. Gezogen mit `skripte/handcodierung_ziehen.py`, drei Stellen je Jahrzehnt und Teil, Startwert 20261125.
