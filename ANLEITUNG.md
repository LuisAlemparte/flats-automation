# Monatslauf — Anleitung

1. Im Sparkasse-Online-Banking: Umsätze exportieren, Format **MT940** (Zeitraum: seit August bis heute).
2. Die Datei speichern als `flats-automation/data/umsaetze.txt` (die alte überschreiben).
3. Doppelklick auf `run.command`. Ein Fenster öffnet sich und zeigt den Lauf; am Ende steht "Fertig in … s".
4. Den Bericht lesen: `flats-automation/output/Bericht-JJJJ-MM.pdf` (neuester Monat).
5. Bei neuen Mieter-E-Mails: eine Zeile in `data/inbox.csv` eintragen (Datum;Mieter;Text), dann Schritt 3 wiederholen.

Beim ersten Mal: im Terminal `chmod +x run.command` ausführen, dann im Finder Rechtsklick → Öffnen (Gatekeeper).
Läuft etwas schief, steht die Fehlermeldung im Fenster; Foto davon an Luis.
