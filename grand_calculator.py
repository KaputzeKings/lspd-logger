import sys
import os
import json
import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGridLayout, QLineEdit, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu,
    QProgressBar, QTextEdit, QTabWidget, QComboBox, QSlider, QColorDialog, QScrollArea,
    QCheckBox, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon, QPainter, QAction, QKeyEvent

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
DB_FILE = os.path.join(BASE_DIR, "grandkasten_db.json")

def load_grandkasten_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

class GrandCalculatorOverlay(QWidget):
    closed = Signal()

    def __init__(self, theme_colors=None, parent=None):
        super().__init__(parent)
        self.theme_colors = theme_colors or {
            "bg": "#0a0614",
            "card_bg": "#130d22",
            "border": "#a855f7",
            "accent": "#7c3aed",
            "accent_hover": "#9333ea",
            "text": "#ffffff",
            "text_muted": "#a1a1aa",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "success": "#10b981"
        }
        self.db = load_grandkasten_db()
        self.selected_items = {} # id -> {"item": item, "voluntary": count}
        self.current_category = "Alle"
        self.search_term = ""

        self.setWindowTitle("LSPD Dienst-Rechner - Strafenkatalog & TOW")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.init_ui()
        self.resize_to_screen()

    def resize_to_screen(self):
        screen = QApplication.primaryScreen().geometry()
        scale = 0.82
        try:
            from pd_logger_overlay import CONFIG
            scale = float(CONFIG.get("calc_scale", 0.82))
        except Exception:
            pass
        w = int(screen.width() * scale)
        h = int(screen.height() * scale)
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def init_ui(self):
        c = self.theme_colors
        self.setStyleSheet(f"""
            QWidget {{
                color: {c['text']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTabWidget::pane {{
                border: 1px solid {c['border']};
                background-color: {c['bg']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {c['card_bg']};
                color: {c['text_muted']};
                border: 1px solid {c['border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 22px;
                font-size: 13px;
                font-weight: bold;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {c['accent']};
                color: #ffffff;
            }}
            QLineEdit {{
                background-color: {c['card_bg']};
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {c['accent_hover']};
            }}
            QComboBox {{
                background-color: {c['card_bg']};
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg']};
                color: {c['text']};
                selection-background-color: {c['accent']};
            }}
            QPushButton {{
                background-color: {c['accent']};
                color: #ffffff;
                border-radius: 6px;
                padding: 7px 16px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid {c['border']};
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {c['card_bg']};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['accent']};
                min-height: 25px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        main_frame = QFrame(self)
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet(f"""
            QFrame#mainFrame {{
                background-color: {c['bg']};
                border: 2px solid {c['border']};
                border-radius: 12px;
            }}
        """)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_frame)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(16, 12, 16, 16)
        frame_layout.setSpacing(10)

        # Header Bar
        header = QHBoxLayout()
        title_lbl = QLabel("⚖️ <span style='font-size: 16px; font-weight: bold;'>LSPD Dienst-Rechner</span> <span style='color:#a855f7; font-size:12px;'>(Strafenkatalog & TOW Rechner)</span>")
        header.addWidget(title_lbl)
        header.addStretch()

        help_lbl = QLabel("<span style='color:#a1a1aa; font-size:11px;'>Drücke <b>[F12]</b> oder <b>[ESC]</b> zum Schließen</span>")
        header.addWidget(help_lbl)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setStyleSheet("background-color: #ef4444; border: none; font-size: 13px; font-weight: bold; padding: 0px;")
        btn_close.clicked.connect(self.hide)
        header.addWidget(btn_close)
        frame_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        frame_layout.addWidget(self.tabs)

        self.tab_bussgeld = QWidget()
        self.tab_tow = QWidget()
        self.tabs.addTab(self.tab_bussgeld, "⚖️ Bußgeld- & Wanteds-Rechner")
        self.tabs.addTab(self.tab_tow, "🚗 TOW Rechner")

        self.setup_bussgeld_tab()
        self.setup_tow_tab()

    # --- TAB 1: BUßGELD & WANTEDS RECHNER ---
    def setup_bussgeld_tab(self):
        c = self.theme_colors
        layout = QHBoxLayout(self.tab_bussgeld)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        # LEFT SIDE: Catalog & Search (60%)
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        # Search bar
        search_lay = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Straftat, Paragraph oder Stichwort suchen (z. B. Mord, Flucht, Drogen, §4)...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_lay.addWidget(self.search_input)

        btn_clear_search = QPushButton("✕")
        btn_clear_search.setFixedWidth(32)
        btn_clear_search.clicked.connect(lambda: self.search_input.clear())
        search_lay.addWidget(btn_clear_search)
        left_box.addLayout(search_lay)

        # Category Filter Buttons
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(42)
        self.cat_scroll.setWidgetResizable(True)
        cat_widget = QWidget()
        self.cat_lay = QHBoxLayout(cat_widget)
        self.cat_lay.setContentsMargins(0, 0, 0, 0)
        self.cat_lay.setSpacing(6)

        categories = ["Alle", "StVO", "StGB Integrität", "StGB Wirtschaft", "StGB Beamte", "WaffG", "BtMG", "Sperrzonen", "BDG"]
        self.cat_buttons = {}
        for cat_name in categories:
            b = QPushButton(cat_name)
            b.setCheckable(True)
            b.setChecked(cat_name == "Alle")
            b.setStyleSheet(f"""
                QPushButton {{
                    background: #171324;
                    border: 1px solid #4c1d95;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background: {c['accent']};
                    color: #ffffff;
                    border: 1px solid {c['border']};
                }}
            """)
            b.clicked.connect(lambda checked, name=cat_name: self.filter_category(name))
            self.cat_buttons[cat_name] = b
            self.cat_lay.addWidget(b)
        self.cat_lay.addStretch()
        self.cat_scroll.setWidget(cat_widget)
        left_box.addWidget(self.cat_scroll)

        # Offenses scroll area
        self.offenses_scroll = QScrollArea()
        self.offenses_scroll.setWidgetResizable(True)
        self.offenses_container = QWidget()
        self.offenses_layout = QVBoxLayout(self.offenses_container)
        self.offenses_layout.setContentsMargins(0, 0, 4, 0)
        self.offenses_layout.setSpacing(6)
        self.offenses_scroll.setWidget(self.offenses_container)
        left_box.addWidget(self.offenses_scroll)

        layout.addLayout(left_box, stretch=62)

        # RIGHT SIDE: Summary, Inputs & Aktenvermerk (38%)
        right_box = QVBoxLayout()
        right_box.setSpacing(10)

        # Live Stats Box
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"background-color: {c['card_bg']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 10px;")
        stats_lay = QVBoxLayout(stats_frame)
        stats_lay.setSpacing(6)

        s_title = QLabel("📊 <b>Aktuelle Strafen-Berechnung</b>")
        s_title.setStyleSheet("font-size: 14px; color: #d8b4fe;")
        stats_lay.addWidget(s_title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Gesamt-Bußgeld:"), 0, 0)
        self.lbl_total_fine = QLabel("$ 0")
        self.lbl_total_fine.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ade80;")
        grid.addWidget(self.lbl_total_fine, 0, 1)

        grid.addWidget(QLabel("Höchste Wanteds:"), 1, 0)
        self.lbl_total_wanteds = QLabel("0 Wanteds")
        self.lbl_total_wanteds.setStyleSheet("font-size: 16px; font-weight: bold; color: #fbbf24;")
        grid.addWidget(self.lbl_total_wanteds, 1, 1)
        stats_lay.addLayout(grid)

        # Warning badges on screen (NOT in akte)
        self.lbl_warning_badges = QLabel("")
        self.lbl_warning_badges.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold;")
        self.lbl_warning_badges.setVisible(False)
        stats_lay.addWidget(self.lbl_warning_badges)

        right_box.addWidget(stats_frame)

        # Akten-Optionen
        opts_frame = QFrame()
        opts_frame.setStyleSheet(f"background-color: {c['card_bg']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 10px;")
        opts_lay = QVBoxLayout(opts_frame)
        opts_lay.setSpacing(6)

        opts_title = QLabel("📝 <b>Optionen für den Aktenvermerk</b>")
        opts_title.setStyleSheet("font-size: 13px; color: #d8b4fe;")
        opts_lay.addWidget(opts_title)

        opts_lay.addWidget(QLabel("TV-Abtransport / Beamter (optional):"))
        self.input_officer = QLineEdit()
        self.input_officer.setPlaceholderText("z.B. @LSPD Alex Springfield")
        self.input_officer.textChanged.connect(self.recalculate)
        opts_lay.addWidget(self.input_officer)

        opts_lay.addWidget(QLabel("Vorhandene Systemwanteds (optional):"))
        self.input_system_wanteds = QLineEdit()
        self.input_system_wanteds.setPlaceholderText("z.B. 2")
        self.input_system_wanteds.textChanged.connect(self.recalculate)
        opts_lay.addWidget(self.input_system_wanteds)

        self.cb_reue = QCheckBox("⚖️ Reue / Kooperation (§35 StGB)")
        self.cb_reue.setStyleSheet("font-size: 12px; color: #f472b6;")
        self.cb_reue.toggled.connect(self.recalculate)
        opts_lay.addWidget(self.cb_reue)

        right_box.addWidget(opts_frame)

        # Aktenvermerk Text Area
        akte_frame = QFrame()
        akte_frame.setStyleSheet(f"background-color: {c['card_bg']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 10px;")
        akte_lay = QVBoxLayout(akte_frame)
        akte_lay.setSpacing(6)

        a_title = QLabel("📋 <b>Generierter Aktenvermerk</b>")
        a_title.setStyleSheet("font-size: 13px; color: #d8b4fe;")
        akte_lay.addWidget(a_title)

        self.txt_aktenvermerk = QTextEdit()
        self.txt_aktenvermerk.setReadOnly(True)
        self.txt_aktenvermerk.setFixedHeight(65)
        self.txt_aktenvermerk.setStyleSheet("background: #090514; border: 1px solid #4c1d95; color: #ffffff; font-size: 12px; font-weight: bold;")
        akte_lay.addWidget(self.txt_aktenvermerk)

        btn_row = QHBoxLayout()
        self.btn_copy_akte = QPushButton("📋 Aktenvermerk kopieren")
        self.btn_copy_akte.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981); color: #ffffff; font-size: 13px; font-weight: bold; padding: 8px;")
        self.btn_copy_akte.clicked.connect(self.copy_aktenvermerk)
        btn_row.addWidget(self.btn_copy_akte)

        btn_reset = QPushButton("🔄 Zurücksetzen")
        btn_reset.setStyleSheet("background: #27142b; border: 1px solid #701a75; color: #f472b6; padding: 8px;")
        btn_reset.clicked.connect(self.reset_calculator)
        btn_row.addWidget(btn_reset)
        akte_lay.addLayout(btn_row)

        right_box.addWidget(akte_frame)
        right_box.addStretch()

        layout.addLayout(right_box, stretch=38)

        self.populate_offenses()

    def populate_offenses(self):
        # Clear existing
        while self.offenses_layout.count():
            item = self.offenses_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        c = self.theme_colors
        displayed = 0

        for cat, items in self.db.items():
            # Filter category
            if self.current_category != "Alle":
                cat_lower = cat.lower()
                cur_lower = self.current_category.lower()
                if "integrität" in cur_lower and "integrität" not in cat_lower:
                    continue
                elif "wirtschaft" in cur_lower and "wirtschaft" not in cat_lower:
                    continue
                elif "beamte" in cur_lower and "beamten" not in cat_lower:
                    continue
                elif cur_lower not in cat_lower:
                    continue

            for item in items:
                item_id = item.get("id", "")
                name = item.get("name", "")
                fine = item.get("fine", 0)
                wanteds = item.get("wanteds", 0) or 0
                voluntary_w = item.get("voluntaryWanteds", 0) or 0
                voluntary_f = item.get("voluntaryFine", 0) or 0
                info = item.get("info", "")

                # Search filter
                if self.search_term:
                    q = self.search_term.lower()
                    if q not in item_id.lower() and q not in name.lower() and q not in info.lower():
                        continue

                displayed += 1
                card = QFrame()
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {c['card_bg']};
                        border: 1px solid #2e1065;
                        border-radius: 6px;
                        padding: 6px 10px;
                    }}
                    QFrame:hover {{
                        border: 1px solid {c['border']};
                    }}
                """)
                c_lay = QVBoxLayout(card)
                c_lay.setContentsMargins(6, 4, 6, 4)
                c_lay.setSpacing(4)

                # Row 1: Checkbox, Name, Badges
                row1 = QHBoxLayout()
                cb = QCheckBox(f"<b>{item_id}</b> — {name}")
                cb.setChecked(item_id in self.selected_items)
                cb.setStyleSheet("font-size: 12px;")
                cb.toggled.connect(lambda checked, i=item: self.on_item_toggled(i, checked))
                row1.addWidget(cb, stretch=1)

                fine_str = f"${fine:,.0f}".replace(",", ".")
                fine_badge = QLabel(fine_str)
                fine_badge.setStyleSheet("background: #064e3b; color: #34d399; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 11px;")
                row1.addWidget(fine_badge)

                w_str = f"⭐ {wanteds}" if wanteds > 0 else "0 Wanteds"
                w_badge = QLabel(w_str)
                w_badge.setStyleSheet("background: #78350f; color: #fbbf24; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 11px;")
                row1.addWidget(w_badge)

                c_lay.addLayout(row1)

                # Row 2: Voluntary / Graue Wanteds & License info
                if voluntary_w > 0 or "entziehen" in info.lower():
                    row2 = QHBoxLayout()
                    if voluntary_w > 0:
                        v_lbl = QLabel(f"<span style='color:#a1a1aa; font-size:11px;'>Graue Wanteds (0 bis {voluntary_w}):</span>")
                        row2.addWidget(v_lbl)

                        current_v = self.selected_items.get(item_id, {}).get("voluntary", 0)
                        for count in range(voluntary_w + 1):
                            btn_v = QPushButton(str(count))
                            btn_v.setFixedSize(24, 20)
                            btn_v.setCheckable(True)
                            btn_v.setChecked(current_v == count)
                            btn_v.setStyleSheet(f"""
                                QPushButton {{
                                    background: #27142b;
                                    color: #d8b4fe;
                                    border: 1px solid #701a75;
                                    border-radius: 3px;
                                    padding: 0px;
                                    font-size: 10px;
                                }}
                                QPushButton:checked {{
                                    background: #a855f7;
                                    color: #ffffff;
                                    font-weight: bold;
                                }}
                            """)
                            btn_v.clicked.connect(lambda _, it=item, val=count: self.set_voluntary_wanteds(it, val))
                            row2.addWidget(btn_v)

                        if voluntary_f > 0:
                            v_fine_lbl = QLabel(f"<span style='color:#34d399; font-size:10px;'>+${voluntary_f:,.0f}/W.</span>".replace(",", "."))
                            row2.addWidget(v_fine_lbl)

                    if "entziehen" in info.lower():
                        row2.addStretch()
                        entzug_badge = QLabel(f"⚠️ {info}")
                        entzug_badge.setStyleSheet("background: #450a0a; color: #f87171; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 10px;")
                        row2.addWidget(entzug_badge)

                    c_lay.addLayout(row2)

                self.offenses_layout.addWidget(card)

        if displayed == 0:
            none_lbl = QLabel("Keine Straftaten gefunden.")
            none_lbl.setStyleSheet("color: #a1a1aa; font-size: 13px; padding: 20px;")
            self.offenses_layout.addWidget(none_lbl)

        self.offenses_layout.addStretch()

    def filter_category(self, cat_name):
        self.current_category = cat_name
        for name, b in self.cat_buttons.items():
            b.setChecked(name == cat_name)
        self.populate_offenses()

    def on_search_changed(self, text):
        self.search_term = text.strip()
        self.populate_offenses()

    def on_item_toggled(self, item, checked):
        item_id = item.get("id")
        if checked:
            if item_id not in self.selected_items:
                self.selected_items[item_id] = {"item": item, "voluntary": 0}
        else:
            if item_id in self.selected_items:
                del self.selected_items[item_id]
        self.recalculate()

    def set_voluntary_wanteds(self, item, count):
        item_id = item.get("id")
        if item_id not in self.selected_items:
            self.selected_items[item_id] = {"item": item, "voluntary": count}
        else:
            self.selected_items[item_id]["voluntary"] = count
        self.populate_offenses()
        self.recalculate()

    def recalculate(self):
        total_fine = 0
        max_wanteds = 0
        warnings = set()
        offense_ids = []

        for item_id, data in self.selected_items.items():
            item = data["item"]
            vol_count = data.get("voluntary", 0)

            base_fine = item.get("fine", 0) or 0
            vol_fine = item.get("voluntaryFine", 0) or 0
            item_fine = base_fine + (vol_count * vol_fine)
            total_fine += item_fine

            base_wanteds = item.get("wanteds", 0) or 0
            item_wanteds = base_wanteds + vol_count

            # Rule 10: Wanteds do NOT add up! Only the highest counts!
            if item_wanteds > max_wanteds:
                max_wanteds = item_wanteds

            offense_ids.append(item_id)

            info = item.get("info", "")
            if "waffenschein" in info.lower():
                warnings.add("⚠️ Waffenschein muss entzogen werden!")
            elif "führerschein" in info.lower():
                warnings.add("⚠️ Führerschein muss entzogen werden!")

        # Reue Checkbox (§35 StGB): Halbiert / reduziert Wanteds, Bußgeld bleibt unverändert!
        if self.cb_reue.isChecked() and max_wanteds > 0:
            max_wanteds = max(1, max_wanteds - 1)

        # Update Live Labels
        self.lbl_total_fine.setText(f"${total_fine:,.0f}".replace(",", "."))
        star_str = "⭐" * max_wanteds if max_wanteds > 0 else ""
        self.lbl_total_wanteds.setText(f"{max_wanteds} Wanteds {star_str}")

        if warnings:
            self.lbl_warning_badges.setText("<br>".join(warnings))
            self.lbl_warning_badges.setVisible(True)
        else:
            self.lbl_warning_badges.setVisible(False)

        # Build Aktenvermerk
        if not offense_ids:
            self.txt_aktenvermerk.setPlainText("")
            return

        now = datetime.datetime.now()
        date_prefix = now.strftime("%d.%m %H:%M")
        crimes_str = ", ".join(offense_ids)

        officer = self.input_officer.text().strip()
        officer_part = f" {officer}" if officer else ""

        sys_wanteds = self.input_system_wanteds.text().strip()
        sys_part = f" + {sys_wanteds} Systemwanteds" if sys_wanteds else ""

        # Format: 04.11 15:30 - StVO §10 Art. 16 @LSPD Alex Springfield + 2 Systemwanteds
        akte = f"{date_prefix} - {crimes_str}{officer_part}{sys_part}"
        self.txt_aktenvermerk.setPlainText(akte)

    def copy_aktenvermerk(self):
        text = self.txt_aktenvermerk.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.btn_copy_akte.setText("✓ Kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_copy_akte.setText("📋 Aktenvermerk kopieren"))

    def reset_calculator(self):
        self.selected_items.clear()
        self.search_input.clear()
        self.input_officer.clear()
        self.input_system_wanteds.clear()
        self.cb_reue.setChecked(False)
        self.populate_offenses()
        self.recalculate()

    # --- TAB 2: TOW RECHNER ---
    def setup_tow_tab(self):
        c = self.theme_colors
        layout = QVBoxLayout(self.tab_tow)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(12)

        # Title
        tow_title = QLabel("<span style='font-size:15px; font-weight:bold; color:#60a5fa;'>🚗 TOW Rechner</span>")
        c_lay.addWidget(tow_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        # Row 1: Kennzeichen & Ort
        grid.addWidget(QLabel("Kennzeichen:"), 0, 0)
        self.tow_plate = QLineEdit()
        self.tow_plate.setPlaceholderText("ABC-123")
        grid.addWidget(self.tow_plate, 0, 1)

        grid.addWidget(QLabel("Ort:"), 0, 2)
        self.tow_location = QLineEdit()
        self.tow_location.setPlaceholderText("z.B. Market")
        grid.addWidget(self.tow_location, 0, 3)

        # Row 2: Zone & Gefahren
        grid.addWidget(QLabel("Zone:"), 1, 0)
        self.tow_zone = QComboBox()
        self.tow_zone.addItem("Verkehrsberuhigte Bereiche (50 km/h)", 50)
        self.tow_zone.addItem("Innerorts (150 km/h)", 150)
        self.tow_zone.addItem("Außerorts (200 km/h)", 200)
        self.tow_zone.addItem("Highway (350 km/h)", 350)
        self.tow_zone.addItem("Freeway (300 km/h)", 300)
        self.tow_zone.setCurrentIndex(1) # Default 150 km/h
        grid.addWidget(self.tow_zone, 1, 1)

        grid.addWidget(QLabel("Gefahren:"), 1, 2)
        self.tow_speed = QLineEdit()
        self.tow_speed.setPlaceholderText("km/h")
        grid.addWidget(self.tow_speed, 1, 3)

        c_lay.addLayout(grid)

        # Row 3: Wiederholungstäter Checkbox
        self.tow_repeat = QCheckBox("⚠️ Wiederholungstäter (StVO §25 lit. 2)")
        self.tow_repeat.setStyleSheet("font-size: 13px; font-weight: bold; color: #fb923c;")
        c_lay.addWidget(self.tow_repeat)

        # Row 4: Berechnen Button
        self.btn_tow_calc = QPushButton("Berechnen")
        self.btn_tow_calc.setStyleSheet(f"""
            QPushButton {{
                background-color: #3b82f6;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
        """)
        self.btn_tow_calc.clicked.connect(self.calculate_tow)
        c_lay.addWidget(self.btn_tow_calc)

        # Row 5: Results Frame
        res_frame = QFrame()
        res_frame.setStyleSheet("background: #090614; border: 1px solid #1e293b; border-radius: 6px; padding: 10px;")
        res_lay = QVBoxLayout(res_frame)
        res_lay.setSpacing(6)

        self.lbl_tow_bussgeld = QLabel("Bußgeld: $ 0")
        self.lbl_tow_bussgeld.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        res_lay.addWidget(self.lbl_tow_bussgeld)

        res_lay.addWidget(QLabel("Generierte Akte:"))
        self.tow_akte = QLineEdit()
        self.tow_akte.setReadOnly(True)
        self.tow_akte.setStyleSheet("background: #020617; border: 1px solid #334155; color: #ffffff; font-size: 12px; font-weight: bold;")
        res_lay.addWidget(self.tow_akte)

        c_lay.addWidget(res_frame)

        # Row 6: Kopieren & Reset Buttons
        row_btn = QHBoxLayout()
        self.btn_tow_copy = QPushButton("Kopieren")
        self.btn_tow_copy.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_tow_copy.clicked.connect(self.copy_tow)
        row_btn.addWidget(self.btn_tow_copy, stretch=1)

        self.btn_tow_reset = QPushButton("Reset")
        self.btn_tow_reset.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #3b82f6;
                color: #60a5fa;
                font-size: 13px;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        self.btn_tow_reset.clicked.connect(self.reset_tow)
        row_btn.addWidget(self.btn_tow_reset, stretch=1)

        c_lay.addLayout(row_btn)
        layout.addWidget(card)
        layout.addStretch()

    def calculate_tow(self):
        zone = self.tow_zone.currentData() or 150
        try:
            speed = int(self.tow_speed.text().strip())
        except ValueError:
            speed = 0

        plate = self.tow_plate.text().strip()
        location = self.tow_location.text().strip()
        diff = speed - zone

        offense = "Keine Ordnungswidrigkeit"
        fine = 0
        paragraph = "-"

        if diff < 10:
            offense = "Keine Ordnungswidrigkeit"
            fine = 0
            paragraph = "-"
        elif diff <= 40:
            paragraph = "StVO §25"
            fine = 10000
            offense = "StVO §25 - Geschwindigkeitsüberschreitung (10-40 km/h)"
        elif diff <= 60:
            paragraph = "StVO §25"
            fine = 20000
            offense = "StVO §25 - Geschwindigkeitsüberschreitung (41-60 km/h) • Abschleppberechtigt"
        elif diff <= 100:
            paragraph = "StVO §25"
            fine = 35000
            offense = "StVO §25 - Geschwindigkeitsüberschreitung (61-100 km/h) • Abschleppberechtigt"
        else:
            paragraph = "StVO §25"
            fine = 50000
            offense = "StVO §25 - Geschwindigkeitsüberschreitung (ab 101 km/h) • Abschleppberechtigt"

        if diff >= 10 and self.tow_repeat.isChecked():
            fine *= 2
            paragraph += " + StVO §25 lit. 2"
            offense += " (Wiederholungstäter StVO §25 lit. 2)"

        fine_formatted = f"${fine:,.0f}".replace(",", ".")
        self.lbl_tow_bussgeld.setText(f"Bußgeld: {fine_formatted}  ({offense})")

        if diff < 10:
            self.tow_akte.setText("")
        else:
            now = datetime.datetime.now()
            date_str = now.strftime("%d.%m %H:%M")
            loc_str = f" @{location}" if location else ""
            plate_str = f" - {plate}" if plate else ""
            akte = f"{date_str} - {paragraph}{loc_str}{plate_str}"
            self.tow_akte.setText(akte)

    def copy_tow(self):
        text = self.tow_akte.text().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.btn_tow_copy.setText("✓ Kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_tow_copy.setText("Kopieren"))

    def reset_tow(self):
        self.tow_plate.clear()
        self.tow_location.clear()
        self.tow_speed.clear()
        self.tow_zone.setCurrentIndex(1)
        self.tow_repeat.setChecked(False)
        self.lbl_tow_bussgeld.setText("Bußgeld: $ 0")
        self.tow_akte.setText("")

    def show_calculator(self):
        self.resize_to_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()

    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.init_ui()
        self.populate_offenses()
        self.recalculate()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_F12:
            self.hide()
            self.closed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GrandCalculatorOverlay()
    w.show()
    sys.exit(app.exec())
