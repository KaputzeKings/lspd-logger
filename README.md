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

* **Feste zentrierte Position:** Der Rechner sitzt stabil und zentriert auf dem Bildschirm – kein versehentliches Verschieben per Mausklick mehr.
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
  * **Lizenz-Entzug:** Prominente rote Warn-Badges bei Delikten, die den Entzug von Führerschein oder Waffenschein verlangen.
  * **1-Klick-Kopieren:** Klick auf den Aktenvermerk oder den Button kopiert den Text sofort ins Clipboard fürs MDT.

* **TOW Rechner (StVO §25 Abschlepp- & Blitzerrechner):**
  * Zonen: *Verkehrsberuhigt (50 km/h)*, *Innerorts (150 km/h)*, *Außerorts (200 km/h)*, *Freeway (300 km/h)*, *Highway (350 km/h)*.
  * Exakte 4 Stufen für Geschwindigkeitsüberschreitungen (10-40 km/h: $5.000, 41-60 km/h: $10.000, 61-100 km/h: $15.000, ab 101 km/h: $20.000).
  * Checkbox für **Wiederholungstäter (StVO §25 lit. 2)** mit Verdopplung des Bußgeldes.
  * Generiert sofort die fertige Akte mit Kennzeichen und Ort: `04.11 16:05 - StVO §8 @Market - ABC-123`.

---

### 2. 🔢 Fortlaufende Nummerierung & Anpassbare Log-Beschriftung
* **Automatisches Zählen:** Jeder Log-Eintrag wird automatisch mit seiner fortlaufenden Nummer betitelt (z.B. `1. Inhaftierung`, `2. Inhaftierung` ... `12. Inhaftierung`, `13. Inhaftierung` ohne Begrenzung).
* **Frei wählbare Titel-Vorlagen (Einstellungen Tab 2):** Für alle 7 Kategorien kann frei eingestellt werden, wie der Post auf Discord heißen soll (z. B. `{nr}. Inhaftierung` oder `Inhaftierung #{nr}`).
* **Discord Markdown Schriftstile:** Checkboxen für **Fett** (`**Text**`), __Unterstrichen__ (`__Text__`) und *Kursiv* (`*Text*`) mit interaktiver Live-Vorschau in den Einstellungen. Im HUD bleibt der Button kurz und sauber, auf Discord kommt das gewählte Styling an.
* **Keine abgeschnittenen Texte mehr:** Das HUD wurde verbreitert und die 2-Shot Phasen wurden optimiert (`(1/2)` / `(2/2)`), sodass auch bei längeren Namen und Skalierungen kein Text abgeschnitten wird.
* **🗑️ Letzten Log per Knopfdruck löschen:**
  * Mit Taste **`[9]`** oder **`[ENTF]`** (oder per Klick auf den roten Button im HUD) wird der letzte gesendete Log automatisch auf Discord gesucht und gelöscht.
  * Auch jederzeit direkt über das Taskleisten-Tray-Menü aufrufbar (*"🗑️ Letzten Discord-Log löschen"*).
  * Der interne Zähler passt sich nach dem Löschen sofort automatisch wieder nach unten an.
* **Discord-Thread-Synchronisation:** Beim Start und nach jedem Post liest das Tool den Discord-Thread aus, erkennt die bisher höchste vergebene Nummer und zählt nahtlos weiter.

---

### 3. 📜 Teleprompter, Rechtebelehrung & Anwalts-Timer ([F10])
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
  * Im F12-Rechner (Tab 3), im F10 Mini-HUD oder in den Einstellungen kann die Durchlaufzeit flexibel von **3s bis 10s** eingestellt werden.
* **Integrierter 5-Minuten Anwalts-Timer:** Fristüberwachung mit akustischem Signal und 1-Klick Vermerkerstellung.

---

### 4. ⚙️ Modern Dark Einstellungsmenü (Ember Velvet Obsidian)
Das Einstellungsmenü (Rechtsklick Tray ➔ **⚙️ Einstellungen**) präsentiert sich im hochmodernen **Ember Dark (Velvet Obsidian)** Design mit eleganten Pill-Tabs, abgerundeten Feldern und Neon-Akzenten, unterteilt in 4 saubere Tabs:
* **Tab 1: 👮 Dienst & Discord:**
  * Reisepassnummer / Badge-ID (Dienstnummer).
  * Medal Screenshot-Ordner mit bequemer `📁 Durchsuchen`-Auswahl.
  * Discord Forum-Thread-ID & sichere Token-Statusanzeige.
* **Tab 2: 📝 Log-Beschriftung & Stil:**
  * Discord Schriftstil (Fett, Unterstrichen, Kursiv) mit Live-Vorschau.
  * Eigene Textvorlagen für alle 7 Kategorien mit `{nr}` Platzhalter.
* **Tab 3: ⚖️ Grandkasten Rechner & F10:**
  * F12 Rechner Design-Theme & Fenstergröße (25% bis 100%).
  * Teleprompter Seiten-Takt (3s bis 10s) & Info zum automatischen Ablauf.
* **Tab 4: 🖥️ Ingame-HUD & Audio:**
  * Live-HUD Farb-Theme, Positionierung, Skalierung, Schriftart & Transparenz.
  * Signalton (Piep-Sound) An/Aus schaltbar.
  * Live-HUD Testvorschau-Button.

---

### 5. 🎨 Vollständig anpassbares Design & Themes
* **Live-Themes:**
  * 🌑 *Ember Dark (Velvet Obsidian)* (Modern Dark Dashboard Design)
  * ⚫ *Schwarz-Grau-Weiß (Monochrome)*
  * 🌐 *Grandkasten Cyberpunk* (Original Grandkasten DE1 Navy / Blue)
  * 🟣 *Schwarz-Lila (Standard)*
  * 🔵 *LSPD Cyber Blue*
  * 🔴 *Tactical Stealth Red*
  * 🟢 *Emerald Special Forces*
* **Windows Light Mode Bugfix:** Keine weißen Balken oder Anzeigefehler mehr bei hellem Windows-Design.

---

## ⌨️ Tastenbelegung im Überblick

| Taste | Funktion |
| :--- | :--- |
| **`F12`** | Bußgeld-, Wanteds- & TOW-Rechner öffnen / schließen (fest zentriert) |
| **`F10`** | Teleprompter & Rechtebelehrung (Automatischer Auto-Play & Auto-Close) |
| **`1` bis `7`** | Screenshot-Kategorie auswählen (wenn HUD aktiv ist) |
| **`8`** / **`Z`** | Tages-Zwischenstand manuell an Discord senden |
| **`9`** / **`ENTF`** | **Letzten Log automatisch aus Discord löschen** |
| **`ESC`** | Rechner, Teleprompter oder Screenshot-Overlay schließen |
| **`ESC`** | Rechner, Teleprompter oder Screenshot-Overlay schließen |

---

## 👥 Mitwirkende & Credits
- **Entwickelt für:** LSPD Beamte auf GrandRP DE1
- **Credits & Stimmen:** Justin Liebermann, Alex Springfield, Stefan Grand
- **Datenbasis Strafenkatalog:** Nach offizieller Vorlage von [Grandkasten](https://grandkasten.com/)
- **Repository & Updates:** [KaputzeKings/lspd-logger](https://github.com/KaputzeKings/lspd-logger)
