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
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon, QPainter, QAction, QKeyEvent, QPen

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

def make_item_key(item):
    return f"{item.get('id', '')}|{item.get('name', '')}"

class ClickableTerminalEdit(QTextEdit):
    clicked = Signal()
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.clicked.emit()

class OffenseCard(QFrame):
    clicked = Signal()

    def __init__(self, item, overlay, parent=None):
        super().__init__(parent)
        self.item = item
        self.item_id = item.get("id", "")
        self.name = item.get("name", "")
        self.fine = item.get("fine", 0) or 0
        self.wanteds = item.get("wanteds", 0) or item.get("mandatoryWanteds", 0) or 0
        self.voluntary_w = item.get("voluntaryWanteds", 0) or 0
        self.voluntary_f = item.get("voluntaryFine", 0) or 0
        self.info = item.get("info", "") or ""
        self.overlay = overlay
        self.is_selected = False
        self.voluntary_selected = 0
        self.v_buttons = []

        self.setCursor(Qt.PointingHandCursor)
        self.init_card_ui()

    def init_card_ui(self):
        self.apply_style(False)

        c_lay = QVBoxLayout(self)
        c_lay.setContentsMargins(12, 9, 12, 9)
        c_lay.setSpacing(4)

        # Row 1: Paragraph ID (Cyan), Selection checkmark, License Pill
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.lbl_id = QLabel(self.item_id)
        self.lbl_id.setStyleSheet("color: #00d2ff; font-size: 13px; font-weight: bold;")
        row1.addWidget(self.lbl_id)

        self.lbl_check = QLabel("✓")
        self.lbl_check.setStyleSheet("color: #00d2ff; font-size: 13px; font-weight: 900;")
        self.lbl_check.setVisible(False)
        row1.addWidget(self.lbl_check)

        row1.addStretch()

        if "entziehen" in self.info.lower():
            badge_text = "⚠️ Führerschein" if "führerschein" in self.info.lower() else "⚠️ Waffenschein"
            entzug_badge = QLabel(badge_text)
            entzug_badge.setStyleSheet("""
                background: #450a0a;
                color: #f87171;
                font-weight: bold;
                border: 1px solid #7f1d1d;
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
            """)
            row1.addWidget(entzug_badge)

        c_lay.addLayout(row1)

        # Row 2: Offense Description
        self.lbl_name = QLabel(self.name)
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setStyleSheet("color: #f3f4f6; font-size: 13px; line-height: 1.3;")
        c_lay.addWidget(self.lbl_name)

        # Row 3: Bottom Row with Wanteds Stars / Gray buttons on Left, Fine on Right
        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 3, 0, 0)
        row3.setSpacing(6)

        # Stars & Voluntary wanteds container
        stars_container = QHBoxLayout()
        stars_container.setSpacing(4)

        if self.wanteds == 0 and self.voluntary_w == 0:
            lbl_none = QLabel("<span style='color: #64748b; font-size: 11px;'>0 Wanteds</span>")
            stars_container.addWidget(lbl_none)
        else:
            # Mandatory gold stars
            if self.wanteds > 0:
                stars_gold = "★ " * self.wanteds
                lbl_gold = QLabel(f"<span style='color: #ffcc00; font-size: 14px; font-weight: bold;'>{stars_gold.strip()}</span>")
                stars_container.addWidget(lbl_gold)

            # Voluntary gray wanteds selector
            if self.voluntary_w > 0:
                lbl_vol = QLabel("<span style='color: #94a3b8; font-size: 10px; margin-left: 2px;'>Grau:</span>")
                stars_container.addWidget(lbl_vol)

                for count in range(self.voluntary_w + 1):
                    btn_v = QPushButton(str(count))
                    btn_v.setFixedSize(22, 19)
                    btn_v.setCheckable(True)
                    btn_v.setChecked(count == 0)
                    btn_v.setStyleSheet("""
                        QPushButton {
                            background: #1e1e28;
                            color: #94a3b8;
                            border: 1px solid #334155;
                            border-radius: 3px;
                            padding: 0px;
                            font-size: 10px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background: #2a2a3a;
                            border-color: #00d2ff;
                            color: #ffffff;
                        }
                        QPushButton:checked {
                            background: #00d2ff;
                            color: #000000;
                            border-color: #00d2ff;
                            font-weight: 900;
                        }
                    """)
                    btn_v.clicked.connect(lambda _, c=count: self.on_voluntary_clicked(c))
                    self.v_buttons.append(btn_v)
                    stars_container.addWidget(btn_v)

        row3.addLayout(stars_container)
        row3.addStretch()

        # Fine Display (Grandkasten Green)
        fine_str = f"${self.fine:,.0f}".replace(",", ".")
        self.lbl_fine = QLabel(fine_str)
        self.lbl_fine.setStyleSheet("""
            background: rgba(34, 197, 94, 0.12);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 12px;
            font-weight: bold;
        """)
        row3.addWidget(self.lbl_fine)

        c_lay.addLayout(row3)

    def apply_style(self, selected):
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                OffenseCard {
                    background-color: rgba(0, 210, 255, 0.10);
                    border: 2px solid #00d2ff;
                    border-radius: 8px;
                }
                OffenseCard:hover {
                    background-color: rgba(0, 210, 255, 0.16);
                    border: 2px solid #38bdf8;
                }
            """)
            if hasattr(self, 'lbl_check'):
                self.lbl_check.setVisible(True)
        else:
            self.setStyleSheet("""
                OffenseCard {
                    background-color: #16161c;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 8px;
                }
                OffenseCard:hover {
                    background-color: #1e1e27;
                    border: 1px solid #00d2ff;
                }
            """)
            if hasattr(self, 'lbl_check'):
                self.lbl_check.setVisible(False)

    def set_selected_visual(self, selected):
        self.apply_style(selected)

    def set_voluntary_visual(self, count):
        self.voluntary_selected = count
        for idx, btn in enumerate(self.v_buttons):
            btn.blockSignals(True)
            btn.setChecked(idx == count)
            btn.blockSignals(False)

    def on_voluntary_clicked(self, count):
        self.overlay.set_voluntary_wanteds(self.item, count)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked inside a voluntary push button
            child = self.childAt(event.pos())
            if isinstance(child, QPushButton):
                super().mousePressEvent(event)
                return
            # Click anywhere else on the card toggles offense!
            self.overlay.toggle_offense(self.item)
            event.accept()
        else:
            super().mousePressEvent(event)

    def reset(self):
        self.set_selected_visual(False)
        self.set_voluntary_visual(0)

class GrandCalculatorOverlay(QWidget):
    closed = Signal()

    def __init__(self, theme_colors=None, parent=None):
        super().__init__(parent)
        self.db = load_grandkasten_db()
        self.selected_items = {} # unique_key -> {"item": item, "voluntary": count}
        self.current_category = "Alle"
        self.search_term = ""
        self.cards_by_key = {}

        self.setWindowTitle("LSPD Dienst-Rechner - 1:1 Grandkasten")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.init_ui()
        self.resize_to_screen()

    def resize_to_screen(self):
        screen = QApplication.primaryScreen().geometry()
        scale = 0.84
        try:
            from pd_logger_overlay import CONFIG
            scale = float(CONFIG.get("calc_scale", 0.84))
        except Exception:
            pass
        w = max(1000, int(screen.width() * scale))
        h = max(680, int(screen.height() * scale))
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def init_ui(self):
        # 100% Original Grandkasten Global Styling
        self.setStyleSheet("""
            QWidget {
                color: #f3f4f6;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.10);
                background-color: #0d0d11;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #16161d;
                color: #a1a1aa;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 9px 24px;
                font-size: 13px;
                font-weight: bold;
                margin-right: 5px;
            }
            QTabBar::tab:selected {
                background-color: #00d2ff;
                color: #000000;
                font-weight: 900;
                border-color: #00d2ff;
            }
            QLineEdit {
                background-color: #16161d;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #00d2ff;
                background-color: #1a1a24;
            }
            QComboBox {
                background-color: #16161d;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid #00d2ff;
            }
            QComboBox QAbstractItemView {
                background-color: #16161d;
                color: #ffffff;
                selection-background-color: #00d2ff;
                selection-color: #000000;
                border: 1px solid #27272a;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #111116;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #272733;
                min-height: 25px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00d2ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QCheckBox {
                color: #f3f4f6;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4b5563;
                border-radius: 4px;
                background-color: #16161d;
            }
            QCheckBox::indicator:hover {
                border-color: #00d2ff;
            }
            QCheckBox::indicator:checked {
                background-color: #00d2ff;
                border-color: #00d2ff;
            }
        """)

        main_frame = QFrame(self)
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: #0a0a0c;
                border: 2px solid rgba(0, 210, 255, 0.4);
                border-radius: 12px;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_frame)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(18, 14, 18, 16)
        frame_layout.setSpacing(10)

        # Header Bar (Grandkasten Cyberpunk Look)
        header = QHBoxLayout()
        title_lbl = QLabel("🛡️ <span style='font-size: 16px; font-weight: 900; color: #ffffff;'>GRANDKASTEN</span> <span style='color: #00d2ff; font-size: 13px; font-weight: bold;'>DIENST-RECHNER</span> <span style='color: #71717a; font-size: 11px;'>| Bußgeld, Wanteds & TOW</span>")
        header.addWidget(title_lbl)
        header.addStretch()

        help_lbl = QLabel("<span style='color: #94a3b8; font-size: 11px;'>Drücke <b>[F12]</b> oder <b>[ESC]</b> zum Schließen</span>")
        header.addWidget(help_lbl)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_close.clicked.connect(self.hide)
        header.addWidget(btn_close)
        frame_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        frame_layout.addWidget(self.tabs)

        self.tab_bussgeld = QWidget()
        self.tab_tow = QWidget()
        self.tabs.addTab(self.tab_bussgeld, "⚖️ Bußgeld- & Wanteds-Rechner")
        self.tabs.addTab(self.tab_tow, "🚙 TOW Rechner")

        self.setup_bussgeld_tab()
        self.setup_tow_tab()

    # --- TAB 1: BUßGELD & WANTEDS RECHNER ---
    def setup_bussgeld_tab(self):
        layout = QHBoxLayout(self.tab_bussgeld)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

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
        btn_clear_search.setStyleSheet("""
            QPushButton {
                background: #1e1e28;
                border: 1px solid #334155;
                color: #94a3b8;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #334155;
                color: #ffffff;
            }
        """)
        btn_clear_search.clicked.connect(lambda: self.search_input.clear())
        search_lay.addWidget(btn_clear_search)
        left_box.addLayout(search_lay)

        # Category Filter Pills (Grandkasten 1:1 rounded pills)
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(44)
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
            b.setCursor(Qt.PointingHandCursor)
            self.style_cat_btn(b, cat_name == "Alle")
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
        self.offenses_layout.setContentsMargins(0, 0, 6, 0)
        self.offenses_layout.setSpacing(8)
        self.offenses_scroll.setWidget(self.offenses_container)
        left_box.addWidget(self.offenses_scroll)

        layout.addLayout(left_box, stretch=60)

        # RIGHT SIDE: Grandkasten Live Dashboard & Aktenvermerk (40%)
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        # Glass Box 1: Gesamtstrafe & Big Star Rating
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: #13141a;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        top_lay = QVBoxLayout(top_frame)
        top_lay.setSpacing(6)

        lbl_strafe_title = QLabel("GESAMTSTRAFE (HÖCHSTSTRAFE)")
        lbl_strafe_title.setAlignment(Qt.AlignCenter)
        lbl_strafe_title.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        top_lay.addWidget(lbl_strafe_title)

        # Grandkasten Glowing Money Display
        self.lbl_total_fine = QLabel("$ 0")
        self.lbl_total_fine.setAlignment(Qt.AlignCenter)
        self.lbl_total_fine.setStyleSheet("""
            font-size: 28px;
            font-weight: 900;
            color: #4ade80;
            padding: 2px 0;
        """)
        top_lay.addWidget(self.lbl_total_fine)

        # Grandkasten Big Star Rating (5 Stars)
        self.lbl_star_row = QLabel("★ ★ ★ ★ ★")
        self.lbl_star_row.setAlignment(Qt.AlignCenter)
        self.lbl_star_row.setStyleSheet("font-size: 26px; font-weight: bold; color: #272733;")
        top_lay.addWidget(self.lbl_star_row)

        self.lbl_wanteds_text = QLabel("0 Wanteds")
        self.lbl_wanteds_text.setAlignment(Qt.AlignCenter)
        self.lbl_wanteds_text.setStyleSheet("color: #ffcc00; font-size: 13px; font-weight: bold;")
        top_lay.addWidget(self.lbl_wanteds_text)

        # Grandkasten Warning Box (Zusatzinfos)
        self.lbl_warning_box = QLabel("")
        self.lbl_warning_box.setWordWrap(True)
        self.lbl_warning_box.setStyleSheet("""
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            font-size: 12px;
            font-weight: bold;
            border-left: 4px solid #ef4444;
            border-radius: 4px;
            padding: 8px;
        """)
        self.lbl_warning_box.setVisible(False)
        top_lay.addWidget(self.lbl_warning_box)

        right_box.addWidget(top_frame)

        # Glass Box 2: Optionen für den Aktenvermerk
        opts_frame = QFrame()
        opts_frame.setStyleSheet("""
            QFrame {
                background-color: #13141a;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        opts_lay = QVBoxLayout(opts_frame)
        opts_lay.setSpacing(8)

        # Switches / Toggles (Wiederholungstäter & §35 Reue)
        toggles_lay = QHBoxLayout()
        self.cb_repeat = QCheckBox("⚠️ Wiederholungstäter (StVO)")
        self.cb_repeat.setStyleSheet("font-size: 12px; color: #fb923c; font-weight: bold;")
        self.cb_repeat.toggled.connect(self.recalculate)
        toggles_lay.addWidget(self.cb_repeat)

        self.cb_reue = QCheckBox("🤝 §35 Reue (-2 Wanteds)")
        self.cb_reue.setStyleSheet("font-size: 12px; color: #a855f7; font-weight: bold;")
        self.cb_reue.toggled.connect(self.recalculate)
        toggles_lay.addWidget(self.cb_reue)
        opts_lay.addLayout(toggles_lay)

        # Grid for Systemwanteds & Abtransport
        grid_lay = QGridLayout()
        grid_lay.setSpacing(8)

        lbl_sys = QLabel("SYSTEMWANTEDS:")
        lbl_sys.setStyleSheet("color: #71717a; font-size: 10px; font-weight: bold;")
        grid_lay.addWidget(lbl_sys, 0, 0)

        self.input_system_wanteds = QLineEdit()
        self.input_system_wanteds.setPlaceholderText("0")
        self.input_system_wanteds.textChanged.connect(self.recalculate)
        grid_lay.addWidget(self.input_system_wanteds, 1, 0)

        lbl_orga = QLabel("ABTRANSPORT DURCH:")
        lbl_orga.setStyleSheet("color: #71717a; font-size: 10px; font-weight: bold;")
        grid_lay.addWidget(lbl_orga, 0, 1)

        self.combo_orga = QComboBox()
        self.combo_orga.addItems(["- Orga -", "LSPD", "SAHP", "NG", "USSS", "FIB", "GOV"])
        self.combo_orga.setCurrentText("LSPD")
        self.combo_orga.currentTextChanged.connect(self.recalculate)
        grid_lay.addWidget(self.combo_orga, 1, 1)

        opts_lay.addLayout(grid_lay)

        # Officer & Plate Inputs
        officer_lay = QHBoxLayout()
        self.input_officer = QLineEdit()
        self.input_officer.setPlaceholderText("Name des Beamten (z.B. Alex Springfield)")
        self.input_officer.textChanged.connect(self.recalculate)
        officer_lay.addWidget(self.input_officer)

        self.input_plate = QLineEdit()
        self.input_plate.setPlaceholderText("Kennzeichen (optional)")
        self.input_plate.textChanged.connect(self.recalculate)
        officer_lay.addWidget(self.input_plate)
        opts_lay.addLayout(officer_lay)

        right_box.addWidget(opts_frame)

        # Glass Box 3: Aktenvermerk Terminal & Copy Button
        akte_frame = QFrame()
        akte_frame.setStyleSheet("""
            QFrame {
                background-color: #13141a;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        akte_lay = QVBoxLayout(akte_frame)
        akte_lay.setSpacing(8)

        lbl_akte_title = QLabel("AKTENVERMERK")
        lbl_akte_title.setStyleSheet("color: #a1a1aa; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        akte_lay.addWidget(lbl_akte_title)

        # 1:1 Grandkasten Terminal Aktenvermerk
        self.txt_aktenvermerk = ClickableTerminalEdit()
        self.txt_aktenvermerk.setReadOnly(True)
        self.txt_aktenvermerk.setFixedHeight(75)
        self.txt_aktenvermerk.setPlaceholderText("Bitte Tatbestände wählen...")
        self.txt_aktenvermerk.setStyleSheet("""
            QTextEdit {
                background: #000000;
                border: 2px solid #22c55e;
                border-radius: 6px;
                color: #22c55e;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QTextEdit:hover {
                border-color: #00d2ff;
            }
        """)
        self.txt_aktenvermerk.clicked.connect(self.copy_aktenvermerk)
        akte_lay.addWidget(self.txt_aktenvermerk)

        lbl_hint_copy = QLabel("<span style='color: #71717a; font-size: 10px;'>Klicken zum Kopieren</span>")
        lbl_hint_copy.setAlignment(Qt.AlignRight)
        akte_lay.addWidget(lbl_hint_copy)

        btn_row = QHBoxLayout()
        self.btn_copy_akte = QPushButton("📋 Aktenvermerk kopieren")
        self.btn_copy_akte.setCursor(Qt.PointingHandCursor)
        self.btn_copy_akte.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                padding: 9px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_copy_akte.clicked.connect(self.copy_aktenvermerk)
        btn_row.addWidget(self.btn_copy_akte, stretch=2)

        # Grandkasten Reset Button (Red Gradient)
        btn_reset = QPushButton("Alles Zurücksetzen")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #991b1b);
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
                padding: 9px;
                border: none;
                text-transform: uppercase;
            }
            QPushButton:hover {
                filter: brightness(1.2);
            }
        """)
        btn_reset.clicked.connect(self.reset_calculator)
        btn_row.addWidget(btn_reset, stretch=1)
        akte_lay.addLayout(btn_row)

        right_box.addWidget(akte_frame)
        right_box.addStretch()

        layout.addLayout(right_box, stretch=40)

        # Build cards once with unique keys
        self.build_offenses_list()

    def style_cat_btn(self, btn, is_active):
        if is_active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00d2ff;
                    color: #000000;
                    font-weight: bold;
                    border: 1px solid #00d2ff;
                    border-radius: 14px;
                    padding: 5px 14px;
                    font-size: 11px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #16161d;
                    color: #a1a1aa;
                    font-weight: normal;
                    border: 1px solid rgba(255, 255, 255, 0.10);
                    border-radius: 14px;
                    padding: 5px 14px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #22222d;
                    color: #ffffff;
                    border-color: #00d2ff;
                }
            """)

    def build_offenses_list(self):
        self.cards_by_key = {}
        for cat, items in self.db.items():
            for item in items:
                key = make_item_key(item)
                card = OffenseCard(item, self)
                self.cards_by_key[key] = card
                self.offenses_layout.addWidget(card)

        self.offenses_layout.addStretch()
        self.filter_offenses()

    def filter_offenses(self):
        q = self.search_term.lower()
        cur_cat = self.current_category.lower()

        for cat, items in self.db.items():
            cat_lower = cat.lower()

            # Check category match
            cat_matches = True
            if self.current_category != "Alle":
                if "integrität" in cur_cat:
                    cat_matches = "integrität" in cat_lower
                elif "wirtschaft" in cur_cat:
                    cat_matches = "wirtschaft" in cat_lower
                elif "beamte" in cur_cat:
                    cat_matches = "beamten" in cat_lower
                else:
                    cat_matches = cur_cat in cat_lower

            for item in items:
                key = make_item_key(item)
                card = self.cards_by_key.get(key)
                if not card:
                    continue

                if not cat_matches:
                    card.setVisible(False)
                    continue

                if q:
                    name_lower = card.name.lower()
                    id_lower = card.item_id.lower()
                    info_lower = card.info.lower()
                    match_search = (q in id_lower) or (q in name_lower) or (q in info_lower)
                    card.setVisible(match_search)
                else:
                    card.setVisible(True)

    def filter_category(self, cat_name):
        self.current_category = cat_name
        for name, b in self.cat_buttons.items():
            self.style_cat_btn(b, name == cat_name)
        self.filter_offenses()

    def on_search_changed(self, text):
        self.search_term = text.strip()
        self.filter_offenses()

    def toggle_offense(self, item):
        key = make_item_key(item)
        if key in self.selected_items:
            del self.selected_items[key]
            is_sel = False
        else:
            self.selected_items[key] = {"item": item, "voluntary": 0}
            is_sel = True

        card = self.cards_by_key.get(key)
        if card:
            card.set_selected_visual(is_sel)
            if not is_sel:
                card.set_voluntary_visual(0)

        self.recalculate()

    def set_voluntary_wanteds(self, item, count):
        key = make_item_key(item)
        if key not in self.selected_items:
            self.selected_items[key] = {"item": item, "voluntary": count}
        else:
            self.selected_items[key]["voluntary"] = count

        card = self.cards_by_key.get(key)
        if card:
            card.set_selected_visual(True)
            card.set_voluntary_visual(count)

        self.recalculate()

    def recalculate(self):
        max_fine = 0
        max_wanteds = 0
        warnings = set()
        offense_ids = []

        # Find most severe offense (Grandkasten logic)
        most_severe = None
        max_base_wanteds = -1

        for key, data in self.selected_items.items():
            item = data["item"]
            base_wanteds = item.get("wanteds", 0) or item.get("mandatoryWanteds", 0) or 0
            fine = item.get("fine", 0) or 0

            offense_ids.append(item.get("id"))

            if base_wanteds > max_base_wanteds or (base_wanteds == max_base_wanteds and fine > (most_severe.get("fine", 0) if most_severe else 0)):
                max_base_wanteds = base_wanteds
                most_severe = item

            # License warnings
            info = item.get("info", "")
            if "waffenschein" in info.lower():
                warnings.add("⚠️ Waffenschein muss entzogen werden!")
            if "führerschein" in info.lower():
                warnings.add("⚠️ Führerschein muss entzogen werden!")

        if most_severe:
            ms_key = make_item_key(most_severe)
            vol_count = self.selected_items.get(ms_key, {}).get("voluntary", 0)
            base_fine = most_severe.get("fine", 0) or 0
            vol_fine = most_severe.get("voluntaryFine", 0) or 0

            max_fine = base_fine + (vol_count * vol_fine)
            base_w = most_severe.get("wanteds", 0) or most_severe.get("mandatoryWanteds", 0) or 0
            max_wanteds = base_w + vol_count
        else:
            for key, data in self.selected_items.items():
                item = data["item"]
                vol_count = data.get("voluntary", 0)
                base_w = item.get("wanteds", 0) or item.get("mandatoryWanteds", 0) or 0
                item_fine = (item.get("fine", 0) or 0) + (vol_count * (item.get("voluntaryFine", 0) or 0))
                item_wanteds = base_w + vol_count
                if item_fine > max_fine:
                    max_fine = item_fine
                if item_wanteds > max_wanteds:
                    max_wanteds = item_wanteds

        # Check for StVO presence
        has_stvo = any(oid.startswith("StVO") for oid in offense_ids if oid)
        self.cb_repeat.setEnabled(has_stvo)
        if not has_stvo:
            self.cb_repeat.setChecked(False)

        # Wiederholungstäter doubles fine on StVO
        if self.cb_repeat.isChecked() and has_stvo:
            max_fine *= 2

        # Check if Reue is allowed
        prevents_reue = any(oid in ["StGB §25", "§6 StPO", "StPO §6", "StGB §4.1", "StGB §27"] for oid in offense_ids if oid)
        if prevents_reue:
            self.cb_reue.setEnabled(False)
            self.cb_reue.setChecked(False)
        else:
            self.cb_reue.setEnabled(True)

        # Reue Checkbox (StGB §35): reduces wanteds by 2 (minimum 1), fine unchanged!
        final_wanteds = max_wanteds
        if self.cb_reue.isChecked() and final_wanteds > 0:
            final_wanteds = max(1, final_wanteds - 2)

        # Parse Systemwanteds
        sys_str = self.input_system_wanteds.text().strip()
        sys_wanteds = 0
        try:
            sys_wanteds = int(sys_str)
        except ValueError:
            sys_wanteds = 0

        total_wanteds = final_wanteds + sys_wanteds

        # Update Grandkasten Money Display
        self.lbl_total_fine.setText(f"${max_fine:,.0f}".replace(",", "."))

        # Update Grandkasten 5 Big Stars
        # Active gold stars for crime wanteds, silver for system wanteds, dark gray for empty
        star_html = ""
        total_slots = max(5, total_wanteds)
        for i in range(total_slots):
            if i < final_wanteds:
                star_html += "<span style='color: #ffcc00;'>★</span> "
            elif i < total_wanteds:
                star_html += "<span style='color: #94a3b8;'>★</span> "
            else:
                star_html += "<span style='color: #272733;'>★</span> "

        self.lbl_star_row.setText(star_html.strip())

        # Wanteds subtext
        if sys_wanteds > 0:
            self.lbl_wanteds_text.setText(f"{total_wanteds} Wanteds ({final_wanteds} Tat + {sys_wanteds} Sys)")
        else:
            self.lbl_wanteds_text.setText(f"{final_wanteds} Wanteds" if final_wanteds > 0 else "0 Wanteds")

        # Warning box
        if warnings:
            self.lbl_warning_box.setText("<br>".join(warnings))
            self.lbl_warning_box.setVisible(True)
        else:
            self.lbl_warning_box.setVisible(False)
            self.lbl_warning_box.setText("")

        # Build Aktenvermerk (1:1 Grandkasten Format)
        plate_str = self.input_plate.text().strip()
        officer_name = self.input_officer.text().strip()
        orga_val = self.combo_orga.currentText()
        if orga_val == "- Orga -":
            orga_val = ""

        if not offense_ids and sys_wanteds == 0 and not officer_name and not plate_str:
            self.txt_aktenvermerk.setPlainText("")
            return

        now = datetime.datetime.now()
        date_prefix = now.strftime("%d.%m %H:%M")

        # Paragraphs joined by ' + '
        parts = [oid for oid in offense_ids if oid]

        if self.cb_reue.isChecked():
            parts.append("StGB §35")

        if self.cb_repeat.isChecked() and has_stvo:
            parts.append("StVO §25 lit. 2")

        if sys_wanteds > 0:
            parts.append(f"{sys_wanteds} Systemwanteds")

        crimes_part = " + ".join(parts) if parts else "..."
        akte = f"{date_prefix} - {crimes_part}"

        # Officer tag
        if officer_name:
            if orga_val and orga_val != "- Orga -":
                akte += f" @{orga_val} {officer_name}"
            else:
                if officer_name.startswith("@"):
                    akte += f" {officer_name}"
                else:
                    akte += f" @{officer_name}"

        # Plate tag
        if plate_str:
            akte += f" - {plate_str}"

        self.txt_aktenvermerk.setPlainText(akte)

    def copy_aktenvermerk(self):
        text = self.txt_aktenvermerk.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.btn_copy_akte.setText("✅ Kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_copy_akte.setText("📋 Aktenvermerk kopieren"))

    def reset_calculator(self):
        self.selected_items.clear()
        for card in self.cards_by_key.values():
            card.reset()
        self.search_input.clear()
        self.input_officer.clear()
        self.input_plate.clear()
        self.input_system_wanteds.clear()
        self.cb_reue.setChecked(False)
        self.cb_repeat.setChecked(False)
        self.recalculate()

    # --- TAB 2: TOW RECHNER (1:1 Grandkasten & Screenshot) ---
    def setup_tow_tab(self):
        layout = QVBoxLayout(self.tab_tow)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Exact Dark Navy Frame from User Screenshot
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e243b;
                border: 1px solid #2e3a59;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(12)

        tow_title = QLabel("🚙 <span style='font-size: 15px; font-weight: bold;'>TOW Rechner</span>")
        tow_title.setStyleSheet("color: #38bdf8;")
        c_lay.addWidget(tow_title)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Row 1: Kennzeichen & Ort
        grid.addWidget(QLabel("Kennzeichen:"), 0, 0)
        self.tow_plate = QLineEdit()
        self.tow_plate.setPlaceholderText("ABC-123")
        self.tow_plate.setStyleSheet("background-color: #14192b; border: 1px solid #2b3655; color: #ffffff;")
        grid.addWidget(self.tow_plate, 0, 1)

        grid.addWidget(QLabel("Ort:"), 0, 2)
        self.tow_location = QLineEdit()
        self.tow_location.setPlaceholderText("z.B. Market")
        self.tow_location.setStyleSheet("background-color: #14192b; border: 1px solid #2b3655; color: #ffffff;")
        grid.addWidget(self.tow_location, 0, 3)

        # Row 2: Zone & Gefahren
        grid.addWidget(QLabel("Zone:"), 1, 0)
        self.tow_zone = QComboBox()
        self.tow_zone.setStyleSheet("background-color: #14192b; border: 1px solid #2b3655; color: #ffffff;")
        self.tow_zone.addItem("Innerorts (150 km/h)", 150)
        self.tow_zone.addItem("Verkehrsberuhigte Bereiche (50 km/h)", 50)
        self.tow_zone.addItem("Außerorts (200 km/h)", 200)
        self.tow_zone.addItem("Highway (350 km/h)", 350)
        self.tow_zone.addItem("Freeway (300 km/h)", 300)
        grid.addWidget(self.tow_zone, 1, 1)

        grid.addWidget(QLabel("Gefahren:"), 1, 2)
        self.tow_speed = QLineEdit()
        self.tow_speed.setPlaceholderText("km/h")
        self.tow_speed.setStyleSheet("background-color: #14192b; border: 1px solid #2b3655; color: #ffffff;")
        grid.addWidget(self.tow_speed, 1, 3)

        c_lay.addLayout(grid)

        # Row 3: Wiederholungstäter Checkbox
        self.tow_repeat = QCheckBox("⚠️ Wiederholungstäter (StVO §25 lit. 2)")
        self.tow_repeat.setStyleSheet("font-size: 13px; font-weight: bold; color: #f97316;")
        c_lay.addWidget(self.tow_repeat)

        # Row 4: Berechnen Button (Exact Blue Button)
        self.btn_tow_calc = QPushButton("Berechnen")
        self.btn_tow_calc.setCursor(Qt.PointingHandCursor)
        self.btn_tow_calc.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_tow_calc.clicked.connect(self.calculate_tow)
        c_lay.addWidget(self.btn_tow_calc)

        # Row 5: Results Frame (Dark navy container)
        res_frame = QFrame()
        res_frame.setStyleSheet("background: #14192b; border: 1px solid #222b44; border-radius: 6px; padding: 10px;")
        res_lay = QVBoxLayout(res_frame)
        res_lay.setSpacing(6)

        self.lbl_tow_bussgeld = QLabel("Bußgeld: $ 0")
        self.lbl_tow_bussgeld.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        res_lay.addWidget(self.lbl_tow_bussgeld)

        res_lay.addWidget(QLabel("Generierte Akte:"))
        self.tow_akte = QLineEdit()
        self.tow_akte.setReadOnly(True)
        self.tow_akte.setStyleSheet("""
            QLineEdit {
                background: #000000;
                border: 2px solid #22c55e;
                color: #22c55e;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        res_lay.addWidget(self.tow_akte)

        c_lay.addWidget(res_frame)

        # Row 6: Kopieren & Reset Buttons (Exact Green & Blue-Slate)
        row_btn = QHBoxLayout()
        self.btn_tow_copy = QPushButton("📋 Kopieren")
        self.btn_tow_copy.setCursor(Qt.PointingHandCursor)
        self.btn_tow_copy.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 9px;
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
        self.btn_tow_reset.setCursor(Qt.PointingHandCursor)
        self.btn_tow_reset.setStyleSheet("""
            QPushButton {
                background-color: #1e243b;
                border: 1px solid #3b82f6;
                color: #ffffff;
                font-size: 13px;
                padding: 9px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e3a59;
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
            self.btn_tow_copy.setText("✅ Kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_tow_copy.setText("📋 Kopieren"))

    def reset_tow(self):
        self.tow_plate.clear()
        self.tow_location.clear()
        self.tow_speed.clear()
        self.tow_repeat.setChecked(False)
        self.tow_zone.setCurrentIndex(0)
        self.lbl_tow_bussgeld.setText("Bußgeld: $ 0")
        self.tow_akte.clear()

    # --- KEY & EVENT HANDLERS ---
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Escape, Qt.Key_F12):
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_overlay()

    def show_calculator(self):
        self.show_overlay()

    def show_overlay(self):
        self.resize_to_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()

    def update_theme(self, theme_colors=None):
        pass
