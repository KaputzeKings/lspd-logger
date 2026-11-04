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
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon, QPainter, QAction, QKeyEvent, QPen, QPalette

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

def normalize_search_text(t):
    if not t:
        return ""
    t = t.lower()
    t = t.replace('ae', 'a').replace('oe', 'o').replace('ue', 'u').replace('ss', 's')
    t = t.replace('ä', 'a').replace('ö', 'o').replace('ü', 'u').replace('ß', 's')
    t = t.replace('§', ' ').replace('/', ' ').replace('-', ' ').replace('.', ' ').replace(',', ' ')
    return ' '.join(t.split())

CALC_THEMES = {
    "Grandkasten Cyberpunk": {
        "bg": "#0f111a",
        "surface": "#141724",
        "card_bg": "#1e202f",
        "card_hover": "#26293c",
        "border": "#00d2ff",
        "border_subtle": "#2e334a",
        "accent": "#3b82f6",
        "accent_text": "#ffffff",
        "card_active_bg": "#24253e",
        "card_active_border": "#8b5cf6",
        "text": "#e2e8f0",
        "text_muted": "#8892b0",
        "money": "#22c55e",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    },
    "Schwarz-Grau-Weiß (Monochrome)": {
        "bg": "#050505",
        "surface": "#111113",
        "card_bg": "#18181b",
        "card_hover": "#27272a",
        "border": "#71717a",
        "border_subtle": "#2a2a32",
        "accent": "#e4e4e7",
        "accent_text": "#000000",
        "card_active_bg": "#222228",
        "card_active_border": "#ffffff",
        "text": "#ffffff",
        "text_muted": "#a1a1aa",
        "money": "#4ade80",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    },
    "Schwarz-Lila (Standard)": {
        "bg": "#0a0614",
        "surface": "#130d22",
        "card_bg": "#19122c",
        "card_hover": "#221338",
        "border": "#a855f7",
        "border_subtle": "#2e1245",
        "accent": "#a855f7",
        "accent_text": "#ffffff",
        "card_active_bg": "#241038",
        "card_active_border": "#c084fc",
        "text": "#f5f3ff",
        "text_muted": "#d8b4fe",
        "money": "#4ade80",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    },
    "LSPD Cyber Blue": {
        "bg": "#060b17",
        "surface": "#0c152a",
        "card_bg": "#111f3d",
        "card_hover": "#172b54",
        "border": "#38bdf8",
        "border_subtle": "#16284a",
        "accent": "#38bdf8",
        "accent_text": "#000000",
        "card_active_bg": "#102342",
        "card_active_border": "#38bdf8",
        "text": "#f0f9ff",
        "text_muted": "#7dd3fc",
        "money": "#4ade80",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    },
    "Tactical Stealth Red": {
        "bg": "#0d0607",
        "surface": "#170a0c",
        "card_bg": "#220e11",
        "card_hover": "#311419",
        "border": "#ef4444",
        "border_subtle": "#381014",
        "accent": "#ef4444",
        "accent_text": "#ffffff",
        "card_active_bg": "#2e0c10",
        "card_active_border": "#f87171",
        "text": "#ffffff",
        "text_muted": "#fca5a5",
        "money": "#4ade80",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    },
    "Emerald Special Forces": {
        "bg": "#040e08",
        "surface": "#0a1c10",
        "card_bg": "#0f2817",
        "card_hover": "#163a22",
        "border": "#10b981",
        "border_subtle": "#12331c",
        "accent": "#10b981",
        "accent_text": "#000000",
        "card_active_bg": "#0d2615",
        "card_active_border": "#34d399",
        "text": "#ffffff",
        "text_muted": "#6ee7b7",
        "money": "#4ade80",
        "stars": "#ffcc00",
        "danger": "#ef4444"
    }
}

PROMPTER_TEMPLATES = {
    "Miranda-Warnung (Standard)": [
        "Sie haben das Recht zu schweigen, alles was Sie sagen kann und wird gegen Sie verwendet werden.",
        "Ab 2 Wanteds haben Sie das Recht auf einen staatlich anerkannten Anwalt, den Sie selbst benennen müssen.",
        "Wenn kein Anwalt verfügbar ist, wird Ihnen ein Pflichtverteidiger gestellt.",
        "Die Judikative übernimmt der Exekutivbeamte.",
        "Wenn ein Anwalt hinzugezogen wird, kann es länger als 25 Minuten dauern.",
        "Haben Sie ihre Rechte verstanden?"
    ],
    "Miranda-Warnung (Wiederholung)": [
        "Ich wiederhole Ihre Rechte ein zweites und letztes Mal:",
        "Sie haben das Recht zu schweigen, alles was Sie sagen kann und wird gegen Sie verwendet werden.",
        "Ab 2 Wanteds haben Sie das Recht auf einen staatlich anerkannten Anwalt, den Sie selbst benennen müssen.",
        "Wenn kein Anwalt verfügbar ist, wird Ihnen ein Pflichtverteidiger gestellt.",
        "Die Judikative übernimmt der Exekutivbeamte.",
        "Wenn ein Anwalt hinzugezogen wird, kann es länger als 25 Minuten dauern.",
        "Haben Sie ihre Rechte nun verstanden?"
    ],
    "Allgemeine Verkehrskontrolle": [
        "Guten Tag, Los Santos Police Department.",
        "Grund für das Anhalten Ihres Fahrzeugs ist eine allgemeine Verkehrskontrolle.",
        "Bitte schalten Sie den Motor ab und lassen Sie die Hände am Lenkrad.",
        "Händigen Sie mir bitte Führerschein und Fahrzeugpapiere aus."
    ],
    "Durchsuchungsbelehrung (§ Dienstvorschrift)": [
        "Sie werden nun gemäß der geltenden Dienstvorschriften nach Waffen, Munition und Betäubungsmitteln durchsucht.",
        "Leisten Sie keinen Widerstand und verhalten Sie sich ruhig.",
        "Jeder Fluchtversuch oder Widerstand wird als schwere Straftat geahndet."
    ],
    "Platzverweis & Sperrzone (§ BDG)": [
        "Sie befinden sich im Bereich eines laufenden polizeilichen Einsatzes.",
        "Ich erteile Ihnen hiermit einen formellen Platzverweis.",
        "Entfernen Sie sich unverzüglich um mindestens 50 Meter von diesem Bereich.",
        "Sollten Sie der Aufforderung nicht nachkommen, wird unmittelbarer Zwang angewendet und Sie werden inhaftiert."
    ],
    "Blutentnahme & Drogentest": [
        "Aufgrund des Verdachts auf das Führen eines Kraftfahrzeugs unter berauschenden Mitteln ordne ich eine Blutentnahme an.",
        "Eine Verweigerung zieht den sofortigen Führerscheinentzug sowie ein Strafverfahren nach sich."
    ],
    "Reue-Aufklärung (§35 StGB)": [
        "Gemäß §35 des Strafgesetzbuches haben Sie die Möglichkeit, Reue zu zeigen und umfassend zu kooperieren.",
        "Bei ehrlicher Reue und Geständnis kann Ihre Strafe um bis zu 2 Wanteds gemildert werden."
    ]
}

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
        self.is_starred = False

        self.setObjectName("offenseCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setFixedHeight(84)

        self.setCursor(Qt.PointingHandCursor)
        self.init_card_ui()

    def get_theme(self):
        return getattr(self.overlay, 'theme_data', CALC_THEMES["Grandkasten Cyberpunk"])

    def init_card_ui(self):
        t = self.get_theme()
        c_lay = QVBoxLayout(self)
        c_lay.setContentsMargins(12, 8, 12, 8)
        c_lay.setSpacing(3)

        # Row 1: Paragraph ID on left, License Pill & Star Icon on right
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(6)

        self.lbl_id = QLabel(self.item_id)
        self.lbl_id.setStyleSheet(f"color: {t['accent']}; font-size: 13px; font-weight: bold; background: transparent;")
        row1.addWidget(self.lbl_id)

        self.lbl_check = QLabel("✓")
        self.lbl_check.setStyleSheet(f"color: {t.get('card_active_border', '#8b5cf6')}; font-size: 13px; font-weight: 900; background: transparent;")
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
                padding: 1px 6px;
                font-size: 9px;
            """)
            row1.addWidget(entzug_badge)

        self.btn_star = QPushButton("★")
        self.btn_star.setFixedSize(20, 20)
        self.btn_star.setCursor(Qt.PointingHandCursor)
        self.btn_star.setStyleSheet("background: transparent; border: none; color: #475569; font-size: 14px; padding: 0;")
        self.btn_star.clicked.connect(self.toggle_star)
        row1.addWidget(self.btn_star)

        c_lay.addLayout(row1)

        # Row 2: Offense Description (Clean Grandkasten typography)
        self.lbl_name = QLabel(self.name)
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setStyleSheet(f"color: {t['text']}; font-size: 12px; font-weight: 500; line-height: 1.2; background: transparent;")
        c_lay.addWidget(self.lbl_name)

        # Row 3: Wanteds Stars / Gray buttons on Left, Fine on Right
        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 2, 0, 0)
        row3.setSpacing(6)

        stars_container = QHBoxLayout()
        stars_container.setSpacing(4)

        if self.wanteds == 0 and self.voluntary_w == 0:
            lbl_none = QLabel("<span style='color: #64748b; font-size: 12px; font-weight: bold;'>-</span>")
            lbl_none.setStyleSheet("background: transparent;")
            stars_container.addWidget(lbl_none)
        else:
            # Mandatory gold stars
            if self.wanteds > 0:
                stars_gold = "★ " * self.wanteds
                lbl_gold = QLabel(f"<span style='color: #ffcc00; font-size: 13px; font-weight: bold;'>{stars_gold.strip()}</span>")
                lbl_gold.setStyleSheet("background: transparent;")
                stars_container.addWidget(lbl_gold)

            # Voluntary gray wanteds selector
            if self.voluntary_w > 0:
                lbl_vol = QLabel("<span style='color: #94a3b8; font-size: 10px; margin-left: 2px;'>Grau:</span>")
                lbl_vol.setStyleSheet("background: transparent;")
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
                            color: #ffffff;
                        }
                        QPushButton:checked {
                            background: #ffcc00;
                            color: #000000;
                            border-color: #ffcc00;
                            font-weight: 900;
                        }
                    """)
                    btn_v.clicked.connect(lambda _, c=count: self.on_voluntary_clicked(c))
                    self.v_buttons.append(btn_v)
                    stars_container.addWidget(btn_v)

        row3.addLayout(stars_container)
        row3.addStretch()

        # Fine Display (Grandkasten Clean Green text, NO dark background box)
        fine_str = f"${self.fine:,.0f}".replace(",", ".")
        self.lbl_fine = QLabel(fine_str)
        self.lbl_fine.setStyleSheet(f"""
            color: {t.get('money', '#22c55e')};
            background: transparent;
            border: none;
            font-size: 13px;
            font-weight: 900;
        """)
        row3.addWidget(self.lbl_fine)

        c_lay.addLayout(row3)
        self.apply_style(False)

    def toggle_star(self):
        self.is_starred = not self.is_starred
        color = "#eab308" if self.is_starred else "#475569"
        self.btn_star.setStyleSheet(f"background: transparent; border: none; color: {color}; font-size: 14px; padding: 0;")

    def apply_style(self, selected):
        self.is_selected = selected
        t = self.get_theme()
        active_border = t.get('card_active_border', '#8b5cf6')
        active_bg = t.get('card_active_bg', '#24253e')
        if selected:
            self.setStyleSheet(f"""
                QFrame#offenseCard, #offenseCard {{
                    background-color: {active_bg};
                    border: 2px solid {active_border};
                    border-radius: 8px;
                }}
                QFrame#offenseCard:hover, #offenseCard:hover {{
                    border: 2px solid {active_border};
                }}
            """)
            if hasattr(self, 'lbl_check'):
                self.lbl_check.setStyleSheet(f"color: {active_border}; font-size: 13px; font-weight: 900; background: transparent;")
                self.lbl_check.setVisible(True)
            if hasattr(self, 'lbl_id'):
                self.lbl_id.setStyleSheet(f"color: {t['accent']}; font-size: 13px; font-weight: bold; background: transparent;")
        else:
            self.setStyleSheet(f"""
                QFrame#offenseCard, #offenseCard {{
                    background-color: {t['card_bg']};
                    border: 1px solid {t['border_subtle']};
                    border-radius: 8px;
                }}
                QFrame#offenseCard:hover, #offenseCard:hover {{
                    background-color: {t['card_hover']};
                    border: 1px solid {t['accent']};
                }}
            """)
            if hasattr(self, 'lbl_check'):
                self.lbl_check.setVisible(False)
            if hasattr(self, 'lbl_id'):
                self.lbl_id.setStyleSheet(f"color: {t['accent']}; font-size: 13px; font-weight: bold; background: transparent;")

        if hasattr(self, 'lbl_fine'):
            self.lbl_fine.setStyleSheet(f"color: {t.get('money', '#22c55e')}; background: transparent; border: none; font-size: 13px; font-weight: 900;")
        if hasattr(self, 'lbl_name'):
            self.lbl_name.setStyleSheet(f"color: {t['text']}; font-size: 12px; font-weight: 500; line-height: 1.2; background: transparent;")

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
            child = self.childAt(event.pos())
            if isinstance(child, QPushButton):
                super().mousePressEvent(event)
                return
            self.overlay.toggle_offense(self.item)
            event.accept()
        else:
            super().mousePressEvent(event)

    def reset(self):
        self.set_selected_visual(False)
        self.set_voluntary_visual(0)

class FloatingPrompterHUD(QWidget):
    def __init__(self, main_calc, theme_data, parent=None):
        super().__init__(parent)
        self.main_calc = main_calc
        self.theme_data = theme_data
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.drag_pos = None
        self.setFixedSize(600, 185)
        self.init_ui()

    def init_ui(self):
        t = self.theme_data
        self.setStyleSheet(f"""
            QFrame#hudContainer {{
                background-color: {t['bg']};
                border: 2px solid {t['accent']};
                border-radius: 12px;
            }}
            QLabel {{
                color: {t['text']};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame(self)
        self.container.setObjectName("hudContainer")
        c_lay = QVBoxLayout(self.container)
        c_lay.setContentsMargins(12, 8, 12, 10)
        c_lay.setSpacing(6)

        # Header bar (Draggable)
        header = QHBoxLayout()
        header.setSpacing(8)

        self.lbl_hud_title = QLabel(f"📜 <b style='color: {t['accent']};'>TELEPROMPTER</b>")
        header.addWidget(self.lbl_hud_title)

        self.combo_hud_template = QComboBox()
        self.combo_hud_template.setStyleSheet(f"background: {t['card_bg']}; color: {t['text']}; border: 1px solid {t['border_subtle']}; border-radius: 4px; padding: 2px 6px; font-size: 11px;")
        for name in PROMPTER_TEMPLATES.keys():
            self.combo_hud_template.addItem(name)
        self.combo_hud_template.currentTextChanged.connect(self.main_calc.prompter_on_template_change)
        header.addWidget(self.combo_hud_template, stretch=1)

        self.lbl_hud_step = QLabel("[1/5]")
        self.lbl_hud_step.setStyleSheet(f"color: {t['text_muted']}; font-weight: bold; font-size: 11px;")
        header.addWidget(self.lbl_hud_step)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("background: #ef4444; color: #ffffff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px;")
        btn_close.clicked.connect(self.hide)
        header.addWidget(btn_close)

        c_lay.addLayout(header)

        # Sentence Display Box
        self.sentence_box = QFrame()
        self.sentence_box.setStyleSheet(f"background: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 8px; padding: 8px;")
        s_lay = QVBoxLayout(self.sentence_box)
        s_lay.setContentsMargins(8, 6, 8, 6)

        self.lbl_sentence = QLabel("Sie haben das Recht zu schweigen, alles was Sie sagen kann und wird gegen Sie verwendet werden.")
        self.lbl_sentence.setWordWrap(True)
        self.lbl_sentence.setAlignment(Qt.AlignCenter)
        self.lbl_sentence.setStyleSheet(f"color: {t['text']}; font-size: 14px; font-weight: 700; line-height: 1.3;")
        s_lay.addWidget(self.lbl_sentence)

        c_lay.addWidget(self.sentence_box, stretch=1)

        # Controls Row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(6)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(28, 26)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setStyleSheet(f"background: {t['card_bg']}; color: {t['text']}; border: 1px solid {t['border_subtle']}; border-radius: 5px; font-size: 11px; font-weight: bold;")
        self.btn_prev.clicked.connect(self.main_calc.prompter_prev)
        ctrl_row.addWidget(self.btn_prev)

        self.btn_copy = QPushButton("📋 Kopieren")
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.setStyleSheet(f"background: {t['card_bg']}; color: #38bdf8; border: 1px solid #0284c7; border-radius: 5px; padding: 4px 8px; font-size: 11px; font-weight: bold;")
        self.btn_copy.clicked.connect(self.main_calc.prompter_copy_current)
        ctrl_row.addWidget(self.btn_copy)

        self.btn_auto = QPushButton("▶ Auto (3s)")
        self.btn_auto.setCursor(Qt.PointingHandCursor)
        self.btn_auto.setStyleSheet("background: #059669; color: #ffffff; border: none; border-radius: 5px; padding: 4px 9px; font-size: 11px; font-weight: bold;")
        self.btn_auto.clicked.connect(self.main_calc.toggle_autoplay)
        ctrl_row.addWidget(self.btn_auto)

        self.btn_next = QPushButton("▶ Weiter")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setStyleSheet(f"background: {t['accent']}; color: {t['accent_text']}; border: none; border-radius: 5px; padding: 4px 12px; font-size: 11px; font-weight: 900;")
        self.btn_next.clicked.connect(self.main_calc.prompter_next)
        ctrl_row.addWidget(self.btn_next, stretch=1)

        # Mini Attorney Timer Indicator
        self.lbl_hud_timer = QLabel("⏱️ 05:00")
        self.lbl_hud_timer.setCursor(Qt.PointingHandCursor)
        self.lbl_hud_timer.setStyleSheet(f"background: {t['card_bg']}; color: #38bdf8; border: 1px solid {t['border_subtle']}; border-radius: 5px; padding: 4px 7px; font-size: 11px; font-weight: bold;")
        self.lbl_hud_timer.mousePressEvent = lambda _: self.main_calc.toggle_attorney_timer()
        ctrl_row.addWidget(self.lbl_hud_timer)

        c_lay.addLayout(ctrl_row)
        main_layout.addWidget(self.container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Space, Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter):
            self.main_calc.prompter_next()
            event.accept()
        elif event.key() in (Qt.Key_Left, Qt.Key_Backspace):
            self.main_calc.prompter_prev()
            event.accept()
        elif event.key() == Qt.Key_C:
            self.main_calc.prompter_copy_current()
            event.accept()
        elif event.key() == Qt.Key_A:
            self.main_calc.toggle_autoplay()
            event.accept()
        elif event.key() in (Qt.Key_Escape, Qt.Key_F10):
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def hideEvent(self, event):
        if hasattr(self, 'main_calc'):
            self.main_calc.stop_autoplay()
        super().hideEvent(event)

    def update_theme(self, theme_data):
        self.theme_data = theme_data
        t = theme_data
        if hasattr(self, 'container'):
            self.container.setStyleSheet(f"""
                QFrame#hudContainer {{
                    background-color: {t['bg']};
                    border: 2px solid {t['accent']};
                    border-radius: 12px;
                }}
            """)
        if hasattr(self, 'lbl_hud_title'):
            self.lbl_hud_title.setText(f"📜 <b style='color: {t['accent']};'>TELEPROMPTER</b>")
        if hasattr(self, 'sentence_box'):
            self.sentence_box.setStyleSheet(f"background: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 8px; padding: 8px;")
        if hasattr(self, 'btn_next'):
            self.btn_next.setStyleSheet(f"background: {t['accent']}; color: {t['accent_text']}; border: none; border-radius: 5px; padding: 5px 14px; font-size: 11px; font-weight: 900;")

class GrandCalculatorOverlay(QWidget):
    closed = Signal()

    def __init__(self, theme_name=None, parent=None):
        super().__init__(parent)
        self.db = load_grandkasten_db()
        self.selected_items = {} # unique_key -> {"item": item, "voluntary": count}
        self.current_category = "Alle"
        self.search_term = ""
        self.cards_by_key = {}

        # Theme Initialization
        initial_theme = theme_name or "Grandkasten Cyberpunk"
        if isinstance(initial_theme, dict):
            self.theme_data = initial_theme
            self.current_theme_name = "Benutzerdefiniert"
        else:
            self.current_theme_name = initial_theme if initial_theme in CALC_THEMES else "Grandkasten Cyberpunk"
            self.theme_data = CALC_THEMES[self.current_theme_name]

        self.setWindowTitle("LSPD Dienst-Rechner - 1:1 Grandkasten")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Prompter State
        self.prompter_step = 0
        self.prompter_current_template = "Miranda-Warnung (Standard)"
        self.prompter_font_size = 20
        self.prompter_autoplay_running = False
        self.prompter_autoplay_seconds = 3
        self.prompter_autoplay_countdown = 3
        self.prompter_autoplay_timer = QTimer(self)
        self.prompter_autoplay_timer.timeout.connect(self._on_autoplay_tick)
        self.attorney_timer_seconds = 300
        self.attorney_timer_running = False
        self.attorney_timer = QTimer(self)
        self.attorney_timer.timeout.connect(self._on_attorney_tick)
        self.floating_prompter = FloatingPrompterHUD(self, self.theme_data)

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
        t = self.theme_data

        p = self.palette()
        p.setColor(QPalette.Window, QColor(t['bg']))
        p.setColor(QPalette.Base, QColor(t['bg']))
        p.setColor(QPalette.AlternateBase, QColor(t['surface']))
        p.setColor(QPalette.Light, QColor(t['surface']))
        p.setColor(QPalette.Midlight, QColor(t['surface']))
        p.setColor(QPalette.Dark, QColor(t['bg']))
        p.setColor(QPalette.Shadow, QColor(t['bg']))
        p.setColor(QPalette.Button, QColor(t['card_bg']))
        self.setPalette(p)

        self.setStyleSheet(f"""
            QWidget {{
                color: {t['text']};
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }}
            QTabWidget::pane {{
                border: 1px solid {t['border_subtle']};
                background-color: {t['surface']};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background-color: {t['card_bg']};
                color: {t['text_muted']};
                border: 1px solid {t['border_subtle']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 9px 24px;
                font-size: 13px;
                font-weight: bold;
                margin-right: 5px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['accent']};
                color: {t['accent_text']};
                font-weight: 900;
                border-color: {t['accent']};
            }}
            QLineEdit {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border_subtle']};
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {t['accent']};
                background-color: {t['card_hover']};
            }}
            QComboBox {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border_subtle']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border: 1px solid {t['accent']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['card_bg']};
                color: {t['text']};
                selection-background-color: {t['accent']};
                selection-color: {t['accent_text']};
                border: 1px solid {t['border_subtle']};
            }}
            QScrollArea, QAbstractScrollArea {{
                background: transparent;
                background-color: transparent;
                border: none;
            }}
            QScrollArea > QWidget, QScrollArea > QWidget > QWidget, QScrollArea::viewport {{
                background: transparent;
                background-color: transparent;
                border: none;
            }}
            QScrollBar:horizontal {{
                height: 0px;
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 7px;
                margin: 0px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border_subtle']};
                min-height: 25px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                height: 0px;
                background: transparent;
                border: none;
            }}
            QCheckBox {{
                color: {t['text']};
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {t['border_subtle']};
                border-radius: 4px;
                background-color: {t['card_bg']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {t['accent']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {t['accent']};
                border-color: {t['accent']};
            }}
        """)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("mainFrame")
        self.main_frame.setStyleSheet(f"""
            QFrame#mainFrame {{
                background-color: {t['bg']};
                border: 2px solid {t['border']};
                border-radius: 12px;
            }}
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)

        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(18, 14, 18, 16)
        frame_layout.setSpacing(10)

        # Header Bar with Live Theme Selector
        header = QHBoxLayout()
        self.title_lbl = QLabel(f"🛡️ <span style='font-size: 16px; font-weight: 900; color: {t['text']};'>GRANDKASTEN</span> <span style='color: {t['accent']}; font-size: 13px; font-weight: bold;'>DIENST-RECHNER</span> <span style='color: {t['text_muted']}; font-size: 11px;'>| Bußgeld, Wanteds & TOW</span>")
        header.addWidget(self.title_lbl)
        header.addStretch()

        # Theme selector dropdown directly in header
        lbl_theme = QLabel("🎨 <span style='font-size:11px; color:#94a3b8;'>HUD-Design:</span>")
        header.addWidget(lbl_theme)

        self.combo_header_theme = QComboBox()
        self.combo_header_theme.setFixedWidth(190)
        self.combo_header_theme.addItems(list(CALC_THEMES.keys()))
        if self.current_theme_name in CALC_THEMES:
            self.combo_header_theme.setCurrentText(self.current_theme_name)
        self.combo_header_theme.currentTextChanged.connect(self.on_theme_changed_from_ui)
        header.addWidget(self.combo_header_theme)

        help_lbl = QLabel("<span style='color: #94a3b8; font-size: 11px; margin-left: 6px;'><b>[F12]</b> Schließen</span>")
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
        self.tab_bussgeld.setStyleSheet("background: transparent; border: none;")
        self.tab_tow = QWidget()
        self.tab_tow.setStyleSheet("background: transparent; border: none;")
        self.tab_prompter = QWidget()
        self.tab_prompter.setStyleSheet("background: transparent; border: none;")
        self.tabs.addTab(self.tab_bussgeld, "⚖️ Bußgeld- & Wanteds-Rechner")
        self.tabs.addTab(self.tab_tow, "🚙 TOW Rechner")
        self.tabs.addTab(self.tab_prompter, "📜 Teleprompter & Rechte")

        self.setup_bussgeld_tab()
        self.setup_tow_tab()
        self.setup_prompter_tab()

    # --- TAB 1: BUßGELD & WANTEDS RECHNER ---
    def setup_bussgeld_tab(self):
        t = self.theme_data
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
        btn_clear_search.setStyleSheet(f"""
            QPushButton {{
                background: {t['card_bg']};
                border: 1px solid {t['border_subtle']};
                color: {t['text_muted']};
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {t['card_hover']};
                color: #ffffff;
            }}
        """)
        btn_clear_search.clicked.connect(lambda: self.search_input.clear())
        search_lay.addWidget(btn_clear_search)
        left_box.addLayout(search_lay)

        # Category Filter Pills
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(44)
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setFrameShape(QFrame.NoFrame)
        self.cat_scroll.setFrameShadow(QFrame.Plain)
        self.cat_scroll.setLineWidth(0)
        self.cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_scroll.setStyleSheet("background: transparent; border: none;")
        self.cat_scroll.viewport().setStyleSheet("background: transparent; border: none;")

        self.cat_widget = QWidget()
        self.cat_widget.setStyleSheet("background: transparent; border: none;")
        self.cat_lay = QHBoxLayout(self.cat_widget)
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
        self.cat_scroll.setWidget(self.cat_widget)
        left_box.addWidget(self.cat_scroll)

        # Offenses scroll area (3-Column Grandkasten Grid)
        self.offenses_scroll = QScrollArea()
        self.offenses_scroll.setWidgetResizable(True)
        self.offenses_scroll.setFrameShape(QFrame.NoFrame)
        self.offenses_scroll.setFrameShadow(QFrame.Plain)
        self.offenses_scroll.setLineWidth(0)
        self.offenses_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.offenses_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.offenses_scroll.setStyleSheet("background: transparent; border: none;")
        self.offenses_scroll.viewport().setStyleSheet("background: transparent; border: none;")
        self.offenses_container = QWidget()
        self.offenses_container.setStyleSheet("background: transparent; border: none;")
        self.offenses_grid = QGridLayout(self.offenses_container)
        self.offenses_grid.setContentsMargins(0, 0, 8, 0)
        self.offenses_grid.setSpacing(10)
        self.offenses_scroll.setWidget(self.offenses_container)
        left_box.addWidget(self.offenses_scroll)

        layout.addLayout(left_box, stretch=60)

        # RIGHT SIDE: Grandkasten Live Dashboard & Aktenvermerk (40%)
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        # Glass Box 1: Gesamtstrafe & Big Star Rating
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {t['surface']};
                border: 1px solid {t['border_subtle']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        top_lay = QVBoxLayout(self.top_frame)
        top_lay.setSpacing(6)

        lbl_strafe_title = QLabel("GESAMTSTRAFE (HÖCHSTSTRAFE)")
        lbl_strafe_title.setAlignment(Qt.AlignCenter)
        lbl_strafe_title.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
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

        right_box.addWidget(self.top_frame)

        # Glass Box 2: Optionen für den Aktenvermerk
        self.opts_frame = QFrame()
        self.opts_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {t['surface']};
                border: 1px solid {t['border_subtle']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        opts_lay = QVBoxLayout(self.opts_frame)
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
        lbl_sys.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px; font-weight: bold;")
        grid_lay.addWidget(lbl_sys, 0, 0)

        self.input_system_wanteds = QLineEdit()
        self.input_system_wanteds.setPlaceholderText("0")
        self.input_system_wanteds.textChanged.connect(self.recalculate)
        grid_lay.addWidget(self.input_system_wanteds, 1, 0)

        lbl_orga = QLabel("ABTRANSPORT DURCH:")
        lbl_orga.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px; font-weight: bold;")
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

        right_box.addWidget(self.opts_frame)

        # Glass Box 3: Aktenvermerk Terminal & Copy Button
        self.akte_frame = QFrame()
        self.akte_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {t['surface']};
                border: 1px solid {t['border_subtle']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        akte_lay = QVBoxLayout(self.akte_frame)
        akte_lay.setSpacing(8)

        lbl_akte_title = QLabel("AKTENVERMERK")
        lbl_akte_title.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        akte_lay.addWidget(lbl_akte_title)

        # Terminal Aktenvermerk (Monospace with Matrix Green Text)
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
                border-color: #4ade80;
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

        right_box.addWidget(self.akte_frame)
        right_box.addStretch()

        layout.addLayout(right_box, stretch=40)

        # Build cards once with unique keys
        self.build_offenses_list()

    def style_cat_btn(self, btn, is_active):
        t = self.theme_data
        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['accent']};
                    color: {t['accent_text']};
                    font-weight: bold;
                    border: 1px solid {t['accent']};
                    border-radius: 14px;
                    padding: 5px 14px;
                    font-size: 11px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['card_bg']};
                    color: {t['text_muted']};
                    font-weight: normal;
                    border: 1px solid {t['border_subtle']};
                    border-radius: 14px;
                    padding: 5px 14px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {t['card_hover']};
                    color: #ffffff;
                    border-color: {t['accent']};
                }}
            """)

    def build_offenses_list(self):
        self.cards_by_key = {}
        self.all_card_items = []
        for cat, items in self.db.items():
            for item in items:
                key = make_item_key(item)
                card = OffenseCard(item, self)
                self.cards_by_key[key] = card
                self.all_card_items.append((cat, item, card))

        self.lbl_no_results = QLabel("🔍 Keine passenden Straftatbestände gefunden.")
        self.lbl_no_results.setAlignment(Qt.AlignCenter)
        self.lbl_no_results.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold; padding: 30px;")
        self.lbl_no_results.setVisible(False)

        self.filter_offenses()

    def filter_offenses(self):
        raw_q = self.search_term.strip()
        q_norm = normalize_search_text(raw_q)
        q_words = q_norm.split() if q_norm else []

        cur_cat = self.current_category.lower()
        is_searching = bool(q_words)

        matched_cards = []

        for cat, item, card in self.all_card_items:
            cat_lower = cat.lower()

            cat_matches = True
            # When actively searching, search GLOBALLY across all categories so nothing gets hidden!
            if not is_searching and self.current_category != "Alle":
                if "integrität" in cur_cat:
                    cat_matches = "integrität" in cat_lower
                elif "wirtschaft" in cur_cat:
                    cat_matches = "wirtschaft" in cat_lower
                elif "beamte" in cur_cat:
                    cat_matches = "beamten" in cat_lower
                else:
                    cat_matches = cur_cat in cat_lower

            if not cat_matches:
                card.setVisible(False)
                continue

            if is_searching:
                haystack = normalize_search_text(f"{card.item_id} {card.name} {card.info} {cat}")
                # Match if all typed words are found anywhere in ID, Name, Info or Category
                match = all(w in haystack for w in q_words)
                if match:
                    card.setVisible(True)
                    matched_cards.append(card)
                else:
                    card.setVisible(False)
            else:
                card.setVisible(True)
                matched_cards.append(card)

        # Clear existing items from grid
        while self.offenses_grid.count():
            self.offenses_grid.takeAt(0)

        # Repopulate matched cards in 3 columns (Grandkasten layout)
        for idx, card in enumerate(matched_cards):
            r = idx // 3
            c = idx % 3
            self.offenses_grid.addWidget(card, r, c)

        if hasattr(self, 'lbl_no_results'):
            if is_searching and len(matched_cards) == 0:
                self.lbl_no_results.setText(f"🔍 Keine Straftaten für \"{raw_q}\" gefunden.\nÜberprüfe Stichwort oder Paragraph.")
                self.offenses_grid.addWidget(self.lbl_no_results, 0, 0, 1, 3)
                self.lbl_no_results.setVisible(True)
            else:
                self.lbl_no_results.setVisible(False)

        # Push items neatly to top if fewer items
        if matched_cards:
            self.offenses_grid.setRowStretch((len(matched_cards) - 1) // 3 + 1, 1)

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

    # --- TAB 2: TOW RECHNER (1:1 Grandkasten StVO §8 Geschwindigkeitsrechner) ---
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

        # Row 4: Berechnen Button
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

        # Row 5: Results Frame
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

        # Row 6: Kopieren & Reset Buttons
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

        # 1:1 StVO §8 Geschwindigkeitsüberschreitung (4 Stufen)
        if diff < 10:
            offense = "Keine Ordnungswidrigkeit"
            fine = 0
            paragraph = "-"
        elif diff <= 40:
            paragraph = "StVO §8"
            fine = 5000
            offense = "StVO §8 - Geschwindigkeitsüberschreitung 10 - 40 km/h"
        elif diff <= 60:
            paragraph = "StVO §8"
            fine = 10000
            offense = "StVO §8 - Geschwindigkeitsüberschreitung 41 - 60 km/h • Abschleppberechtigt"
        elif diff <= 100:
            paragraph = "StVO §8"
            fine = 15000
            offense = "StVO §8 - Geschwindigkeitsüberschreitung 61 - 100 km/h • Abschleppberechtigt"
        else:
            paragraph = "StVO §8"
            fine = 20000
            offense = "StVO §8 - Geschwindigkeitsüberschreitung ab 101 km/h • Abschleppberechtigt"

        # Wiederholungstäter StVO §25 lit. 2: Verdopplung Bußgeld
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

    # --- TAB 3: TELEPROMPTER & RECHTE ---
    def setup_prompter_tab(self):
        t = self.theme_data
        layout = QHBoxLayout(self.tab_prompter)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # LEFT COLUMN (320px): Vorlagen & Einstellungen & Anwalts-Timer
        left_box = QVBoxLayout()
        left_box.setSpacing(12)

        # Frame 1: Vorlagen & Mini-HUD
        self.p_box_templates = QFrame()
        self.p_box_templates.setStyleSheet(f"background-color: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 10px; padding: 12px;")
        f1_lay = QVBoxLayout(self.p_box_templates)
        f1_lay.setSpacing(10)

        lbl_tpl_title = QLabel("BELEHRUNGS-VORLAGEN")
        lbl_tpl_title.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px;")
        f1_lay.addWidget(lbl_tpl_title)

        self.combo_prompter_tpl = QComboBox()
        for name in PROMPTER_TEMPLATES.keys():
            self.combo_prompter_tpl.addItem(name)
        self.combo_prompter_tpl.currentTextChanged.connect(self.prompter_on_template_change)
        f1_lay.addWidget(self.combo_prompter_tpl)

        self.btn_open_floating = QPushButton("📌 Schwebendes Mini-HUD öffnen (F10)")
        self.btn_open_floating.setCursor(Qt.PointingHandCursor)
        self.btn_open_floating.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']};
                color: {t['accent']};
                border: 1px solid {t['accent']};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {t['card_hover']};
            }}
        """)
        self.btn_open_floating.clicked.connect(self.toggle_floating_prompter)
        f1_lay.addWidget(self.btn_open_floating)

        # Font-Size Slider
        lbl_font = QLabel("Schriftgröße (Prompter):")
        lbl_font.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px;")
        f1_lay.addWidget(lbl_font)

        font_row = QHBoxLayout()
        self.slider_font = QSlider(Qt.Horizontal)
        self.slider_font.setRange(14, 30)
        self.slider_font.setValue(self.prompter_font_size)
        self.lbl_font_val = QLabel(f"{self.prompter_font_size}px")
        self.lbl_font_val.setFixedWidth(35)
        self.slider_font.valueChanged.connect(self.prompter_on_font_slider)
        font_row.addWidget(self.slider_font)
        font_row.addWidget(self.lbl_font_val)
        f1_lay.addLayout(font_row)

        left_box.addWidget(self.p_box_templates)

        # Frame 2: Anwalts-Timer (5-Minuten Frist)
        self.p_box_timer = QFrame()
        self.p_box_timer.setStyleSheet(f"background-color: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 10px; padding: 12px;")
        f2_lay = QVBoxLayout(self.p_box_timer)
        f2_lay.setSpacing(8)

        lbl_timer_title = QLabel("⚖️ ANWALTS-WARTEFRIST (5 MIN.)")
        lbl_timer_title.setAlignment(Qt.AlignCenter)
        lbl_timer_title.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px;")
        f2_lay.addWidget(lbl_timer_title)

        self.lbl_attorney_time = QLabel("05:00")
        self.lbl_attorney_time.setAlignment(Qt.AlignCenter)
        self.lbl_attorney_time.setStyleSheet("font-size: 30px; font-weight: 900; color: #38bdf8; font-family: monospace; padding: 4px 0;")
        f2_lay.addWidget(self.lbl_attorney_time)

        self.progress_attorney = QProgressBar()
        self.progress_attorney.setRange(0, 300)
        self.progress_attorney.setValue(300)
        self.progress_attorney.setTextVisible(False)
        self.progress_attorney.setFixedHeight(6)
        self.progress_attorney.setStyleSheet("""
            QProgressBar {
                background: #181822;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background: #38bdf8;
                border-radius: 3px;
            }
        """)
        f2_lay.addWidget(self.progress_attorney)

        timer_btns = QHBoxLayout()
        self.btn_timer_toggle = QPushButton("▶ Timer Starten")
        self.btn_timer_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_timer_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: bold;
                border-radius: 6px;
                padding: 7px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_timer_toggle.clicked.connect(self.toggle_attorney_timer)
        timer_btns.addWidget(self.btn_timer_toggle, stretch=2)

        self.btn_timer_reset = QPushButton("↺ Reset")
        self.btn_timer_reset.setCursor(Qt.PointingHandCursor)
        self.btn_timer_reset.setStyleSheet(f"background: {t['card_bg']}; color: {t['text_muted']}; border: 1px solid {t['border_subtle']}; border-radius: 6px; padding: 7px; font-size: 12px;")
        self.btn_timer_reset.clicked.connect(self.reset_attorney_timer)
        timer_btns.addWidget(self.btn_timer_reset, stretch=1)
        f2_lay.addLayout(timer_btns)

        # Quick Vermerk Buttons
        lbl_vermerk_title = QLabel("<span style='color: #94a3b8; font-size: 10px; font-weight: bold;'>MDT-AKTENVERMERK BEI FRIST:</span>")
        f2_lay.addWidget(lbl_vermerk_title)

        self.btn_vermerk_expired = QPushButton("📋 Vermerk: Anwalt nicht erschienen")
        self.btn_vermerk_expired.setCursor(Qt.PointingHandCursor)
        self.btn_vermerk_expired.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']};
                color: #fb923c;
                border: 1px solid #7c2d12;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {t['card_hover']};
            }}
        """)
        self.btn_vermerk_expired.clicked.connect(lambda: self.copy_attorney_vermerk("expired"))
        f2_lay.addWidget(self.btn_vermerk_expired)

        self.btn_vermerk_arrived = QPushButton("📋 Vermerk: Anwalt eingetroffen")
        self.btn_vermerk_arrived.setCursor(Qt.PointingHandCursor)
        self.btn_vermerk_arrived.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']};
                color: #4ade80;
                border: 1px solid #14532d;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {t['card_hover']};
            }}
        """)
        self.btn_vermerk_arrived.clicked.connect(lambda: self.copy_attorney_vermerk("arrived"))
        f2_lay.addWidget(self.btn_vermerk_arrived)

        left_box.addWidget(self.p_box_timer)
        left_box.addStretch()
        layout.addLayout(left_box, stretch=35)

        # RIGHT COLUMN: Prompter Stage
        right_box = QVBoxLayout()
        right_box.setSpacing(10)

        # Stage Header
        stage_head = QHBoxLayout()
        self.lbl_stage_title = QLabel("🛡️ Miranda-Warnung (Standard)")
        self.lbl_stage_title.setStyleSheet(f"font-size: 16px; font-weight: 900; color: {t['accent']};")
        stage_head.addWidget(self.lbl_stage_title)
        stage_head.addStretch()

        self.lbl_step_progress = QLabel("Satz 1 von 5")
        self.lbl_step_progress.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {t['text_muted']}; background: {t['card_bg']}; border: 1px solid {t['border_subtle']}; border-radius: 4px; padding: 4px 10px;")
        stage_head.addWidget(self.lbl_step_progress)

        btn_reset_prompter = QPushButton("🔄 Von vorn")
        btn_reset_prompter.setCursor(Qt.PointingHandCursor)
        btn_reset_prompter.setStyleSheet(f"background: {t['card_bg']}; color: {t['text_muted']}; border: 1px solid {t['border_subtle']}; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        btn_reset_prompter.clicked.connect(self.prompter_reset)
        stage_head.addWidget(btn_reset_prompter)
        right_box.addLayout(stage_head)

        # Scroll area for sentence list
        self.prompter_scroll = QScrollArea()
        self.prompter_scroll.setWidgetResizable(True)
        self.prompter_scroll.setFrameShape(QFrame.NoFrame)
        self.prompter_scroll.setFrameShadow(QFrame.Plain)
        self.prompter_scroll.setLineWidth(0)
        self.prompter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.prompter_scroll.setStyleSheet("background: transparent; border: none;")
        self.prompter_scroll.viewport().setStyleSheet("background: transparent; border: none;")

        self.prompter_container = QWidget()
        self.prompter_container.setStyleSheet("background: transparent; border: none;")
        self.prompter_layout = QVBoxLayout(self.prompter_container)
        self.prompter_layout.setContentsMargins(4, 4, 10, 4)
        self.prompter_layout.setSpacing(10)

        self.prompter_scroll.setWidget(self.prompter_container)
        right_box.addWidget(self.prompter_scroll, stretch=1)

        # Stage Action Bar
        act_bar = QHBoxLayout()
        act_bar.setSpacing(10)

        self.btn_p_prev = QPushButton("⏮ Vorheriger")
        self.btn_p_prev.setCursor(Qt.PointingHandCursor)
        self.btn_p_prev.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border_subtle']};
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {t['card_hover']};
            }}
        """)
        self.btn_p_prev.clicked.connect(self.prompter_prev)
        act_bar.addWidget(self.btn_p_prev)

        self.btn_p_copy_cur = QPushButton("📋 Satz kopieren (Chat)")
        self.btn_p_copy_cur.setCursor(Qt.PointingHandCursor)
        self.btn_p_copy_cur.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)
        self.btn_p_copy_cur.clicked.connect(self.prompter_copy_current)
        act_bar.addWidget(self.btn_p_copy_cur)

        self.btn_p_copy_all = QPushButton("📋 Alles kopieren")
        self.btn_p_copy_all.setCursor(Qt.PointingHandCursor)
        self.btn_p_copy_all.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['card_bg']};
                color: {t['text_muted']};
                border: 1px solid {t['border_subtle']};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['card_hover']};
                color: #ffffff;
            }}
        """)
        self.btn_p_copy_all.clicked.connect(self.prompter_copy_all)
        act_bar.addWidget(self.btn_p_copy_all)

        self.btn_p_auto = QPushButton("▶ Auto-Play (3s)")
        self.btn_p_auto.setCursor(Qt.PointingHandCursor)
        self.btn_p_auto.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        self.btn_p_auto.clicked.connect(self.toggle_autoplay)
        act_bar.addWidget(self.btn_p_auto)

        self.btn_p_next = QPushButton("⏭ Weiter (Leertaste / Enter)")
        self.btn_p_next.setCursor(Qt.PointingHandCursor)
        self.btn_p_next.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['accent']};
                color: {t['accent_text']};
                border: none;
                border-radius: 6px;
                padding: 10px 22px;
                font-weight: 900;
                font-size: 13px;
            }}
            QPushButton:hover {{
                filter: brightness(1.15);
            }}
        """)
        self.btn_p_next.clicked.connect(self.prompter_next)
        act_bar.addWidget(self.btn_p_next, stretch=1)

        right_box.addLayout(act_bar)
        layout.addLayout(right_box, stretch=65)

        self.render_prompter_sentences()

    def render_prompter_sentences(self):
        while self.prompter_layout.count():
            item = self.prompter_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        sentences = PROMPTER_TEMPLATES.get(self.prompter_current_template, [])
        total = len(sentences)
        t = self.theme_data

        if hasattr(self, 'lbl_stage_title'):
            self.lbl_stage_title.setText(f"🛡️ {self.prompter_current_template}")
        if hasattr(self, 'lbl_step_progress'):
            self.lbl_step_progress.setText(f"Satz {self.prompter_step + 1} von {max(1, total)}")

        if hasattr(self, 'floating_prompter') and sentences:
            cur_s = sentences[min(self.prompter_step, total - 1)]
            self.floating_prompter.lbl_sentence.setText(cur_s)
            self.floating_prompter.lbl_hud_step.setText(f"[{self.prompter_step + 1}/{total}]")
            if self.floating_prompter.combo_hud_template.currentText() != self.prompter_current_template:
                self.floating_prompter.combo_hud_template.blockSignals(True)
                self.floating_prompter.combo_hud_template.setCurrentText(self.prompter_current_template)
                self.floating_prompter.combo_hud_template.blockSignals(False)

        for idx, sentence in enumerate(sentences):
            card = QFrame()
            is_active = (idx == self.prompter_step)
            is_past = (idx < self.prompter_step)

            if is_active:
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {t['card_active_bg']};
                        border: 2px solid {t['accent']};
                        border-radius: 10px;
                        padding: 12px 16px;
                    }}
                """)
            elif is_past:
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {t['surface']};
                        border: 1px solid {t['border_subtle']};
                        border-radius: 8px;
                        padding: 10px 14px;
                    }}
                """)
            else:
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {t['card_bg']};
                        border: 1px solid {t['border_subtle']};
                        border-radius: 8px;
                        padding: 10px 14px;
                    }}
                """)

            c_lay = QHBoxLayout(card)
            c_lay.setContentsMargins(6, 4, 6, 4)
            c_lay.setSpacing(12)

            if is_past:
                lbl_icon = QLabel("✓")
                lbl_icon.setStyleSheet("color: #4ade80; font-size: 15px; font-weight: 900;")
            elif is_active:
                lbl_icon = QLabel("▶")
                lbl_icon.setStyleSheet(f"color: {t['accent']}; font-size: 16px; font-weight: 900;")
            else:
                lbl_icon = QLabel(f"{idx + 1}.")
                lbl_icon.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
            lbl_icon.setFixedWidth(24)
            c_lay.addWidget(lbl_icon)

            lbl_text = QLabel(sentence)
            lbl_text.setWordWrap(True)
            if is_active:
                lbl_text.setStyleSheet(f"color: {t['text']}; font-size: {self.prompter_font_size}px; font-weight: bold; line-height: 1.35;")
            elif is_past:
                lbl_text.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
            else:
                lbl_text.setStyleSheet("color: #475569; font-size: 13px; font-weight: 500;")
            c_lay.addWidget(lbl_text, stretch=1)

            def make_click_handler(target_idx):
                def handler(event):
                    self.prompter_step = target_idx
                    self.render_prompter_sentences()
                return handler

            card.mousePressEvent = make_click_handler(idx)
            card.setCursor(Qt.PointingHandCursor)
            self.prompter_layout.addWidget(card)

        self.prompter_layout.addStretch()

    def prompter_next(self):
        sentences = PROMPTER_TEMPLATES.get(self.prompter_current_template, [])
        if self.prompter_step < len(sentences) - 1:
            self.prompter_step += 1
            self.render_prompter_sentences()
            if self.prompter_autoplay_running:
                self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
                self._update_autoplay_buttons()
        else:
            if self.prompter_autoplay_running:
                self.stop_autoplay()
                self.prompter_step = 0
                self.render_prompter_sentences()
                if hasattr(self, 'floating_prompter') and self.floating_prompter.isVisible():
                    self.floating_prompter.hide()

    def prompter_prev(self):
        if self.prompter_step > 0:
            self.prompter_step -= 1
            self.render_prompter_sentences()
            if self.prompter_autoplay_running:
                self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
                self._update_autoplay_buttons()

    def prompter_reset(self):
        self.prompter_step = 0
        self.render_prompter_sentences()
        if self.prompter_autoplay_running:
            self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
            self._update_autoplay_buttons()

    def prompter_copy_current(self):
        sentences = PROMPTER_TEMPLATES.get(self.prompter_current_template, [])
        if sentences and 0 <= self.prompter_step < len(sentences):
            text = sentences[self.prompter_step]
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            if hasattr(self, 'btn_p_copy_cur'):
                self.btn_p_copy_cur.setText("✅ Kopiert!")
                QTimer.singleShot(1200, lambda: self.btn_p_copy_cur.setText("📋 Satz kopieren (Chat)"))
            if hasattr(self, 'floating_prompter') and hasattr(self.floating_prompter, 'btn_copy'):
                self.floating_prompter.btn_copy.setText("✅ Kopiert!")
                QTimer.singleShot(1200, lambda: self.floating_prompter.btn_copy.setText("📋 Kopieren"))

    def prompter_copy_all(self):
        sentences = PROMPTER_TEMPLATES.get(self.prompter_current_template, [])
        if sentences:
            text = " ".join(sentences)
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            if hasattr(self, 'btn_p_copy_all'):
                self.btn_p_copy_all.setText("✅ Alles kopiert!")
                QTimer.singleShot(1200, lambda: self.btn_p_copy_all.setText("📋 Alles kopieren"))

    def prompter_on_template_change(self, name):
        if name in PROMPTER_TEMPLATES:
            self.prompter_current_template = name
            self.prompter_step = 0
            if hasattr(self, 'combo_prompter_tpl') and self.combo_prompter_tpl.currentText() != name:
                self.combo_prompter_tpl.blockSignals(True)
                self.combo_prompter_tpl.setCurrentText(name)
                self.combo_prompter_tpl.blockSignals(False)
            if hasattr(self, 'floating_prompter') and hasattr(self.floating_prompter, 'combo_hud_template'):
                if self.floating_prompter.combo_hud_template.currentText() != name:
                    self.floating_prompter.combo_hud_template.blockSignals(True)
                    self.floating_prompter.combo_hud_template.setCurrentText(name)
                    self.floating_prompter.combo_hud_template.blockSignals(False)
            if self.prompter_autoplay_running:
                self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
            self.render_prompter_sentences()

    def prompter_on_font_slider(self, val):
        self.prompter_font_size = val
        if hasattr(self, 'lbl_font_val'):
            self.lbl_font_val.setText(f"{val}px")
        self.render_prompter_sentences()

    def toggle_floating_prompter(self):
        if hasattr(self, 'floating_prompter'):
            if self.floating_prompter.isVisible():
                self.floating_prompter.hide()
                self.stop_autoplay()
            else:
                self.prompter_step = 0
                self.render_prompter_sentences()
                screen = QApplication.primaryScreen().geometry()
                w = self.floating_prompter.width()
                x = (screen.width() - w) // 2
                y = 50
                self.floating_prompter.move(x, y)
                self.floating_prompter.show()
                self.floating_prompter.raise_()
                self.floating_prompter.activateWindow()
                self.start_autoplay()

    def toggle_autoplay(self):
        if self.prompter_autoplay_running:
            self.stop_autoplay()
        else:
            self.start_autoplay()

    def start_autoplay(self):
        self.prompter_autoplay_running = True
        self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
        self.prompter_autoplay_timer.start(1000)
        self._update_autoplay_buttons()

    def stop_autoplay(self):
        self.prompter_autoplay_running = False
        self.prompter_autoplay_timer.stop()
        self._update_autoplay_buttons()

    def _update_autoplay_buttons(self):
        if hasattr(self, 'btn_p_auto'):
            if self.prompter_autoplay_running:
                self.btn_p_auto.setText(f"⏸ Auto-Play ({self.prompter_autoplay_countdown}s)")
                self.btn_p_auto.setStyleSheet("background-color: #eab308; color: #000000; border: none; border-radius: 6px; padding: 10px 18px; font-weight: 900; font-size: 13px;")
            else:
                self.btn_p_auto.setText("▶ Auto-Play (3s)")
                self.btn_p_auto.setStyleSheet("background-color: #059669; color: #ffffff; border: none; border-radius: 6px; padding: 10px 18px; font-weight: bold; font-size: 13px;")

        if hasattr(self, 'floating_prompter') and hasattr(self.floating_prompter, 'btn_auto'):
            if self.prompter_autoplay_running:
                self.floating_prompter.btn_auto.setText(f"⏸ {self.prompter_autoplay_countdown}s")
                self.floating_prompter.btn_auto.setStyleSheet("background: #eab308; color: #000000; border: none; border-radius: 5px; padding: 4px 9px; font-size: 11px; font-weight: 900;")
            else:
                self.floating_prompter.btn_auto.setText("▶ Auto (3s)")
                self.floating_prompter.btn_auto.setStyleSheet("background: #059669; color: #ffffff; border: none; border-radius: 5px; padding: 4px 9px; font-size: 11px; font-weight: bold;")

    def _on_autoplay_tick(self):
        if not self.prompter_autoplay_running:
            return
        self.prompter_autoplay_countdown -= 1
        if self.prompter_autoplay_countdown <= 0:
            sentences = PROMPTER_TEMPLATES.get(self.prompter_current_template, [])
            if self.prompter_step < len(sentences) - 1:
                self.prompter_next()
                self.prompter_autoplay_countdown = self.prompter_autoplay_seconds
            else:
                # Finished first complete run! Close HUD automatically.
                self.stop_autoplay()
                self.prompter_step = 0
                self.render_prompter_sentences()
                if hasattr(self, 'floating_prompter') and self.floating_prompter.isVisible():
                    self.floating_prompter.hide()
                return
        self._update_autoplay_buttons()

    def toggle_attorney_timer(self):
        if self.attorney_timer_running:
            self.attorney_timer.stop()
            self.attorney_timer_running = False
            self.btn_timer_toggle.setText("▶ Timer Fortsetzen")
            self.btn_timer_toggle.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 7px; font-size: 12px; border: none;")
        else:
            self.attorney_timer.start(1000)
            self.attorney_timer_running = True
            self.btn_timer_toggle.setText("⏸ Pause")
            self.btn_timer_toggle.setStyleSheet("background-color: #eab308; color: #000000; font-weight: bold; border-radius: 6px; padding: 7px; font-size: 12px; border: none;")

    def reset_attorney_timer(self):
        self.attorney_timer.stop()
        self.attorney_timer_running = False
        self.attorney_timer_seconds = 300
        self.btn_timer_toggle.setText("▶ Timer Starten")
        self.btn_timer_toggle.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 7px; font-size: 12px; border: none;")
        self.lbl_attorney_time.setText("05:00")
        self.lbl_attorney_time.setStyleSheet("font-size: 30px; font-weight: 900; color: #38bdf8; font-family: monospace; padding: 4px 0;")
        self.progress_attorney.setValue(300)
        if hasattr(self, 'floating_prompter'):
            self.floating_prompter.lbl_hud_timer.setText("⏱️ 05:00")
            self.floating_prompter.lbl_hud_timer.setStyleSheet(f"background: {self.theme_data['card_bg']}; color: #38bdf8; border: 1px solid {self.theme_data['border_subtle']}; border-radius: 5px; padding: 5px 8px; font-size: 11px; font-weight: bold;")

    def _on_attorney_tick(self):
        if self.attorney_timer_seconds > 0:
            self.attorney_timer_seconds -= 1
            mins = self.attorney_timer_seconds // 60
            secs = self.attorney_timer_seconds % 60
            time_str = f"{mins:02d}:{secs:02d}"
            self.lbl_attorney_time.setText(time_str)
            self.progress_attorney.setValue(self.attorney_timer_seconds)
            if hasattr(self, 'floating_prompter'):
                self.floating_prompter.lbl_hud_timer.setText(f"⏱️ {time_str}")

            if self.attorney_timer_seconds == 0:
                self.attorney_timer.stop()
                self.attorney_timer_running = False
                self.lbl_attorney_time.setText("00:00 (Frist um!)")
                self.lbl_attorney_time.setStyleSheet("font-size: 24px; font-weight: 900; color: #ef4444; font-family: monospace; padding: 4px 0;")
                if hasattr(self, 'floating_prompter'):
                    self.floating_prompter.lbl_hud_timer.setText("⚠️ 00:00!")
                    self.floating_prompter.lbl_hud_timer.setStyleSheet("background: #450a0a; color: #f87171; border: 1px solid #ef4444; border-radius: 5px; padding: 5px 8px; font-size: 11px; font-weight: bold;")
                try:
                    import winsound
                    winsound.Beep(1200, 250)
                    winsound.Beep(1600, 350)
                except Exception:
                    pass

    def copy_attorney_vermerk(self, mode):
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m %H:%M")
        if mode == "expired":
            txt = f"{date_str} - Anwalt verlangt, 5-Minuten-Wartefrist ergebnislos verstrichen"
        else:
            txt = f"{date_str} - Anwalt vor Ort erschienen - Akteneinsicht gewährt"

        clipboard = QApplication.clipboard()
        clipboard.setText(txt)
        if mode == "expired" and hasattr(self, 'btn_vermerk_expired'):
            orig = self.btn_vermerk_expired.text()
            self.btn_vermerk_expired.setText("✅ Vermerk kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_vermerk_expired.setText(orig))
        elif mode == "arrived" and hasattr(self, 'btn_vermerk_arrived'):
            orig = self.btn_vermerk_arrived.text()
            self.btn_vermerk_arrived.setText("✅ Vermerk kopiert!")
            QTimer.singleShot(1500, lambda: self.btn_vermerk_arrived.setText(orig))

    # --- THEME SWITCHING (LIVE) ---
    def on_theme_changed_from_ui(self, theme_name):
        self.update_theme(theme_name)
        try:
            from pd_logger_overlay import CONFIG, save_config
            CONFIG["calc_theme"] = theme_name
            save_config(CONFIG)
        except Exception:
            pass

    def update_theme(self, theme_name_or_data):
        if isinstance(theme_name_or_data, str):
            if theme_name_or_data in CALC_THEMES:
                self.current_theme_name = theme_name_or_data
                self.theme_data = CALC_THEMES[theme_name_or_data]
            else:
                return
        elif isinstance(theme_name_or_data, dict):
            self.theme_data = theme_name_or_data
            self.current_theme_name = "Benutzerdefiniert"

        t = self.theme_data

        # Update Main Frame
        if hasattr(self, 'main_frame'):
            self.main_frame.setStyleSheet(f"""
                QFrame#mainFrame {{
                    background-color: {t['bg']};
                    border: 2px solid {t['border']};
                    border-radius: 12px;
                }}
            """)

        # Update Title Label
        if hasattr(self, 'title_lbl'):
            self.title_lbl.setText(f"🛡️ <span style='font-size: 16px; font-weight: 900; color: {t['text']};'>GRANDKASTEN</span> <span style='color: {t['accent']}; font-size: 13px; font-weight: bold;'>DIENST-RECHNER</span> <span style='color: {t['text_muted']}; font-size: 11px;'>| Bußgeld, Wanteds & TOW</span>")

        # Update Theme Combo without triggering signals
        if hasattr(self, 'combo_header_theme') and self.current_theme_name in CALC_THEMES:
            self.combo_header_theme.blockSignals(True)
            self.combo_header_theme.setCurrentText(self.current_theme_name)
            self.combo_header_theme.blockSignals(False)

        # Update Dashboard frames
        if hasattr(self, 'top_frame'):
            self.top_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {t['surface']};
                    border: 1px solid {t['border_subtle']};
                    border-radius: 10px;
                    padding: 12px;
                }}
            """)
        if hasattr(self, 'opts_frame'):
            self.opts_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {t['surface']};
                    border: 1px solid {t['border_subtle']};
                    border-radius: 10px;
                    padding: 12px;
                }}
            """)
        if hasattr(self, 'akte_frame'):
            self.akte_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {t['surface']};
                    border: 1px solid {t['border_subtle']};
                    border-radius: 10px;
                    padding: 12px;
                }}
            """)

        # Update category buttons
        if hasattr(self, 'cat_buttons'):
            for name, b in self.cat_buttons.items():
                self.style_cat_btn(b, name == self.current_category)

        # Update all offense cards
        if hasattr(self, 'cards_by_key'):
            for card in self.cards_by_key.values():
                card.apply_style(card.is_selected)

        # Re-enforce dark palette & transparent containers
        try:
            p = self.palette()
            p.setColor(QPalette.Window, QColor(t['bg']))
            p.setColor(QPalette.Base, QColor(t['bg']))
            p.setColor(QPalette.AlternateBase, QColor(t['surface']))
            p.setColor(QPalette.Light, QColor(t['surface']))
            p.setColor(QPalette.Midlight, QColor(t['surface']))
            p.setColor(QPalette.Dark, QColor(t['bg']))
            p.setColor(QPalette.Shadow, QColor(t['bg']))
            p.setColor(QPalette.Button, QColor(t['card_bg']))
            self.setPalette(p)
        except Exception:
            pass

        if hasattr(self, 'cat_scroll'):
            self.cat_scroll.setStyleSheet("background: transparent; border: none;")
            self.cat_scroll.viewport().setStyleSheet("background: transparent; border: none;")
            self.cat_scroll.setFrameShape(QFrame.NoFrame)
            self.cat_scroll.setFrameShadow(QFrame.Plain)
            self.cat_scroll.setLineWidth(0)
        if hasattr(self, 'cat_widget'):
            self.cat_widget.setStyleSheet("background: transparent; border: none;")
        if hasattr(self, 'offenses_scroll'):
            self.offenses_scroll.setStyleSheet("background: transparent; border: none;")
            self.offenses_scroll.viewport().setStyleSheet("background: transparent; border: none;")
            self.offenses_scroll.setFrameShape(QFrame.NoFrame)
            self.offenses_scroll.setFrameShadow(QFrame.Plain)
            self.offenses_scroll.setLineWidth(0)
        if hasattr(self, 'offenses_container'):
            self.offenses_container.setStyleSheet("background: transparent; border: none;")
        if hasattr(self, 'tab_bussgeld'):
            self.tab_bussgeld.setStyleSheet("background: transparent; border: none;")
        if hasattr(self, 'tab_tow'):
            self.tab_tow.setStyleSheet("background: transparent; border: none;")
        if hasattr(self, 'tab_prompter'):
            self.tab_prompter.setStyleSheet("background: transparent; border: none;")
        if hasattr(self, 'p_box_templates'):
            self.p_box_templates.setStyleSheet(f"background-color: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 10px; padding: 12px;")
        if hasattr(self, 'p_box_timer'):
            self.p_box_timer.setStyleSheet(f"background-color: {t['surface']}; border: 1px solid {t['border_subtle']}; border-radius: 10px; padding: 12px;")
        if hasattr(self, 'floating_prompter'):
            self.floating_prompter.update_theme(t)
        if hasattr(self, 'prompter_layout'):
            self.render_prompter_sentences()

    # --- KEY & EVENT HANDLERS ---
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Escape, Qt.Key_F12):
            self.hide()
            event.accept()
        elif hasattr(self, 'tabs') and self.tabs.currentIndex() == 2 and not self.search_input.hasFocus():
            if event.key() in (Qt.Key_Space, Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter):
                self.prompter_next()
                event.accept()
            elif event.key() in (Qt.Key_Left, Qt.Key_Backspace):
                self.prompter_prev()
                event.accept()
            else:
                super().keyPressEvent(event)
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
