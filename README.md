# 🛡️ LSPD Log Assistent

[![GitHub Release](https://img.shields.io/github/v/release/KaputzeKings/lspd-logger?color=7c3aed&label=Version)](https://github.com/KaputzeKings/lspd-logger/releases)
[![GrandRP DE1](https://img.shields.io/badge/GrandRP-DE1-blue.svg)](https://gta5grand.com)
[![Platform](https://img.shields.io/badge/Plattform-Windows-0078d7.svg)](https://microsoft.com)

Ein leistungsstarkes, automatisiertes **Logging-, Auswertungs- und Dienst-Tool** für Beamte des **Los Santos Police Department** auf GrandRP (DE1). 

Inklusive Echtzeit-HUD, Discord-Forum-Uploader, automatischem Mitternachts-Reset und vollwertigem **Dienst-Rechner (F12)** für Bußgelder, Wanteds und TOW nach Vorbild von [Grandkasten](https://grandkasten.com/).

---

## 🚀 Kernfunktionen

### 1. ⚖️ Dienst-Rechner & Aktenvermerk ([F12])
Mit einem Tastendruck auf **[F12]** öffnet sich der Rechner (82% Bildschirmgröße) direkt über dem Spiel.

* **Bußgeld- & Strafenkatalog nach Grandkasten (GrandRP DE1):**
  * Über **100 offizielle Straftaten** in 9 Kategorien (`StVO`, `StGB Integrität`, `StGB Wirtschaft`, `StGB Beamte`, `WaffG`, `BtMG`, `Sperrzonen`, `BDG`, `StPO`).
  * **Echtzeit-Suchleiste:** Suche blitzschnell nach Paragraphen oder Stichwörtern (z.B. *Mord*, *Flucht*, *Drogen*, *§4*).
  * **Höchststrafe-Regel (1:1 Grandkasten):** Weder Bußgelder noch Wanteds addieren sich willkürlich auf – es zählt immer nur das schwerste Delikt für Gesamtstrafe und Fahndungslevel.
  * **Graue Wanteds (`voluntaryWanteds`):** Beamten-Ermessensspielraum per Knopfdruck auswählbar inkl. exakter automatischer Bußgelderhöhung.
  * **Reue & Kooperation (StGB §35):** Reduziert Wanteds automatisch um 2 (min. 1) und vermerkt das Delikt im Aktenvermerk.
  * **Systemwanteds:** Bereits vorhandene Fahndungssterne können eingegeben und in Gesamt-Wanteds & Akte einberechnet werden.
  * **Originales 1:1 Aktenvermerk-Format:** Erzeugt den vorschriftsmäßigen Text mit ` + ` Trennzeichen:
    * `04.11 16:01 - StGB §4.1`
    * `04.11 16:01 - StGB §5 + StGB §3.3`
    * `04.11 16:02 - StGB §5 + StGB §35`
    * `04.11 16:02 - StGB §5 + 2 Systemwanteds`
    * `04.11 16:05 - StVO §10 Art. 16 @LSPD Alex Springfield`
  * **Lizenz-Entzug:** Prominente rote Warn-Badges bei Delikten, die den Entzug von Führerschein oder Waffenschein verlangen (bleiben sauber außerhalb des Aktenvermerks).
  * **1-Klick-Kopieren:** Klick auf den Aktenvermerk oder den Button kopiert den Text sofort ins Clipboard fürs MDT.
  * **1-Klick-Zurücksetzen:** Leert alle Felder und setzt Bußgeld und Wanteds sofort auf 0 zurück.

* **TOW Rechner (StVO §25 Abschlepp- & Blitzerrechner):**
  * Zonen: *Verkehrsberuhigt (50 km/h)*, *Innerorts (150 km/h)*, *Außerorts (200 km/h)*, *Freeway (300 km/h)*, *Highway (350 km/h)*.
  * Automatische Prüfung der Geschwindigkeitsüberschreitung, Bußgelder ($10.000 bis $50.000) und Kennzeichnung als **Abschleppberechtigt** (ab 41 km/h drüber).
  * Checkbox für **Wiederholungstäter (StVO §25 lit. 2)** mit Verdopplung des Bußgeldes.
  * Generiert sofort die fertige Akte mit Kennzeichen und Ort: `04.11 16:05 - StVO §25 @Market - ABC-123`.

---

### 2. 📸 Automatisiertes Discord-Forum-Logging (Hotkeys 1–8)
Erkennt neu erstellte Screenshots (aus Medal, Shadowplay, FiveM etc.) und öffnet ein elegantes HUD-Overlay:

| Taste | Aktion | Beschreibung |
| :---: | :--- | :--- |
| **`1`** | **Inhaftierung** | Loggt Festnahme/Haft ins Forum (inkl. Wanteds, Bußgeld & Akte) |
| **`2`** | **Globaler Notruf** | Loggt Anfahrt/Teilnahme an einem globalen Notruf |
| **`3`** | **Lokaler Notruf** | Loggt Anfahrt/Teilnahme an einem lokalen Notruf |
| **`4`** | **Event** | Loggt Schutz oder Teilnahme an einem Server-Event |
| **`5`** | **Shoprob / Atmrob** | Loggt Raubüberfälle (Shoprob, Bank, ATM) |
| **`6`** | **FZ-Raid** | Loggt Fort Zancudo Raid-Einsätze |
| **`7`** | **Streifenpartner** | Loggt Streifenfahrten mit Kollegen (Partnermeldung) |
| **`Z`** | **Zwischenstand** | Sendet den aktuellen Tageszähler sofort in den Discord-Thread |
| **`ESC`** | **Schließen / Abbrechen** | Schließt das Screenshot-Overlay ohne Aktion |
| **`F12`** | **Dienst-Rechner** | Öffnet/Schließt den Grandkasten Bußgeld- & TOW-Rechner |

---

### 3. 📊 Live-HUD & Uprank-Zähler
- Zeigt in Echtzeit deine heutigen Einsätze auf dem Bildschirm:
  - `GL / LO`: Globale / Lokale Notrufe
  - `Shop`: Shoprobs & Überfälle
  - `Ev`: Events
  - `FZ`: Fort Zancudo Einsätze
  - `Inh`: Durchgeführte Inhaftierungen
  - `Partner`: Streifenpartner-Einsätze
- **Automatische Mitternachts-Abrechnung (00:00 Uhr):** Sendet automatisch deinen Tagesbericht ins Discord-Forum und setzt alle Zähler für die nächste Schicht auf 0 zurück.

---

### 4. 🎨 Vollständig anpassbares Design
- **Theme-Presets:**
  - 🟣 *Schwarz-Lila* (Modern Dark & Purple Neon)
  - 🔵 *Midnight Blue* (Elegantes Dunkelblau)
  - 🟡 *Cyberpunk* (Gelb-Schwarz)
  - 🟢 *Stealth Dark* (Minimalistisches Dunkelgrün)
  - ⚪ *LSPD Classic* (Weiß / Polizei-Blau)
  - 🎨 *Benutzerdefiniert* (Freier Color-Picker für Hintergrund, Akzentfarbe, Rahmen & Text)
- **Positionierung:** Oben Rechts, Oben Links, Unten Rechts, Unten Links.
- **Skalierung & Transparenz:** Stufenlos anpassbar von 70% bis 120%.

---

### 5. 🔄 Integrierter Auto-Updater
- Erkennt neue Updates auf GitHub automatisch im Hintergrund.
- **1-Klick-Installation:** Lädt das Update im Hintergrund herunter, entpackt alle Dateien sicher und startet die Anwendung nahtlos neu – keine manuelle Link-Eingabe oder manuelles Entpacken nötig!

---

## 📥 Installation

1. Lade dir die neueste Version herunter:  
   👉 **[Neueste Version downloaden (Releases)](https://github.com/KaputzeKings/lspd-logger/releases/latest)**
2. Entpacke das ZIP-Archiv in einen beliebigen Ordner (z.B. auf den Desktop).
3. Starte `LSPD_Log_Assistent.exe`.
4. Beim ersten Start öffnet sich das Einstellungsfenster:
   - **Reisepass-ID (Badge):** Deine Dienstnummer / Reisepassnummer.
   - **Screenshot-Ordner:** Wähle deinen Medal- oder Aufnahmeordner (z.B. `Videos\Medal\Screenshots\...`).
   - **Discord Bot / Webhook Token & Channel-ID:** Trage deine Zugangsdaten für das Forum ein.
5. Fertig! Das Tool läuft im Hintergrund (Tray-Icon unten rechts neben der Uhr).

---

## ⌨️ Tastenbelegung im Überblick

| Taste | Funktion |
| :--- | :--- |
| **`F12`** | Bußgeld-, Wanteds- & TOW-Rechner öffnen / schließen |
| **`F10`** | Teleprompter & Rechtebelehrung (Automatischer 3s Auto-Play & Auto-Close) |
| **`1` bis `7`** | Screenshot-Kategorie auswählen (wenn HUD aktiv ist) |
| **`Z`** | Tages-Zwischenstand manuell an Discord senden |
| **`ESC`** | Rechner, Teleprompter oder Screenshot-Overlay schließen |

---

## 🛠️ Mitwirkende & Credits
- **Entwickelt für:** LSPD Beamte auf GrandRP DE1
- **Datenbasis Strafenkatalog:** Nach offizieller Vorlage von [Grandkasten](https://grandkasten.com/)
- **Repository & Updates:** [KaputzeKings/lspd-logger](https://github.com/KaputzeKings/lspd-logger)
