# 👮‍♂️ LSPD Log Assistent (v1.4.9)

[![GitHub Release](https://img.shields.io/github/v/release/KaputzeKings/lspd-logger?color=4bd4a3&label=Version%201.4.9)](https://github.com/KaputzeKings/lspd-logger/releases)
[![GrandRP DE1](https://img.shields.io/badge/GrandRP-DE1-blue.svg)](https://gta5grand.com)
[![Platform](https://img.shields.io/badge/Plattform-Windows-0078d7.svg)](https://microsoft.com)

Ein leistungsstarkes, automatisiertes **Logging-, Auswertungs- und Dienst-Tool** für Beamte des **Los Santos Police Department** auf GrandRP (DE1). 

Inklusive Echtzeit-HUD, Discord-Forum-Uploader, automatischem Mitternachts-Reset und vollwertigem **Dienst-Rechner (F12)** für Bußgelder, Wanteds und TOW nach Vorbild von [Grandkasten](https://grandkasten.com/).

---

## 🚀 Neu in Version 1.4.9

* **Automatisches Logbuch mit höchster Kalenderwoche (KW):**
  * Erkennt im Discord-Forum automatisch das **aktuelle Logbuch mit der höchsten KW-Nummer** (z.B. `KW 46` statt `KW 45`).
  * **Perfekt für den wöchentlichen Samstag-Reset:** Sobald jeden Samstag ein neues Logbuch (z.B. KW 46, KW 47) erstellt wird, wechselt der Log-Assistent vollautomatisch in den neuen Thread – ganz ohne manuelle Konfiguration!
  * **Live KW-Badge im HUD:** Der Ingame-Header zeigt jetzt direkt an, in welche Woche geloggt wird (z.B. `#317108 KW 46`).
  * Berücksichtigt Archivierungsstatus und Discord-Snowflakes für maximale Ausfallsicherheit.

---

## 🚀 Neu in Version 1.4.8

* **Flüssige Fenster-Animationen (Smooth Window Transitions):**
  * **[F12] Grandkasten Dienst-Rechner:** Sanftes Einblenden mit feinem Micro-Slide-Up beim Öffnen, flüssiges Ausblenden mit Slide-Down beim Schließen (F12, ESC oder [✕]-Button).
  * **Ingame-HUD (Echtzeit-Overlay):** Geschmeidiges Auftauchen beim Eintreffen neuer Screenshots und elegantes Wegblenden nach Auswahl eines Buttons oder Druck auf [ESC].
  * **[F10] Teleprompter (Rechte & Miranda):** Butterweicher Übergang beim Aufrufen und Schließen des Floating-Prompters.
  * **Einstellungen (Setup):** Fließende Öffnungs- und Schließanimation bei "Einstellungen speichern" oder "Abbrechen".
* **DWM Hardware-Beschleunigung (60–144Hz):**
  * Berechnet via Windows Desktop Window Manager mit `OutCubic` / `InCubic` Kurven – butterweich ohne Mikroruckler oder FPS-Verlust in FiveM.
* **Re-Entrance Schutz:**
  * Zuverlässiges Verhindern von Darstellungsfehlern bei schnellem Mehrfachdrücken von [F12] oder [ESC].

---

## 🚀 Neu in Version 1.4.7

* **Systemfehler (+ Vermerk) integriert (1:1 Grandkasten):**
  * Neuer Schalter im F12 Dienst-Rechner: **Systemfehler (+ Vermerk)**.
  * Hängt vorschriftsmäßig `+ Systemfehler` an den MDT-Aktenvermerk an (z.B. `05.11 21:53 - ... + Systemfehler` oder `05.11 21:53 - StGB §4.1 + Systemfehler`).
  * Ermöglicht Beamten die saubere Dokumentation von unvorhergesehenen Spiel-, Fahrzeug- oder Anti-Cheat-Fehlern.
* **1:1 Grandkasten Switch-Toggles:**
  * Moderne Pill-Switches mit dynamischen Farbakzenten (Orange für Wiederholungstäter, Lila für §35 Reue, Blau für Systemfehler).
* **Reset-Unterstützung:**
  * Ein Klick auf *Alles Zurücksetzen* setzt auch den Systemfehler-Schalter wieder zurück.

---

## 🚀 Neu in Version 1.4.6

* **Grandkasten Dienst-Rechner gefixt:**
  * Zuverlässiges Laden aller 104 Straftatbestände auch in PyInstaller onedir/internal Umgebungen.
  * Kein leeres Fenster mehr: Alle Paragraphen (StVO, StGB, WaffG, BtMG, BDG etc.) werden sauber im 3-Spalten-Raster gerendert.
* **1:1 Ember Inter-Typografie:**
  * Originale `InterVariable.ttf` Schriftart für gestochen scharfe Lesbarkeit mit nativer Kantenglättung (`PreferAntialias`).
  * Saubere Schriftgewichte (700 für Paragraphen & Zahlen, 600 für Badges/Kategorien, 500 für Namen).
* **Farbige Status-Punkte (Ember Design System):**
  * **Ingame-HUD:** Echte, antialiased Farb-Icons an allen 7 Action-Buttons (Mint `#4bd4a3` für Inhaftierung, Crimson `#ef4444` für Global, Blau `#5ea2ef` für Local, Lila `#a87ffb` für Event, Amber `#f7bd2e` für Shoprob, Cyan `#2dd4bf` für FZ-Raid, Pink `#ec5ba3` für Streifenpartner).
  * **Dienst-Rechner:** Farbige Status-Punkte auf jedem Kategorie-Pill (`Alle`, `StVO`, `StGB Integrität`, `StGB Wirtschaft`, `StGB Beamte`, `WaffG`, `BtMG`, `Sperrzonen`, `BDG`) und auf jeder einzelnen Delikt-Karte.
* **Aktenvermerk & Terminal-Bereich überarbeitet:**
  * Samtiges Dark-Card Design (`#101012`) ohne grelle Rahmenlinien.
  * Dezente Velvet-Buttons für Kopieren (Mint) und Zurücksetzen (Subtiles Rot).

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
