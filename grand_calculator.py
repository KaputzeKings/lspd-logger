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

def ensure_check_icon():
    icon_path = os.path.join(BASE_DIR, "check_icon.png")
    try:
        pm = QPixmap(20, 20)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor('#ffffff'), 2.6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(4, 10, 8, 15)
        p.drawLine(8, 15, 16, 5)
        p.end()
        pm.save(icon_path)
    except Exception:
        pass
    return icon_path.replace("\\", "/")

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
        self.v_buttons = []

        self.setCursor(Qt.PointingHandCursor)
        self.init_card_ui()

    def init_card_ui(self):
        self.apply_style(False)

        c_lay = QVBoxLayout(self)
        c_lay.setContentsMargins(10, 6, 10, 6)
        c_lay.setSpacing(4)

        # Row 1: Checkbox, Name, Fine, Wanteds
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.cb = QCheckBox(f"<b>{self.item_id}</b> — {self.name}")
        self.cb.setStyleSheet("font-size: 13px; font-weight: normal; color: #f1f5f9;")
        self.cb.clicked.connect(self.on_cb_clicked)
        row1.addWidget(self.cb, stretch=1)

        fine_str = f"${self.fine:,.0f}".replace(",", ".")
        fine_badge = QLabel(fine_str)
        fine_badge.setStyleSheet("background: #064e3b; color: #34d399; font-weight: bold; border-radius: 4px; padding: 3px 8px; font-size: 12px;")
        row1.addWidget(fine_badge)

        w_str = f"★ {self.wanteds}" if self.wanteds > 0 else "0 Wanteds"
        w_badge = QLabel(w_str)
        w_badge.setStyleSheet("background: #78350f; color: #fbbf24; font-weight: bold; border-radius: 4px; padding: 3px 8px; font-size: 12px;")
        row1.addWidget(w_badge)

        c_lay.addLayout(row1)

        # Row 2: Voluntary / Graue Wanteds & License info
        if self.voluntary_w > 0 or "entziehen" in self.info.lower():
            row2 = QHBoxLayout()
            row2.setSpacing(6)
            if self.voluntary_w > 0:
                v_lbl = QLabel(f"<span style='color:#a1a1aa; font-size:11px;'>Graue Wanteds (0-{self.voluntary_w}):</span>")
                row2.addWidget(v_lbl)

                for count in range(self.voluntary_w + 1):
                    btn_v = QPushButton(str(count))
                    btn_v.setFixedSize(26, 22)
                    btn_v.setCheckable(True)
                    btn_v.setChecked(count == 0)
                    btn_v.setStyleSheet("""
                        QPushButton {
                            background: #27142b;
                            color: #d8b4fe;
                            border: 1px solid #701a75;
                            border-radius: 4px;
                            padding: 0px;
                            font-size: 11px;
                        }
                        QPushButton:checked {
                            background: #a855f7;
                            color: #ffffff;
                            font-weight: bold;
                        }
                    """)
                    btn_v.clicked.connect(lambda _, c=count: self.on_voluntary_clicked(c))
                    self.v_buttons.append(btn_v)
                    row2.addWidget(btn_v)

                if self.voluntary_f > 0:
                    v_fine_lbl = QLabel(f"<span style='color:#34d399; font-size:11px;'>+${self.voluntary_f:,.0f}/W.</span>".replace(",", "."))
                    row2.addWidget(v_fine_lbl)

            if "entziehen" in self.info.lower():
                row2.addStretch()
                entzug_badge = QLabel(f"⚠️ {self.info}")
                entzug_badge.setStyleSheet("background: #450a0a; color: #f87171; font-weight: bold; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
                row2.addWidget(entzug_badge)

            c_lay.addLayout(row2)

    def apply_style(self, selected):
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                OffenseCard {
                    background-color: #221338;
                    border: 2px solid #a855f7;
                    border-radius: 8px;
                }
                OffenseCard:hover {
                    border: 2px solid #c084fc;
                    background-color: #2a1845;
                }
            """)
        else:
            self.setStyleSheet("""
                OffenseCard {
                    background-color: #130d22;
                    border: 1px solid #2e1065;
                    border-radius: 8px;
                }
                OffenseCard:hover {
                    border: 1px solid #7c3aed;
                    background-color: #19122c;
                }
            """)

    def set_selected_visual(self, selected):
        self.apply_style(selected)
        self.cb.blockSignals(True)
        self.cb.setChecked(selected)
        self.cb.blockSignals(False)

    def set_voluntary_visual(self, count):
        for idx, btn in enumerate(self.v_buttons):
            btn.blockSignals(True)
            btn.setChecked(idx == count)
            btn.blockSignals(False)

    def on_cb_clicked(self):
        # Click on the checkbox itself
        self.overlay.toggle_offense(self.item)

    def on_voluntary_clicked(self, count):
        self.overlay.set_voluntary_wanteds(self.item, count)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked inside a child push button (voluntary buttons handle themselves)
            child = self.childAt(event.pos())
            if isinstance(child, QPushButton):
                super().mousePressEvent(event)
                return
            # Otherwise, toggle offense!
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
        self.cards_by_id = {}

        self.check_icon_url = ensure_check_icon()

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
            QCheckBox {{
                color: #f1f5f9;
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid #a855f7;
                border-radius: 4px;
                background-color: #1a1528;
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid #c084fc;
                background-color: #261b3d;
            }}
            QCheckBox::indicator:checked {{
                background-color: #9333ea;
                border: 2px solid #ffffff;
                image: url('{self.check_icon_url}');
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
        title_lbl = QLabel("🛡️ <span style='font-size: 16px; font-weight: bold;'>LSPD Dienst-Rechner</span> <span style='color:#a855f7; font-size:12px;'>(Grandkasten Bußgeld-, Wanteds- & TOW-Rechner)</span>")
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
        self.tabs.addTab(self.tab_tow, "🚙 TOW Rechner")

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

        layout.addLayout(left_box, stretch=60)

        # RIGHT SIDE: Summary, Inputs & Aktenvermerk (40%)
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
        grid.addWidget(QLabel("Bußgeld (Höchststrafe):"), 0, 0)
        self.lbl_total_fine = QLabel("$ 0")
        self.lbl_total_fine.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ade80;")
        grid.addWidget(self.lbl_total_fine, 0, 1)

        grid.addWidget(QLabel("Wanteds (Höchste Tat):"), 1, 0)
        self.lbl_total_wanteds = QLabel("0 Wanteds")
        self.lbl_total_wanteds.setStyleSheet("font-size: 16px; font-weight: bold; color: #fbbf24;")
        grid.addWidget(self.lbl_total_wanteds, 1, 1)

        stats_lay.addLayout(grid)

        # Warning badges on screen (NOT in akte)
        self.lbl_warning_badges = QLabel("")
        self.lbl_warning_badges.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold; background: #3b0707; border: 1px solid #b91c1c; border-radius: 6px; padding: 6px;")
        self.lbl_warning_badges.setVisible(False)
        stats_lay.addWidget(self.lbl_warning_badges)

        right_box.addWidget(stats_frame)

        # Akten-Optionen
        opts_frame = QFrame()
        opts_frame.setStyleSheet(f"background-color: {c['card_bg']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 10px;")
        opts_lay = QVBoxLayout(opts_frame)
        opts_lay.setSpacing(6)

        opts_title = QLabel("⚙️ <b>Optionen für den Aktenvermerk</b>")
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

        self.cb_reue = QCheckBox("🤝 Reue / Kooperation (StGB §35)")
        self.cb_reue.setStyleSheet("font-size: 12px; color: #f472b6; font-weight: bold;")
        self.cb_reue.toggled.connect(self.recalculate)
        opts_lay.addWidget(self.cb_reue)

        self.cb_repeat = QCheckBox("⚠️ Wiederholungstäter (StVO §25 lit. 2)")
        self.cb_repeat.setStyleSheet("font-size: 12px; color: #fb923c; font-weight: bold;")
        self.cb_repeat.toggled.connect(self.recalculate)
        opts_lay.addWidget(self.cb_repeat)

        right_box.addWidget(opts_frame)

        # Aktenvermerk Terminal Text Area (Exact Grandkasten Green Terminal Font)
        akte_frame = QFrame()
        akte_frame.setStyleSheet(f"background-color: {c['card_bg']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 10px;")
        akte_lay = QVBoxLayout(akte_frame)
        akte_lay.setSpacing(6)

        a_title = QLabel("📝 <b>Generierter Aktenvermerk</b> (1:1 Grandkasten)")
        a_title.setStyleSheet("font-size: 13px; color: #d8b4fe;")
        akte_lay.addWidget(a_title)

        self.txt_aktenvermerk = ClickableTerminalEdit()
        self.txt_aktenvermerk.setReadOnly(True)
        self.txt_aktenvermerk.setFixedHeight(75)
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
        """)
        self.txt_aktenvermerk.clicked.connect(self.copy_aktenvermerk)
        akte_lay.addWidget(self.txt_aktenvermerk)

        lbl_hint_copy = QLabel("<span style='color:#a1a1aa; font-size:10px;'>Klicke auf das grüne Feld oder den Button unten zum Kopieren</span>")
        akte_lay.addWidget(lbl_hint_copy)

        btn_row = QHBoxLayout()
        self.btn_copy_akte = QPushButton("📋 Aktenvermerk kopieren")
        self.btn_copy_akte.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981); color: #ffffff; font-size: 13px; font-weight: bold; padding: 8px;")
        self.btn_copy_akte.clicked.connect(self.copy_aktenvermerk)
        btn_row.addWidget(self.btn_copy_akte, stretch=2)

        btn_reset = QPushButton("🔄 Zurücksetzen")
        btn_reset.setStyleSheet("background: #27142b; border: 1px solid #701a75; color: #f472b6; padding: 8px; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_calculator)
        btn_row.addWidget(btn_reset, stretch=1)
        akte_lay.addLayout(btn_row)

        right_box.addWidget(akte_frame)
        right_box.addStretch()

        layout.addLayout(right_box, stretch=40)

        # Build cards once
        self.build_offenses_list()

    def build_offenses_list(self):
        self.cards_by_id = {}
        for cat, items in self.db.items():
            for item in items:
                item_id = item.get("id", "")
                card = OffenseCard(item, self)
                self.cards_by_id[item_id] = card
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
                item_id = item.get("id", "")
                card = self.cards_by_id.get(item_id)
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
            b.setChecked(name == cat_name)
        self.filter_offenses()

    def on_search_changed(self, text):
        self.search_term = text.strip()
        self.filter_offenses()

    def toggle_offense(self, item):
        item_id = item.get("id")
        if item_id in self.selected_items:
            del self.selected_items[item_id]
            is_sel = False
        else:
            self.selected_items[item_id] = {"item": item, "voluntary": 0}
            is_sel = True

        card = self.cards_by_id.get(item_id)
        if card:
            card.set_selected_visual(is_sel)
            if not is_sel:
                card.set_voluntary_visual(0)

        self.recalculate()

    def set_voluntary_wanteds(self, item, count):
        item_id = item.get("id")
        if item_id not in self.selected_items:
            self.selected_items[item_id] = {"item": item, "voluntary": count}
        else:
            self.selected_items[item_id]["voluntary"] = count

        card = self.cards_by_id.get(item_id)
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

        for item_id, data in self.selected_items.items():
            item = data["item"]
            vol_count = data.get("voluntary", 0)
            base_wanteds = item.get("wanteds", 0) or item.get("mandatoryWanteds", 0) or 0
            fine = item.get("fine", 0) or 0

            offense_ids.append(item_id)

            if base_wanteds > max_base_wanteds or (base_wanteds == max_base_wanteds and fine > (most_severe.get("fine", 0) if most_severe else 0)):
                max_base_wanteds = base_wanteds
                most_severe = item

            # License warnings apply across all selected offenses
            info = item.get("info", "")
            if "waffenschein" in info.lower():
                warnings.add("⚠️ Waffenschein muss entzogen werden!")
            if "führerschein" in info.lower():
                warnings.add("⚠️ Führerschein muss entzogen werden!")

        if most_severe:
            item_id = most_severe.get("id")
            vol_count = self.selected_items.get(item_id, {}).get("voluntary", 0)
            base_fine = most_severe.get("fine", 0) or 0
            vol_fine = most_severe.get("voluntaryFine", 0) or 0

            max_fine = base_fine + (vol_count * vol_fine)
            base_w = most_severe.get("wanteds", 0) or most_severe.get("mandatoryWanteds", 0) or 0
            max_wanteds = base_w + vol_count
        else:
            # Fallback
            for item_id, data in self.selected_items.items():
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
        has_stvo = any(oid.startswith("StVO") for oid in offense_ids)
        if hasattr(self, 'cb_repeat'):
            self.cb_repeat.setEnabled(has_stvo)
            if not has_stvo:
                self.cb_repeat.setChecked(False)

        # Wiederholungstäter doubles fine on StVO
        if hasattr(self, 'cb_repeat') and self.cb_repeat.isChecked() and has_stvo:
            max_fine *= 2

        # Check if Reue is allowed (cannot use Reue on severe crimes)
        prevents_reue = any(oid in ["StGB §25", "§6 StPO", "StPO §6", "StGB §4.1", "StGB §27"] for oid in offense_ids)
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

        # Update Live Labels
        self.lbl_total_fine.setText(f"${max_fine:,.0f}".replace(",", "."))
        if sys_wanteds > 0:
            self.lbl_total_wanteds.setText(f"{total_wanteds} Wanteds ({final_wanteds} Tat + {sys_wanteds} Sys)")
        else:
            star_str = "★ " * final_wanteds if final_wanteds > 0 else ""
            self.lbl_total_wanteds.setText(f"{final_wanteds} Wanteds  {star_str}")

        if warnings:
            self.lbl_warning_badges.setText("<br>".join(warnings))
            self.lbl_warning_badges.setVisible(True)
        else:
            self.lbl_warning_badges.setVisible(False)
            self.lbl_warning_badges.setText("")

        # Build Aktenvermerk (Exact 1:1 Grandkasten Format)
        if not offense_ids and sys_wanteds == 0 and not self.input_officer.text().strip():
            self.txt_aktenvermerk.setPlainText("")
            return

        now = datetime.datetime.now()
        date_prefix = now.strftime("%d.%m %H:%M")

        # Parts joined by ' + '
        parts = list(offense_ids) if offense_ids else []

        if self.cb_reue.isChecked():
            parts.append("StGB §35")

        if hasattr(self, 'cb_repeat') and self.cb_repeat.isChecked() and has_stvo:
            parts.append("StVO §25 lit. 2")

        if sys_wanteds > 0:
            parts.append(f"{sys_wanteds} Systemwanteds")

        crimes_part = " + ".join(parts) if parts else "..."
        akte = f"{date_prefix} - {crimes_part}"

        officer = self.input_officer.text().strip()
        if officer:
            if officer.startswith("@"):
                akte += f" {officer}"
            else:
                akte += f" @{officer}"

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
        for card in self.cards_by_id.values():
            card.reset()
        self.search_input.clear()
        self.input_officer.clear()
        self.input_system_wanteds.clear()
        self.cb_reue.setChecked(False)
        if hasattr(self, 'cb_repeat'):
            self.cb_repeat.setChecked(False)
        self.recalculate()

    # --- TAB 2: TOW RECHNER (1:1 Grandkasten) ---
    def setup_tow_tab(self):
        c = self.theme_colors
        layout = QVBoxLayout(self.tab_tow)
        layout.setContentsMargins(16, 16, 16, 16)
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

        tow_title = QLabel("🚙 <span style='font-size: 15px; font-weight: bold;'>TOW Rechner</span>")
        tow_title.setStyleSheet("color: #38bdf8;")
        c_lay.addWidget(tow_title)

        grid = QGridLayout()
        grid.setSpacing(10)

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
        self.tow_zone.addItem("Freeway (300 km/h)", 300)
        self.tow_zone.addItem("Highway (350 km/h)", 350)
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
        self.btn_tow_calc.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.btn_tow_calc.clicked.connect(self.calculate_tow)
        c_lay.addWidget(self.btn_tow_calc)

        # Row 5: Results Frame
        res_frame = QFrame()
        res_frame.setStyleSheet("background: #090614; border: 1px solid #1e293b; border-radius: 6px; padding: 10px;")
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

        # Row 6: Kopieren & Reset Buttons
        row_btn = QHBoxLayout()
        self.btn_tow_copy = QPushButton("📋 Kopieren")
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

        self.btn_tow_reset = QPushButton("🔄 Reset")
        self.btn_tow_reset.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #3b82f6;
                color: #60a5fa;
                font-size: 13px;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
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
            self.btn_tow_copy.setText("✅ Kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_tow_copy.setText("📋 Kopieren"))

    def reset_tow(self):
        self.tow_plate.clear()
        self.tow_location.clear()
        self.tow_speed.clear()
        self.tow_repeat.setChecked(False)
        self.tow_zone.setCurrentIndex(1)
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

    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.init_ui()
