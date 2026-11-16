#!/bin/bash
# Doppelklick startet den Monatslauf. Fenster bleibt offen, damit man das Ergebnis lesen kann.
cd "$(dirname "$0")"
/usr/local/bin/python3 run.py
echo
read -p "Enter zum Schließen"
