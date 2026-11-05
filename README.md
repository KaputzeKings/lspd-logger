# LSPD Log Assistent

[![GitHub Release](https://img.shields.io/github/v/release/KaputzeKings/lspd-logger?color=7c3aed&label=Version)](https://github.com/KaputzeKings/lspd-logger/releases)
[![GrandRP DE1](https://img.shields.io/badge/GrandRP-DE1-blue.svg)](https://gta5grand.com)
[![Platform](https://img.shields.io/badge/Plattform-Windows-0078d7.svg)](https://microsoft.com)

Ein präzises, automatisiertes **Logging-, Auswertungs- und Dienst-Tool** für Beamte des **Los Santos Police Department** auf GrandRP (DE1). 

Inklusive Ingame-HUD, Discord-Forum-Uploader, automatischem Mitternachts-Reset, vollwertigem **Dienst-Rechner (F12)** für Bußgelder, Wanteds und TOW nach Vorbild von Grandkasten sowie schwebendem **Teleprompter (F10)** für Miranda-Warnungen.

---

## Kernfunktionen

### 1. Dienst-Rechner & Aktenvermerk ([F12])
Mit einem Tastendruck auf **[F12]** öffnet sich der Rechner direkt über dem Spiel.

* **Feste zentrierte Position:** Der Rechner sitzt stabil und zentriert auf dem Bildschirm – kein versehentliches Verschieben per Mausklick.
* **Multi-Auflösung & Flexible Größen (25% bis 100%):**
  * **25% (Mini):** Ultrakompakte 1-Spalten-Ansicht – ideal für kleine Monitore, Laptops oder Nebenbeiblick.
  * **50% (Halb):** 2-Spalten-Ansicht – halbe Bildschirmbreite für entspanntes Multitasking.
  * **75% / 82% / 88% / 95% / 100%:** Volle 3-Spalten-Kartenansicht.
  * **Live-Größenwähler im Header:** Ohne Neustart direkt im F12-Fenster zwischen 25%, 50%, 75%, 82%, 88%, 95% und 100% wechseln.
  * **Anpassung an jede Bildschirmauflösung:** Automatische Ausrichtung für 4K, 1440p, 1080p, 720p/Laptops und Ultrawide (21:9) ohne Taskleisten-Clipping.
* **Bußgeld- & Strafenkatalog nach Grandkasten (GrandRP DE1):**
  * Über **100 offizielle Straftaten** in 9 Kategorien (`StVO`, `StGB Integrität`, `StGB Wirtschaft`, `StGB Beamte`, `WaffG`, `BtMG`, `Sperrzonen`, `BDG`, `StPO`).
  * **Echtzeit-Suchleiste:** Suche blitzschnell nach Paragraphen oder Stichwörtern (z. B. *Mord*, *Flucht*, *Drogen*, *§4*, *101*).
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
  * **Lizenz-Entzug:** Rote Warn-Badges bei Delikten, die den Entzug von Führerschein oder Waffenschein verlangen.
  * **1-Klick-Kopieren:** Klick auf den Aktenvermerk oder den Button kopiert den Text sofort ins Clipboard fürs MDT.

* **TOW Rechner (StVO §25 Abschlepp- & Blitzerrechner):**
  * Zonen: *Verkehrsberuhigt (50 km/h)*, *Innerorts (150 km/h)*, *Außerorts (200 km/h)*, *Freeway (300 km/h)*, *Highway (350 km/h)*.
  * Exakte 4 Stufen für Geschwindigkeitsüberschreitungen (10-40 km/h: $5.000, 41-60 km/h: $10.000, 61-100 km/h: $15.000, ab 101 km/h: $20.000).
  * Checkbox für **Wiederholungstäter (StVO §25 lit. 2)** mit Verdopplung des Bußgeldes.
  * Generiert sofort die fertige Akte mit Kennzeichen und Ort: `04.11 16:05 - StVO §8 @Market - ABC-123`.

---

### 2. Fortlaufende Nummerierung & Anpassbare Log-Beschriftung
* **Automatisches Zählen:** Jeder Log-Eintrag wird automatisch mit seiner fortlaufenden Nummer betitelt (z.B. `1. Inhaftierung`, `2. Inhaftierung` ... `12. Inhaftierung`, `13. Inhaftierung` ohne Begrenzung).
* **Individuelle Discord-Beschriftung:** In den Einstellungen kann für jede Kategorie festgelegt werden, wie der Log im Discord formatiert wird (z. B. `{nr}. Inhaftierung` oder `Inhaftierung #{nr}`).
* **Markdown-Schriftstile:** Wähle flexibel, ob gesendete Logs in Discord **Fett**, __Unterstrichen__ oder *Kursiv* formatiert werden sollen – inklusive Live-Vorschau in den Einstellungen.
* **1-Klick Log-Löschung ([9] / [ENTF]):** Versehentlich einen falschen Log gesendet? Ein Druck auf die Taste `[9]` oder `[ENTF]` löscht den zuletzt geposteten Log direkt und automatisch wieder aus dem Discord-Thread.

---

### 3. Teleprompter & Rechtebelehrung ([F10])
* **Miranda-Warnung per Knopfdruck:** Drücke im Einsatz **[F10]**, um das schwebende Mini-HUD zu öffnen.
* **Taktung frei konfigurierbar:** Stelle die Anzeigedauer der Sätze (3 bis 10 Sekunden) in den Einstellungen oder direkt am HUD ein.
* **Auto-Play & Auto-Close:** Läuft vollautomatisch Satz für Satz durch und schließt sich nach dem 5. Satz selbstständig.
* **Integrierter 5-Minuten Anwalts-Timer:** Klick auf den Timer startet die gesetzliche Wartefrist für Rechtsbeistände mit automatischen Aktenvermerken ("Anwalt nicht erschienen" / "Anwalt eingetroffen").

---

### 4. Einstellungen & Konfiguration
Über das Tray-Icon per Rechtsklick erreichbar:

* **Tab 1: Dienst & Discord:**
  * Reisepassnummer / Badge-ID (Dienstnummer).
  * Medal Screenshot-Ordner mit bequemer `Durchsuchen`-Auswahl.
  * Discord Forum-Thread-ID & sichere Token-Statusanzeige.
* **Tab 2: Log-Beschriftung & Stil:**
  * Discord Schriftstil (Fett, Unterstrichen, Kursiv) mit Live-Vorschau.
  * Eigene Textvorlagen für alle 7 Kategorien mit `{nr}` Platzhalter.
* **Tab 3: Grandkasten Rechner & F10:**
  * F12 Rechner Design-Theme & Fenstergröße (25% bis 100%).
  * Teleprompter Seiten-Takt (3s bis 10s) & Info zum automatischen Ablauf.
* **Tab 4: Ingame-HUD & Audio:**
  * Live-HUD Farb-Theme, Positionierung, Skalierung, Schriftart & Transparenz.
  * Signalton (Piep-Sound) An/Aus schaltbar.
  * Live-HUD Testvorschau-Button.

---

### 5. Unslopped Design System (Ember Velvet Obsidian)
* **Reines, ruhiges Chrome:** Keine bunten Farbverläufe, keine Neonränder, keine dekorativen Emojis.
* **1:1 Inter Variable Font:** Perfekte Lesbarkeit mit moderner digitaler Typografie.
* **Monochrome Dot-Statusanzeigen:** Saubere Farb-Dots (`●`) zur visuellen Unterscheidung ohne Emoji-Unruhe.
* **Tabellarische Ziffern (`tabular-nums`):** Flatterfreie Ziffern in Timern, Geldbeträgen und Statistiken.

---

## Tastenbelegung im Überblick

| Taste | Funktion |
| :--- | :--- |
| **`F12`** | Bußgeld-, Wanteds- & TOW-Rechner öffnen / schließen (fest zentriert) |
| **`F10`** | Teleprompter & Rechtebelehrung (Automatischer Auto-Play & Auto-Close) |
| **`1` bis `7`** | Screenshot-Kategorie auswählen (wenn HUD aktiv ist) |
| **`8`** / **`Z`** | Tages-Zwischenstand manuell an Discord senden |
| **`9`** / **`ENTF`** | **Letzten Log automatisch aus Discord löschen** |
| **`ESC`** | Rechner, Teleprompter oder Screenshot-Overlay schließen |

---

## Mitwirkende & Credits
- **Entwickelt für:** LSPD Beamte auf GrandRP DE1
- **Credits & Stimmen:** Justin Liebermann, Alex Springfield, Stefan Grand
- **Datenbasis Strafenkatalog:** Nach offizieller Vorlage von [Grandkasten](https://grandkasten.com/)
- **Repository & Updates:** [KaputzeKings/lspd-logger](https://github.com/KaputzeKings/lspd-logger)
