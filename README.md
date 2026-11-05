# 👮‍♂️ LSPD Log Assistent

[![GitHub Release](https://img.shields.io/github/v/release/KaputzeKings/lspd-logger?color=7c3aed&label=Version)](https://github.com/KaputzeKings/lspd-logger/releases)
[![GrandRP DE1](https://img.shields.io/badge/GrandRP-DE1-blue.svg)](https://gta5grand.com)
[![Platform](https://img.shields.io/badge/Plattform-Windows-0078d7.svg)](https://microsoft.com)

Ein leistungsstarkes, automatisiertes **Logging-, Auswertungs- und Dienst-Tool** für Beamte des **Los Santos Police Department** auf GrandRP (DE1). 

Inklusive Echtzeit-HUD, Discord-Forum-Uploader, automatischem Mitternachts-Reset und vollwertigem **Dienst-Rechner (F12)** für Bußgelder, Wanteds und TOW nach Vorbild von [Grandkasten](https://grandkasten.com/).

---

## 🌟 Kernfunktionen

### 1. ⚖️ Dienst-Rechner & Aktenvermerk ([F12])
Mit einem Tastendruck auf **[F12]** öffnet sich der Rechner direkt über dem Spiel.

* **Multi-Auflösung & Flexible Größen (25% bis 100%):**
  * **25% (Mini):** Ultrakompakte 1-Spalten-Ansicht – ideal für kleine Monitore, Laptops oder Nebenbeiblick.
  * **50% (Halb):** 2-Spalten-Ansicht – halbe Bildschirmbreite für entspanntes Multitasking.
  * **75% / 82% / 88% / 95% / 100%:** Volle 3-Spalten-Kartenansicht.
  * **Live-Größenwähler im Header:** Ohne Neustart direkt im F12-Fenster zwischen 25%, 50%, 75%, 82%, 88%, 95% und 100% wechseln.
  * **Anpassung an jede Bildschirmauflösung:** Automatische Ausrichtung für 4K, 1440p, 1080p, 720p/Laptops und Ultrawide (21:9) ohne Taskleisten-Clipping.
* **Bußgeld- & Strafenkatalog nach Grandkasten (GrandRP DE1):**
  * Über **100 offizielle Straftaten** in 9 Kategorien (`StVO`, `StGB Integrität`, `StGB Wirtschaft`, `StGB Beamte`, `WaffG`, `BtMG`, `Sperrzonen`, `BDG`, `StPO`).
  * **Echtzeit-Suchleiste:** Suche blitzschnell nach Paragraphen oder Stichwörtern (z.B. *Mord*, *Flucht*, *Drogen*, *§4*, *101*).
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
  * **Lizenz-Entzug:** Prominente rote Warn-Badges bei Delikten, die den Entzug von Führerschein oder Waffenschein verlangen.
  * **1-Klick-Kopieren:** Klick auf den Aktenvermerk oder den Button kopiert den Text sofort ins Clipboard fürs MDT.

* **TOW Rechner (StVO §25 Abschlepp- & Blitzerrechner):**
  * Zonen: *Verkehrsberuhigt (50 km/h)*, *Innerorts (150 km/h)*, *Außerorts (200 km/h)*, *Freeway (300 km/h)*, *Highway (350 km/h)*.
  * Exakte 4 Stufen für Geschwindigkeitsüberschreitungen (10-40 km/h: $5.000, 41-60 km/h: $10.000, 61-100 km/h: $15.000, ab 101 km/h: $20.000).
  * Checkbox für **Wiederholungstäter (StVO §25 lit. 2)** mit Verdopplung des Bußgeldes.
  * Generiert sofort die fertige Akte mit Kennzeichen und Ort: `04.11 16:05 - StVO §8 @Market - ABC-123`.

---

### 2. 📜 Teleprompter, Rechtebelehrung & Anwalts-Timer ([F10])
* **Exakte Miranda-Rechte:**
  1. *Sie haben das Recht zu schweigen, alles was Sie sagen kann und wird gegen Sie verwendet werden.*
  2. *Ab 2 Wanteds haben Sie das Recht auf einen staatlich anerkannten Anwalt, den Sie selbst benennen müssen.*
  3. *Wenn kein Anwalt verfügbar ist, wird Ihnen ein Pflichtverteidiger gestellt.*
  4. *Die Judikative übernimmt der Exekutivbeamte.*
  5. *Wenn ein Anwalt hinzugezogen wird, kann es länger als 25 Minuten dauern.*
  6. *Haben Sie ihre Rechte verstanden?*
* **Automatischer Auto-Play:** Startet beim Öffnen mit **[F10]** direkt.
* **Auto-Close:** Schließt sich nach dem ersten Durchlauf automatisch selbst.
* **Einstellbarer Takt (3 bis 10 Sekunden):**
  * Im F12-Rechner (Tab 3) oder im F10 Mini-HUD kann die Durchlaufzeit flexibel von **3s bis 10s** eingestellt werden.
* **Integrierter 5-Minuten Anwalts-Timer:** Fristüberwachung mit akustischem Signal und 1-Klick Vermerkerstellung.

---

### 3. 🔊 Sound-Einstellungen (Piepton Ein / Aus)
* Der Signalton (Piep-Sound) bei Uploads, Aktionen und Timer-Ablauf kann flexibel **ein- und ausgeschaltet** werden:
  * In den **Einstellungen (⚙️ HUD & Aussehen)**.
  * Direkt im **System-Tray Menü** mit einem Klick auf `🔊 Signalton (Piep-Sound)`.

---

### 4. 🎨 Vollständig anpassbares Design & Themes
* **Live-Themes:**
  * 🌐 *Grandkasten Cyberpunk* (Original Grandkasten DE1 Navy / Blue)
  * ⚫ *Schwarz-Grau-Weiß (Monochrome)*
  * 🟣 *Schwarz-Lila (Standard)*
  * 🔵 *LSPD Cyber Blue*
  * 🔴 *Tactical Stealth Red*
  * 🟢 *Emerald Special Forces*
* **Windows Light Mode Bugfix:** Keine weißen Balken oder Anzeigefehler mehr bei hellem Windows-Design.

---

## ⌨️ Tastenbelegung im Überblick

| Taste | Funktion |
| :--- | :--- |
| **`F12`** | Bußgeld-, Wanteds- & TOW-Rechner öffnen / schließen |
| **`F10`** | Teleprompter & Rechtebelehrung (Automatischer Auto-Play & Auto-Close) |
| **`1` bis `7`** | Screenshot-Kategorie auswählen (wenn HUD aktiv ist) |
| **`Z`** | Tages-Zwischenstand manuell an Discord senden |
| **`ESC`** | Rechner, Teleprompter oder Screenshot-Overlay schließen |

---

## 👥 Mitwirkende & Credits
- **Entwickelt für:** LSPD Beamte auf GrandRP DE1
- **Credits & Stimmen:** Justin Liebermann, Alex Springfield, Stefan Grand
- **Datenbasis Strafenkatalog:** Nach offizieller Vorlage von [Grandkasten](https://grandkasten.com/)
- **Repository & Updates:** [KaputzeKings/lspd-logger](https://github.com/KaputzeKings/lspd-logger)
