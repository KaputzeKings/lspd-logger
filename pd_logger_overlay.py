import os
import sys
import time
import json
import base64
import re
import datetime
import threading
import winsound
import requests
import ctypes
from ctypes import wintypes
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QGridLayout, QLineEdit, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu,
    QProgressBar, QTextEdit, QTabWidget, QComboBox, QSlider, QColorDialog, QScrollArea,
    QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon, QPainter, QAction, QKeyEvent
from pynput import keyboard
from grand_calculator import GrandCalculatorOverlay, load_grandkasten_db

CURRENT_VERSION = "1.2.1"
DEFAULT_UPDATE_URL = "https://api.github.com/repos/KaputzeKings/lspd-logger/releases/latest"

# Base directory
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
STATE_FILE = os.path.join(BASE_DIR, "logger_state.json")
MIDNIGHT_STATE_FILE = os.path.join(BASE_DIR, "midnight_state.json")
LOG_FILE = os.path.join(BASE_DIR, "debug.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass
    print(msg)

def adjust_color(hex_color, factor):
    try:
        c = hex_color.lstrip('#')
        if len(c) == 6:
            r = min(255, max(0, int(int(c[0:2], 16) * factor)))
            g = min(255, max(0, int(int(c[2:4], 16) * factor)))
            b = min(255, max(0, int(int(c[4:6], 16) * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        pass
    return hex_color

THEMES = {
    "Schwarz-Lila (Standard)": {
        "bg": "#0f0c18",
        "card_bg": "#171324",
        "border": "#a855f7",
        "accent": "#7e22ce",
        "accent_hover": "#9333ea",
        "accent_pressed": "#581c87",
        "text": "#f5f3ff",
        "text_muted": "#a78bfa",
        "btn_bg": "#1b162b",
        "btn_hover": "#2b2046",
        "thumb_bg": "#08060d"
    },
    "LSPD Cyber Blue": {
        "bg": "#070d1e",
        "card_bg": "#0f1c3f",
        "border": "#00d2ff",
        "accent": "#0077b6",
        "accent_hover": "#0096c7",
        "accent_pressed": "#023e8a",
        "text": "#ffffff",
        "text_muted": "#90e0ef",
        "btn_bg": "#12204a",
        "btn_hover": "#1a2f6c",
        "thumb_bg": "#040814"
    },
    "Tactical Stealth Red": {
        "bg": "#0d090a",
        "card_bg": "#1c1214",
        "border": "#ef4444",
        "accent": "#b91c1c",
        "accent_hover": "#dc2626",
        "accent_pressed": "#7f1d1d",
        "text": "#ffffff",
        "text_muted": "#fca5a5",
        "btn_bg": "#221316",
        "btn_hover": "#361a1f",
        "thumb_bg": "#080405"
    },
    "Emerald Special Forces": {
        "bg": "#06130b",
        "card_bg": "#0c2717",
        "border": "#10b981",
        "accent": "#047857",
        "accent_hover": "#059669",
        "accent_pressed": "#064e3b",
        "text": "#ffffff",
        "text_muted": "#6ee7b7",
        "btn_bg": "#11261b",
        "btn_hover": "#173827",
        "thumb_bg": "#030a06"
    },
    "Pure Dark Minimal": {
        "bg": "#121212",
        "card_bg": "#1e1e1e",
        "border": "#71717a",
        "accent": "#3f3f46",
        "accent_hover": "#52525b",
        "accent_pressed": "#27272a",
        "text": "#fafafa",
        "text_muted": "#a1a1aa",
        "btn_bg": "#27272a",
        "btn_hover": "#3f3f46",
        "thumb_bg": "#09090b"
    }
}

def get_theme_colors(hud_conf=None):
    if hud_conf is None:
        hud_conf = CONFIG.get("hud", {})
    theme_name = hud_conf.get("theme", "Schwarz-Lila (Standard)")
    if theme_name in THEMES:
        return THEMES[theme_name]
    
    # Custom colors
    bg = hud_conf.get("custom_bg", "#0f0c18")
    accent = hud_conf.get("custom_accent", "#a855f7")
    text = hud_conf.get("custom_text", "#f5f3ff")
    return {
        "bg": bg,
        "card_bg": adjust_color(bg, 1.4),
        "border": accent,
        "accent": adjust_color(accent, 0.8),
        "accent_hover": accent,
        "accent_pressed": adjust_color(accent, 0.6),
        "text": text,
        "text_muted": adjust_color(text, 0.8),
        "btn_bg": adjust_color(bg, 1.6),
        "btn_hover": adjust_color(bg, 2.2),
        "thumb_bg": adjust_color(bg, 0.6)
    }

def get_default_watch_dir():
    user_home = os.path.expanduser("~")
    p1 = os.path.join(user_home, "Videos", "Medal", "Screenshots", "Grand Theft Auto V FiveM")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(user_home, "Videos", "Medal", "Screenshots")
    if os.path.exists(p2):
        return p2
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        p3 = os.path.join(user_profile, "Videos", "Medal", "Screenshots", "Grand Theft Auto V FiveM")
        if os.path.exists(p3):
            return p3
    return p1

def get_default_config():
    return {
        "user_badge": "317108",
        "forum_channel_id": "1551241898340122756",
        "thread_id": "",
        "watch_dir": get_default_watch_dir(),
        "discord_token": "",
        "update_url": "",
        "hud": {
            "theme": "Schwarz-Lila (Standard)",
            "scale": 1.0,
            "position": "Oben Rechts",
            "font_family": "Segoe UI",
            "font_size": 11,
            "opacity": 0.96,
            "auto_close_sec": 25,
            "custom_bg": "#0f0c18",
            "custom_accent": "#a855f7",
            "custom_text": "#f5f3ff"
        }
    }

def load_config():
    config = get_default_config()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config.update(loaded)
                if "hud" in loaded and isinstance(loaded["hud"], dict):
                    config["hud"] = {**get_default_config()["hud"], **loaded["hud"]}
        except Exception as e:
            log(f"[Config Load Error] {e}")
    else:
        save_config(config)
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"[Config Save Error] {e}")
        return False

CONFIG = load_config()

# Windows DPAPI Decryption for Discord Token
class DATA_BLOB(ctypes.Structure):
    _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_byte))]

def decrypt_dpapi(cipher_bytes):
    blob_in = DATA_BLOB(len(cipher_bytes), ctypes.cast(ctypes.create_string_buffer(cipher_bytes), ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        data = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return data
    return None

def get_discord_token():
    manual_token = CONFIG.get("discord_token", "").strip()
    if manual_token:
        return manual_token

    appdata = os.environ.get('APPDATA')
    if not appdata:
        return None
    local_state_path = os.path.join(appdata, 'discord', 'Local State')
    if not os.path.exists(local_state_path):
        return None
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)

        enc_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        master_key = decrypt_dpapi(enc_key)

        leveldb = os.path.join(appdata, 'discord', 'Local Storage', 'leveldb')
        tokens = []
        if os.path.exists(leveldb):
            for file in os.listdir(leveldb):
                if not (file.endswith('.ldb') or file.endswith('.log')):
                    continue
                filepath = os.path.join(leveldb, file)
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    for match in re.findall(rb'dQw4w9WgXcQ:[^"]*', content):
                        raw_val = match.split(b':')[1]
                        try:
                            encrypted_token = base64.b64decode(raw_val)
                            iv = encrypted_token[3:15]
                            payload = encrypted_token[15:]
                            aes = AESGCM(master_key)
                            token = aes.decrypt(iv, payload, None).decode('utf-8')
                            if token not in tokens:
                                tokens.append(token)
                        except Exception:
                            pass
                except Exception:
                    pass

        for t in tokens:
            res = requests.get('https://discord.com/api/v9/users/@me', headers={'Authorization': t}, timeout=5)
            if res.status_code == 200:
                return t
    except Exception as e:
        log(f"[Discord Token Error] {e}")
    return None

def get_active_thread_id(token, badge=None, thread_override=None):
    if thread_override and thread_override.strip():
        return thread_override.strip()
    manual_thread = CONFIG.get("thread_id", "").strip()
    if manual_thread:
        return manual_thread

    badge = str(badge or CONFIG.get("user_badge", "")).strip()
    forum_channel = CONFIG.get("forum_channel_id", "1551241898340122756").strip()
    headers = {'Authorization': token}

    if badge:
        try:
            url = f'https://discord.com/api/v9/channels/{forum_channel}/threads/search?name={badge}&sort_by=last_message_time&sort_order=desc'
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                threads = res.json().get('threads', [])
                for t in threads:
                    if badge in t.get('name', ''):
                        log(f"[Thread Finder] Gefunden: {t.get('name')} (ID: {t.get('id')})")
                        return t['id']
        except Exception as e:
            log(f"[Thread Search by Badge Error] {e}")

    try:
        url = f'https://discord.com/api/v9/channels/{forum_channel}/threads/search?sort_by=last_message_time&sort_order=desc'
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            threads = res.json().get('threads', [])
            for t in threads:
                if badge and badge in t.get('name', ''):
                    return t['id']
    except Exception as e:
        log(f"[Thread Search Fallback Error] {e}")

    if badge == "317108":
        return "1566193909250400278"
    return None

def send_to_discord(token, thread_id, title, file_paths):
    url = f"https://discord.com/api/v9/channels/{thread_id}/messages"
    headers = {"Authorization": token}
    files = {}
    opened = []
    attachments = []
    try:
        for i, fp in enumerate(file_paths):
            f = open(fp, "rb")
            opened.append(f)
            fname = os.path.basename(fp)
            files[f"files[{i}]"] = (fname, f, "image/png")
            attachments.append({"id": i, "filename": fname})

        data = {
            "payload_json": json.dumps({
                "content": title,
                "attachments": attachments
            })
        }
        res = requests.post(url, headers=headers, data=data, files=files, timeout=15)
        return res.status_code in (200, 201), res.text
    except Exception as e:
        return False, str(e)
    finally:
        for f in opened:
            f.close()

def calculate_zwischenstand(token=None, thread_id=None):
    if not token:
        token = get_discord_token()
    if not token:
        return None, "Kein Token gefunden"
    if not thread_id:
        thread_id = get_active_thread_id(token)
    if not thread_id:
        return None, "Kein Forum-Thread gefunden"

    headers = {'Authorization': token}
    url = f'https://discord.com/api/v9/channels/{thread_id}/messages?limit=100'
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code != 200:
            return None, f"Fehler {res.status_code}"
        
        messages = res.json()
        counts = {
            'GL/LO': 0,
            'Shoprob etc.': 0,
            'Events': 0,
            'FZ-Raid': 0,
            'Inhaftierungen': 0,
            'Streifenpartner': 0
        }

        for m in messages:
            content = m.get('content', '').strip()
            files = len(m.get('attachments', []))

            snapshots = m.get('message_snapshots', [])
            if snapshots and isinstance(snapshots, list) and len(snapshots) > 0:
                snap_msg = snapshots[0].get('message', {})
                content = snap_msg.get('content', '').strip()
                files = len(snap_msg.get('attachments', []))

            if 'Uprank-Punktesystem' in content or 'Zwischenstand:' in content:
                continue

            has_media = (files > 0) or ('http://' in content or 'https://' in content)
            if not has_media:
                continue

            clean = re.sub(r'<@!?[0-9]+>', '', content).strip().lower()

            if 'event' in clean:
                counts['Events'] += 1
            elif 'fz' in clean or 'fort zancudo' in clean:
                counts['FZ-Raid'] += 1
            elif any(k in clean for k in ['shop', 'ammu', 'geisel']):
                counts['Shoprob etc.'] += 1
            elif 'inhaftierung' in clean or 'knast' in clean or 'sg' in clean or re.search(r'\binh\b', clean) or clean.startswith('inh'):
                counts['Inhaftierungen'] += 1
            elif any(k in clean for k in ['streifenpartner', 'partner', 'rookie']):
                counts['Streifenpartner'] += 1
            elif any(k in clean for k in ['global', 'local']) or re.search(r'\b(gl|lo)\b', clean):
                counts['GL/LO'] += 1

        formatted = (
            "Zwischenstand:\n"
            f"GL/LO: {counts['GL/LO']}/3\n"
            f"Shoprob etc.: {counts['Shoprob etc.']}/3\n"
            f"Events: {counts['Events']}/5\n"
            f"FZ-Raid: {counts['FZ-Raid']}/1\n"
            f"Inhaftierungen: {counts['Inhaftierungen']}/7\n"
            f"Streifenpartner: {counts['Streifenpartner']}/2"
        )
        return counts, formatted
    except Exception as e:
        return None, str(e)

def analyze_image_recommendation(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        h, w = img.shape[:2]
        
        roi_center = img[int(0.6*h):int(0.85*h), int(0.35*w):int(0.65*w)]
        hsv_c = cv2.cvtColor(roi_center, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv_c, (35, 100, 100), (85, 255, 255))
        if np.sum(green_mask > 0) > 2000:
            return "inhaftierung"

        skull_roi = img[int(h * 0.948):int(h * 0.985), int(w * 0.068):int(w * 0.088)]
        hsv_s = cv2.cvtColor(skull_roi, cv2.COLOR_BGR2HSV)
        
        red1 = cv2.inRange(hsv_s, (0, 150, 150), (10, 255, 255))
        red2 = cv2.inRange(hsv_s, (170, 150, 150), (180, 255, 255))
        if np.sum((red1 | red2) > 0) > 75:
            return "global"

        blue_mask = cv2.inRange(hsv_s, (95, 150, 150), (125, 255, 255))
        if np.sum(blue_mask > 0) > 75:
            return "local"
    except Exception:
        pass
    return None

# Auto-Updater Logic
def is_newer_version(remote, local):
    def parse_v(v):
        v = str(v).lstrip('v').strip()
        parts = [int(x) for x in re.findall(r'\d+', v)]
        return parts if parts else [0]
    try:
        return parse_v(remote) > parse_v(local)
    except Exception:
        return False

def check_remote_version(custom_url=None):
    raw_url = (custom_url or CONFIG.get("update_url", "") or DEFAULT_UPDATE_URL).strip()
    if not raw_url:
        return None
    
    url = raw_url
    gh_match = re.search(r'github\.com/([^/]+)/([^/]+)', raw_url)
    if gh_match and "api.github.com" not in raw_url and "raw.githubusercontent.com" not in raw_url:
        owner = gh_match.group(1)
        repo = gh_match.group(2).replace(".git", "").split("/")[0]
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    elif re.match(r'^[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+$', raw_url):
        url = f"https://api.github.com/repos/{raw_url}/releases/latest"

    try:
        headers = {"User-Agent": "LSPD-Log-Assistent"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200 or "<html" in res.text[:200].lower():
            fallback_url = "https://raw.githubusercontent.com/KaputzeKings/lspd-logger/main/version.json"
            if url != fallback_url:
                res = requests.get(fallback_url, headers=headers, timeout=5)
            if res.status_code != 200 or "<html" in res.text[:200].lower():
                return None
        data = res.json()
        
        if "tag_name" in data:
            remote_ver = data.get("tag_name", "").lstrip("v").strip()
            changelog = data.get("body", "Neue Version verfügbar.")
            download_url = ""
            assets = data.get("assets", [])
            for a in assets:
                name = a.get("name", "").lower()
                if name.endswith(".zip") or name.endswith(".exe"):
                    download_url = a.get("browser_download_url")
                    break
            if not download_url and data.get("zipball_url"):
                download_url = data.get("zipball_url")
        else:
            remote_ver = str(data.get("version", "")).lstrip("v").strip()
            changelog = data.get("changelog", "Neue Version verfügbar.")
            download_url = data.get("download_url", "")

        has_update = is_newer_version(remote_ver, CURRENT_VERSION) and bool(download_url)
        return {
            "has_update": has_update,
            "version": remote_ver,
            "changelog": changelog,
            "download_url": download_url
        }
    except Exception as e:
        log(f"[Updater Check] {e}")
        return None

def apply_update_and_restart(source_folder, temp_dir):
    import subprocess
    app_dir = BASE_DIR
    exe_name = "LSPD_Log_Assistent.exe"
    bat_path = os.path.join(temp_dir, "apply_update.bat")

    script = f"""@echo off
taskkill /f /im {exe_name} >nul 2>&1
timeout /t 1 /nobreak >nul

if exist "{app_dir}\\config.json" (
    copy /y "{app_dir}\\config.json" "{temp_dir}\\config_backup.json" >nul
)

xcopy /e /y /q "{source_folder}\\*" "{app_dir}\\"

if exist "{temp_dir}\\config_backup.json" (
    copy /y "{temp_dir}\\config_backup.json" "{app_dir}\\config.json" >nul
    del /f /q "{temp_dir}\\config_backup.json" 2>nul
)

start "" "{app_dir}\\{exe_name}"
exit
"""
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(script)
        log(f"[Updater] Starte Update-Script: {bat_path}")
        subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True, creationflags=0x00000008)
        time.sleep(0.3)
        os._exit(0)
    except Exception as e:
        log(f"[Apply Update Error] {e}")

def calculate_overlay_geometry(scale=1.0, position="Oben Rechts"):
    screen = QApplication.primaryScreen().geometry()
    base_w = 350
    base_h = 530
    w = int(base_w * scale)
    h = int(base_h * scale)
    
    margin_x = 40
    margin_y = 50

    if position == "Oben Links":
        x = margin_x
        y = margin_y
    elif position == "Unten Rechts":
        x = screen.width() - w - margin_x
        y = screen.height() - h - 70
    elif position == "Unten Links":
        x = margin_x
        y = screen.height() - h - 70
    elif position == "Mitte":
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
    else: # Oben Rechts
        x = screen.width() - w - margin_x
        y = margin_y

    return x, y, w, h

class OverlaySignal(QObject):
    show_overlay = Signal(str, str)
    hide_overlay = Signal()
    key_pressed = Signal(str)
    update_stats = Signal(dict)
    open_settings = Signal()
    show_update_dialog = Signal(dict)
    show_msg = Signal(str, str, str)
    update_progress = Signal(int, str)
    reload_theme = Signal()
    toggle_calculator = Signal()

overlay_signal = OverlaySignal()

# Update Dialog
class UpdateDialog(QDialog):
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle("LSPD Log Assistent - Update verfügbar")
        self.setFixedSize(500, 390)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.init_ui()
        overlay_signal.update_progress.connect(self.on_progress)

    def init_ui(self):
        colors = get_theme_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg']};
                border: 2px solid {colors['border']};
                border-radius: 12px;
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QTextEdit {{
                background-color: {colors['card_bg']};
                color: {colors['text_muted']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }}
            QProgressBar {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
                height: 22px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent']}, stop:1 {colors['accent_hover']});
                border-radius: 5px;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent']}, stop:1 {colors['accent_hover']});
                color: #ffffff;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid {colors['border']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent_hover']}, stop:1 {colors['border']});
            }}
            QPushButton#btnLater {{
                background: #261122;
                border: 1px solid #701a75;
                color: #f472b6;
            }}
            QPushButton#btnLater:hover {{
                background: #3b1434;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(f"🚀 <span style='color: {colors['border']}; font-size: 15px;'><b>Neues Update verfügbar!</b></span>")
        layout.addWidget(title)

        new_ver = self.update_info.get("version", "Neu")
        v_label = QLabel(f"Version <span style='color: {colors['border']};'><b>v{new_ver}</b></span> ist bereit zum Download (Deine Version: v{CURRENT_VERSION}).")
        v_label.setStyleSheet(f"font-size: 12px; color: {colors['text_muted']};")
        layout.addWidget(v_label)

        layout.addWidget(QLabel("Was ist neu in diesem Update:"))
        self.changelog_box = QTextEdit()
        self.changelog_box.setReadOnly(True)
        changelog_text = self.update_info.get("changelog", "Keine Versionshinweise vorhanden.")
        self.changelog_box.setPlainText(changelog_text)
        layout.addWidget(self.changelog_box)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 11px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)

        self.btn_update = QPushButton("⬇️ Jetzt automatisch aktualisieren")
        self.btn_update.clicked.connect(self.start_download)
        self.btn_layout.addWidget(self.btn_update)

        self.btn_later = QPushButton("Später")
        self.btn_later.setObjectName("btnLater")
        self.btn_later.clicked.connect(self.reject)
        self.btn_layout.addWidget(self.btn_later)

        layout.addLayout(self.btn_layout)

    def start_download(self):
        download_url = self.update_info.get("download_url")
        if not download_url:
            QMessageBox.warning(self, "Fehler", "Keine Download-URL gefunden!")
            return

        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Lade Update herunter...")

        threading.Thread(target=self._download_worker, args=(download_url,), daemon=True).start()

    def _download_worker(self, download_url):
        import tempfile
        try:
            try:
                temp_dir = tempfile.mkdtemp(prefix="lspd_upd_")
            except Exception:
                temp_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), f"lspd_upd_{int(time.time())}")
                os.makedirs(temp_dir, exist_ok=True)
            
            is_zip = download_url.lower().endswith(".zip") or ".zip?" in download_url.lower()
            fname = "update.zip" if is_zip else "LSPD_Log_Assistent_new.exe"
            dest_file = os.path.join(temp_dir, fname)

            if os.path.exists(dest_file):
                try:
                    os.remove(dest_file)
                except Exception:
                    dest_file = os.path.join(temp_dir, f"update_{int(time.time())}.zip" if is_zip else f"LSPD_Log_Assistent_{int(time.time())}.exe")

            res = requests.get(download_url, stream=True, timeout=30)
            if res.status_code != 200:
                overlay_signal.update_progress.emit(-1, f"Download-Fehler (HTTP {res.status_code})")
                return

            total_size = int(res.headers.get('content-length', 0))
            downloaded = 0

            with open(dest_file, "wb") as f:
                for chunk in res.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = int((downloaded / total_size) * 85)
                            mb_down = downloaded / (1024 * 1024)
                            mb_tot = total_size / (1024 * 1024)
                            overlay_signal.update_progress.emit(pct, f"Heruntergeladen: {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct}%)")
                        else:
                            mb_down = downloaded / (1024 * 1024)
                            overlay_signal.update_progress.emit(50, f"Heruntergeladen: {mb_down:.1f} MB...")

            overlay_signal.update_progress.emit(90, "Entpacke Update-Dateien...")
            extracted_dir = os.path.join(temp_dir, "extracted")
            if os.path.exists(extracted_dir):
                import shutil
                shutil.rmtree(extracted_dir, ignore_errors=True)
            os.makedirs(extracted_dir, exist_ok=True)

            if is_zip:
                import zipfile
                with zipfile.ZipFile(dest_file, 'r') as zip_ref:
                    zip_ref.extractall(extracted_dir)
                source_folder = extracted_dir
                for sub in os.listdir(extracted_dir):
                    sub_path = os.path.join(extracted_dir, sub)
                    if os.path.isdir(sub_path) and os.path.exists(os.path.join(sub_path, "LSPD_Log_Assistent.exe")):
                        source_folder = sub_path
                        break
            else:
                source_folder = extracted_dir
                import shutil
                shutil.copy(dest_file, os.path.join(source_folder, "LSPD_Log_Assistent.exe"))

            overlay_signal.update_progress.emit(100, "Update bereit! Starte neu...")
            time.sleep(0.5)
            apply_update_and_restart(source_folder, temp_dir)

        except Exception as e:
            import traceback
            log(f"[Updater Download Error] {traceback.format_exc()}")
            overlay_signal.update_progress.emit(-1, f"Fehler: {str(e)}")

    def on_progress(self, pct, status):
        self.status_label.setWordWrap(True)
        if pct >= 0:
            self.progress_bar.setValue(pct)
            self.status_label.setText(status)
        else:
            self.status_label.setText(str(status))
            self.btn_update.setEnabled(True)
            self.btn_later.setEnabled(True)

# Full Customizable Setup Dialog with Tabs
class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LSPD Log Assistent - Einstellungen")
        self.setFixedSize(540, 560)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.init_ui()

    def init_ui(self):
        colors = get_theme_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0f0c18;
                border: 2px solid {colors['border']};
                border-radius: 12px;
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['accent']};
                background: #130f20;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: #171324;
                color: #d8b4fe;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: {colors['accent']};
                color: #ffffff;
            }}
            QLabel {{
                color: #f5f3ff;
                font-size: 11px;
                font-weight: bold;
            }}
            QLineEdit, QComboBox {{
                background-color: #1a1528;
                color: #ffffff;
                border: 1px solid #4c1d95;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {colors['border']};
                background-color: #231b36;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent']}, stop:1 {colors['accent_hover']});
                color: #ffffff;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 11px;
                font-weight: bold;
                border: 1px solid {colors['border']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent_hover']}, stop:1 {colors['border']});
            }}
            QPushButton#btnBrowse, QPushButton#btnColor {{
                background: #251c3a;
                border: 1px solid #4c1d95;
                color: #d8b4fe;
                padding: 5px 10px;
            }}
            QPushButton#btnBrowse:hover, QPushButton#btnColor:hover {{
                background: #3b285a;
                color: #ffffff;
            }}
            QPushButton#btnCancel {{
                background: #261122;
                border: 1px solid #701a75;
                color: #f472b6;
            }}
            QPushButton#btnCancel:hover {{
                background: #3b1434;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # Title
        title_label = QLabel(f"🛡️ <span style='color: {colors['border']}; font-size: 15px;'><b>LSPD Log Assistent</b></span> <span style='color: #a855f7; font-size: 11px;'>v{CURRENT_VERSION}</span>")
        layout.addWidget(title_label)

        # Tabs
        self.tabs = QTabWidget()

        # --- TAB 1: Dienst & Discord ---
        tab_service = QWidget()
        l_serv = QVBoxLayout(tab_service)
        l_serv.setContentsMargins(12, 12, 12, 12)
        l_serv.setSpacing(8)

        l_serv.addWidget(QLabel("1. Reisepassnummer / Badge-ID (z. B. 317595):"))
        self.badge_input = QLineEdit()
        self.badge_input.setText(str(CONFIG.get("user_badge", "")))
        l_serv.addWidget(self.badge_input)

        l_serv.addWidget(QLabel("2. Medal Screenshot-Ordner:"))
        dir_lay = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(CONFIG.get("watch_dir", get_default_watch_dir()))
        dir_lay.addWidget(self.dir_input)
        browse_btn = QPushButton("📁 Durchsuchen")
        browse_btn.setObjectName("btnBrowse")
        browse_btn.clicked.connect(self.choose_directory)
        dir_lay.addWidget(browse_btn)
        l_serv.addLayout(dir_lay)

        l_serv.addWidget(QLabel("3. Forum Thread-ID (Optional):"))
        self.thread_input = QLineEdit()
        self.thread_input.setPlaceholderText("Leer lassen für automatische Suche")
        self.thread_input.setText(CONFIG.get("thread_id", ""))
        l_serv.addWidget(self.thread_input)

        info_box = QFrame()
        info_box.setStyleSheet("background: #171324; border: 1px solid #4c1d95; border-radius: 6px; padding: 4px;")
        ib_lay = QVBoxLayout(info_box)
        ib_lay.setContentsMargins(6, 6, 6, 6)
        itxt = QLabel("ℹ️ <b>Discord-Token:</b> Wird automatisch und sicher aus deiner Desktop-App gelesen.")
        itxt.setStyleSheet("color: #d8b4fe; font-size: 10px; font-weight: normal; border: none;")
        ib_lay.addWidget(itxt)
        l_serv.addWidget(info_box)

        self.tabs.addTab(tab_service, "👮 Dienst & Discord")

        # --- TAB 2: HUD & Aussehen ---
        tab_hud = QWidget()
        l_hud = QVBoxLayout(tab_hud)
        l_hud.setContentsMargins(12, 12, 12, 12)
        l_hud.setSpacing(8)

        hud_conf = CONFIG.get("hud", {})

        # Theme selection
        l_hud.addWidget(QLabel("1. Farb-Theme:"))
        self.theme_combo = QComboBox()
        theme_names = list(THEMES.keys()) + ["Benutzerdefiniert"]
        self.theme_combo.addItems(theme_names)
        curr_theme = hud_conf.get("theme", "Schwarz-Lila (Standard)")
        idx = self.theme_combo.findText(curr_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        l_hud.addWidget(self.theme_combo)

        # Custom colors row
        custom_row = QHBoxLayout()
        self.btn_bg_color = QPushButton("Hintergrund")
        self.btn_bg_color.setObjectName("btnColor")
        self.btn_bg_color.clicked.connect(self.pick_bg_color)
        custom_row.addWidget(self.btn_bg_color)

        self.btn_accent_color = QPushButton("Akzent/Border")
        self.btn_accent_color.setObjectName("btnColor")
        self.btn_accent_color.clicked.connect(self.pick_accent_color)
        custom_row.addWidget(self.btn_accent_color)

        self.btn_text_color = QPushButton("Textfarbe")
        self.btn_text_color.setObjectName("btnColor")
        self.btn_text_color.clicked.connect(self.pick_text_color)
        custom_row.addWidget(self.btn_text_color)
        l_hud.addLayout(custom_row)

        self.custom_bg = hud_conf.get("custom_bg", "#0f0c18")
        self.custom_accent = hud_conf.get("custom_accent", "#a855f7")
        self.custom_text = hud_conf.get("custom_text", "#f5f3ff")

        # Scale & Position
        grid_hud = QGridLayout()
        grid_hud.setSpacing(6)

        grid_hud.addWidget(QLabel("2. HUD-Größe / Skalierung:"), 0, 0)
        self.scale_combo = QComboBox()
        self.scale_combo.addItem("Kompakt (85%)", 0.85)
        self.scale_combo.addItem("Standard (100%)", 1.0)
        self.scale_combo.addItem("Groß (115%)", 1.15)
        self.scale_combo.addItem("Sehr groß (130%)", 1.30)
        curr_scale = float(hud_conf.get("scale", 1.0))
        for i in range(self.scale_combo.count()):
            if abs(self.scale_combo.itemData(i) - curr_scale) < 0.05:
                self.scale_combo.setCurrentIndex(i)
                break
        grid_hud.addWidget(self.scale_combo, 0, 1)

        grid_hud.addWidget(QLabel("3. Bildschirm-Position:"), 1, 0)
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(["Oben Rechts", "Oben Links", "Unten Rechts", "Unten Links", "Mitte"])
        self.pos_combo.setCurrentText(hud_conf.get("position", "Oben Rechts"))
        grid_hud.addWidget(self.pos_combo, 1, 1)

        grid_hud.addWidget(QLabel("4. Schriftart (Font):"), 2, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Bahnschrift", "Roboto", "Montserrat", "Arial", "Consolas"])
        curr_font = hud_conf.get("font_family", "Segoe UI")
        f_idx = self.font_combo.findText(curr_font)
        if f_idx >= 0:
            self.font_combo.setCurrentIndex(f_idx)
        grid_hud.addWidget(self.font_combo, 2, 1)

        grid_hud.addWidget(QLabel("5. Schriftgröße:"), 3, 0)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItem("Klein (10pt)", 10)
        self.font_size_combo.addItem("Normal (11pt)", 11)
        self.font_size_combo.addItem("Groß (12pt)", 12)
        self.font_size_combo.addItem("Extra Groß (13pt)", 13)
        curr_fsize = int(hud_conf.get("font_size", 11))
        for i in range(self.font_size_combo.count()):
            if self.font_size_combo.itemData(i) == curr_fsize:
                self.font_size_combo.setCurrentIndex(i)
                break
        grid_hud.addWidget(self.font_size_combo, 3, 1)

        grid_hud.addWidget(QLabel("6. F12 Rechner Größe:"), 4, 0)
        self.calc_scale_combo = QComboBox()
        self.calc_scale_combo.addItem("Kompakt (75%)", 0.75)
        self.calc_scale_combo.addItem("Standard (82%)", 0.82)
        self.calc_scale_combo.addItem("Groß (88%)", 0.88)
        self.calc_scale_combo.addItem("Sehr groß (95%)", 0.95)
        c_scale = float(CONFIG.get("calc_scale", 0.82))
        for i in range(self.calc_scale_combo.count()):
            if abs(self.calc_scale_combo.itemData(i) - c_scale) < 0.02:
                self.calc_scale_combo.setCurrentIndex(i)
                break
        grid_hud.addWidget(self.calc_scale_combo, 4, 1)

        l_hud.addLayout(grid_hud)

        # Opacity Slider
        l_hud.addWidget(QLabel("6. Transparenz / Deckkraft:"))
        op_lay = QHBoxLayout()
        self.op_slider = QSlider(Qt.Horizontal)
        self.op_slider.setRange(75, 100)
        curr_op = int(float(hud_conf.get("opacity", 0.96)) * 100)
        self.op_slider.setValue(curr_op)
        self.op_label = QLabel(f"{curr_op}%")
        self.op_slider.valueChanged.connect(lambda v: self.op_label.setText(f"{v}%"))
        op_lay.addWidget(self.op_slider)
        op_lay.addWidget(self.op_label)
        l_hud.addLayout(op_lay)

        # Test Preview button
        self.btn_preview = QPushButton("👁️ HUD-Vorschau jetzt testen")
        self.btn_preview.setObjectName("btnBrowse")
        self.btn_preview.clicked.connect(self.trigger_hud_preview)
        l_hud.addWidget(self.btn_preview)

        self.tabs.addTab(tab_hud, "🎨 HUD & Aussehen")

        layout.addWidget(self.tabs)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.save_btn = QPushButton("💾 Einstellungen speichern & anwenden")
        self.save_btn.clicked.connect(self.save_and_close)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.setObjectName("btnCancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def choose_directory(self):
        curr = self.dir_input.text()
        chosen = QFileDialog.getExistingDirectory(self, "Medal Screenshot Ordner auswählen", curr or os.path.expanduser("~"))
        if chosen:
            self.dir_input.setText(chosen)

    def pick_bg_color(self):
        col = QColorDialog.getColor(QColor(self.custom_bg), self, "Hintergrundfarbe wählen")
        if col.isValid():
            self.custom_bg = col.name()
            self.theme_combo.setCurrentText("Benutzerdefiniert")

    def pick_accent_color(self):
        col = QColorDialog.getColor(QColor(self.custom_accent), self, "Akzentfarbe wählen")
        if col.isValid():
            self.custom_accent = col.name()
            self.theme_combo.setCurrentText("Benutzerdefiniert")

    def pick_text_color(self):
        col = QColorDialog.getColor(QColor(self.custom_text), self, "Textfarbe wählen")
        if col.isValid():
            self.custom_text = col.name()
            self.theme_combo.setCurrentText("Benutzerdefiniert")

    def trigger_hud_preview(self):
        self.apply_to_config_runtime()
        overlay_signal.reload_theme.emit()

    def apply_to_config_runtime(self):
        CONFIG["user_badge"] = self.badge_input.text().strip()
        CONFIG["watch_dir"] = self.dir_input.text().strip() or get_default_watch_dir()
        CONFIG["thread_id"] = self.thread_input.text().strip()
        CONFIG["calc_scale"] = float(self.calc_scale_combo.currentData())

        CONFIG["hud"] = {
            "theme": self.theme_combo.currentText(),
            "scale": float(self.scale_combo.currentData()),
            "position": self.pos_combo.currentText(),
            "font_family": self.font_combo.currentText(),
            "font_size": int(self.font_size_combo.currentData()),
            "opacity": float(self.op_slider.value()) / 100.0,
            "auto_close_sec": 25,
            "custom_bg": self.custom_bg,
            "custom_accent": self.custom_accent,
            "custom_text": self.custom_text
        }

    def save_and_close(self):
        badge = self.badge_input.text().strip()
        if not badge:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte gib deine Reisepassnummer / Badge-ID ein!")
            return

        self.apply_to_config_runtime()
        save_config(CONFIG)
        log(f"[Setup] Gespeichert: Badge={badge}, HUD Theme={CONFIG['hud']['theme']}, Scale={CONFIG['hud']['scale']}")
        overlay_signal.reload_theme.emit()
        self.accept()

# Full Customizable Overlay Window
class PDOverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_screenshot = None
        self.pending_two_shot = self.load_pending_state()
        self.init_ui()

    def load_pending_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def save_pending_state(self, state):
        self.pending_two_shot = state
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass

    def clear_pending_state(self):
        self.pending_two_shot = None
        if os.path.exists(STATE_FILE):
            try:
                os.remove(STATE_FILE)
            except Exception:
                pass

    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.card = QFrame(self)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(6)
        self.card_layout.setContentsMargins(12, 12, 12, 12)

        # Header Title
        self.header_label = QLabel()
        self.card_layout.addWidget(self.header_label)

        # Stats frame
        self.stats_frame = QFrame()
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(6, 6, 6, 6)
        self.stats_layout.setSpacing(2)

        self.stats_title = QLabel("📊 <b>Aktueller Zwischenstand:</b>")
        self.stats_layout.addWidget(self.stats_title)

        self.stats_line1 = QLabel("GL/LO: ?/3  |  Shop: ?/3  |  Events: ?/5")
        self.stats_layout.addWidget(self.stats_line1)

        self.stats_line2 = QLabel("FZ: ?/1  |  Inh: ?/7  |  Partner: ?/2")
        self.stats_layout.addWidget(self.stats_line2)

        self.card_layout.addWidget(self.stats_frame)

        # Status text
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.card_layout.addWidget(self.status_label)

        # Thumbnail Image
        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.thumb_label)

        # Action Buttons Grid (4 rows x 2 columns)
        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        self.btn_inhaftierung = QPushButton("[1] 🟢 Inhaftierung")
        self.btn_inhaftierung.clicked.connect(lambda: self.handle_action("Inhaftierung", 1))
        self.grid.addWidget(self.btn_inhaftierung, 0, 0)

        self.btn_global = QPushButton("[2] 🔴 Global")
        self.btn_global.clicked.connect(lambda: self.handle_action("Global", 1))
        self.grid.addWidget(self.btn_global, 0, 1)

        self.btn_local = QPushButton("[3] 🔵 Local")
        self.btn_local.clicked.connect(lambda: self.handle_action("Local", 1))
        self.grid.addWidget(self.btn_local, 1, 0)

        self.btn_event = QPushButton("[4] 🟣 Event")
        self.btn_event.clicked.connect(lambda: self.handle_event_action("Event"))
        self.grid.addWidget(self.btn_event, 1, 1)

        self.btn_shoprob = QPushButton("[5] 🟠 Shoprob")
        self.btn_shoprob.clicked.connect(lambda: self.handle_shoprob_action("Ammu-Rob"))
        self.grid.addWidget(self.btn_shoprob, 2, 0)

        self.btn_fz = QPushButton("[6] 🪖 FZ-Raid")
        self.btn_fz.clicked.connect(lambda: self.handle_fz_action("FZ Raid"))
        self.grid.addWidget(self.btn_fz, 2, 1)

        # NEW ACTION: Streifenpartner mitnehmen!
        self.btn_streifenpartner = QPushButton("[7] 👥 Streifenpartner")
        self.btn_streifenpartner.clicked.connect(lambda: self.handle_action("Streifenpartner mitnehmen", 1))
        self.grid.addWidget(self.btn_streifenpartner, 3, 0, 1, 2)

        self.card_layout.addLayout(self.grid)

        # Intermediate Summary Button
        self.btn_send_summary = QPushButton("[8] / [Z] 📊 Zwischenstand in Chat senden")
        self.btn_send_summary.clicked.connect(self.handle_send_summary)
        self.card_layout.addWidget(self.btn_send_summary)

        # Cancel Button
        self.btn_cancel = QPushButton("[ESC] ❌ Verwerfen (Nicht posten)")
        self.btn_cancel.clicked.connect(self.close_overlay)
        self.card_layout.addWidget(self.btn_cancel)

        # Notification Bar
        self.notify_label = QLabel("")
        self.notify_label.setAlignment(Qt.AlignCenter)
        self.notify_label.setVisible(False)
        self.card_layout.addWidget(self.notify_label)

        layout.addWidget(self.card)

        self.auto_timer = QTimer(self)
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self.close_overlay)

        self.apply_theme()

    def apply_theme(self):
        hud = CONFIG.get("hud", {})
        colors = get_theme_colors(hud)
        scale = float(hud.get("scale", 1.0))
        font_family = hud.get("font_family", "Segoe UI")
        font_size = int(hud.get("font_size", 11))
        opacity = float(hud.get("opacity", 0.96))
        
        self.setWindowOpacity(opacity)
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        pos = hud.get("position", "Oben Rechts")
        x, y, w, h = calculate_overlay_geometry(scale, pos)
        self.setGeometry(x, y, w, h)

        badge_text = str(CONFIG.get("user_badge", "317108"))
        self.header_label.setText(f"📸 <span style='color: {colors['border']};'><b>LSPD</b></span> <span style='color: #ffffff;'><b>Log Assistent</b></span> <span style='color: {colors['accent_hover']}; font-size: {int(font_size*0.9)}px;'>[{badge_text}]</span>")
        self.header_label.setStyleSheet(f"font-size: {int(font_size * 1.2)}px; border: none; font-family: '{font_family}';")

        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg']};
                border: 2px solid {colors['border']};
                border-radius: {int(12 * scale)}px;
                font-family: "{font_family}";
            }}
        """)

        self.stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['accent']};
                border-radius: {int(6 * scale)}px;
                padding: {int(4 * scale)}px;
            }}
        """)
        self.stats_title.setStyleSheet(f"color: {colors['text_muted']}; font-size: {int(font_size * 0.95)}px; font-weight: bold; border: none;")
        self.stats_line1.setStyleSheet(f"color: {colors['text']}; font-size: {int(font_size * 0.92)}px; font-weight: bold; border: none;")
        self.stats_line2.setStyleSheet(f"color: {colors['text']}; font-size: {int(font_size * 0.92)}px; font-weight: bold; border: none;")

        self.status_label.setStyleSheet(f"color: {colors['border']}; font-size: {int(font_size * 0.95)}px; font-weight: bold; border: none;")
        self.notify_label.setStyleSheet(f"color: {colors['border']}; font-size: {int(font_size * 1.05)}px; font-weight: bold; border: none;")

        thumb_w = int(290 * scale)
        thumb_h = int(135 * scale)
        self.thumb_label.setFixedSize(thumb_w, thumb_h)
        self.thumb_label.setStyleSheet(f"background-color: {colors['thumb_bg']}; border-radius: {int(6 * scale)}px; border: 1px solid {colors['accent']};")

        self.btn_base_style = f"""
            QPushButton {{
                background-color: {colors['btn_bg']};
                color: {colors['text']};
                border-radius: {int(6 * scale)}px;
                padding: {int(6 * scale)}px {int(8 * scale)}px;
                font-size: {font_size}px;
                font-weight: bold;
                border: 1px solid {colors['accent']};
                text-align: left;
                font-family: "{font_family}";
            }}
            QPushButton:hover {{
                background-color: {colors['btn_hover']};
                color: #ffffff;
                border-color: {colors['border']};
            }}
            QPushButton:pressed {{
                background-color: {colors['bg']};
            }}
        """

        self.btn_send_summary.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent']}, stop:1 {colors['accent_hover']});
                color: #ffffff;
                border-radius: {int(6 * scale)}px;
                padding: {int(7 * scale)}px {int(10 * scale)}px;
                font-size: {font_size}px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                text-align: center;
                font-family: "{font_family}";
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['accent_hover']}, stop:1 {colors['border']});
            }}
            QPushButton:pressed {{
                background: {colors['accent_pressed']};
            }}
        """)

        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #261122;
                color: #f472b6;
                border-radius: {int(6 * scale)}px;
                padding: {int(6 * scale)}px {int(10 * scale)}px;
                font-size: {font_size}px;
                font-weight: bold;
                border: 1px solid #701a75;
                font-family: "{font_family}";
            }}
            QPushButton:hover {{
                background-color: #3b1434;
                color: #ffffff;
            }}
        """)

        self.reset_button_styles()

    def update_stats_ui(self, counts):
        if counts:
            gl = f"{counts.get('GL/LO', 0)}/3"
            sh = f"{counts.get('Shoprob etc.', 0)}/3"
            ev = f"{counts.get('Events', 0)}/5"
            fz = f"{counts.get('FZ-Raid', 0)}/1"
            inh = f"{counts.get('Inhaftierungen', 0)}/7"
            part = f"{counts.get('Streifenpartner', 0)}/2"
            self.stats_line1.setText(f"GL/LO: {gl}  |  Shop: {sh}  |  Events: {ev}")
            self.stats_line2.setText(f"FZ: {fz}  |  Inh: {inh}  |  Partner: {part}")
            log(f"[UI] Stats: GL/LO={gl}, Shop={sh}, Ev={ev}, FZ={fz}, Inh={inh}, Partner={part}")

    def display_screenshot(self, screenshot_path, recommendation=None):
        log(f"[UI] display_screenshot: {screenshot_path}")
        self.current_screenshot = screenshot_path
        self.pending_two_shot = self.load_pending_state()
        
        pix = QPixmap(screenshot_path)
        if not pix.isNull():
            hud = CONFIG.get("hud", {})
            scale = float(hud.get("scale", 1.0))
            thumb_w = int(290 * scale)
            thumb_h = int(135 * scale)
            scaled = pix.scaled(thumb_w, thumb_h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.thumb_label.setPixmap(scaled)

        self.reset_button_styles()

        if self.pending_two_shot and self.pending_two_shot.get("type") == "Event":
            self.status_label.setText("⏳ Event: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_event.setText("[4] 🟣 Event (2/2 Senden)")
            self.highlight_button(self.btn_event, "#c084fc")
        else:
            self.btn_event.setText("[4] 🟣 Event (1/2 Start)")

        if self.pending_two_shot and self.pending_two_shot.get("type") == "Ammu-Rob":
            self.status_label.setText("⏳ Shoprob: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_shoprob.setText("[5] 🟠 Shoprob (2/2 Senden)")
            self.highlight_button(self.btn_shoprob, "#e67e22")
        else:
            self.btn_shoprob.setText("[5] 🟠 Shoprob (1/2 Start)")

        if self.pending_two_shot and self.pending_two_shot.get("type") == "FZ Raid":
            self.status_label.setText("⏳ FZ-Raid: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_fz.setText("[6] 🪖 FZ-Raid (2/2 Senden)")
            self.highlight_button(self.btn_fz, "#2ecc71")
        else:
            self.btn_fz.setText("[6] 🪖 FZ-Raid (1/2 Start)")

        if not self.pending_two_shot:
            self.status_label.setVisible(False)
            if recommendation == "inhaftierung":
                self.highlight_button(self.btn_inhaftierung, "#57f287")
                self.btn_inhaftierung.setText("[1] 🟢 Inhaftierung ⭐")
            elif recommendation == "global":
                self.highlight_button(self.btn_global, "#ed4245")
                self.btn_global.setText("[2] 🔴 Global ⭐")
            elif recommendation == "local":
                self.highlight_button(self.btn_local, "#5865f2")
                self.btn_local.setText("[3] 🔵 Local ⭐")

        self.notify_label.setVisible(False)
        self.show()
        self.raise_()
        self.activateWindow()

        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception as e:
            log(f"[Win32 Error] {e}")

        threading.Thread(target=self._fetch_stats_async, daemon=True).start()

        try:
            winsound.Beep(1200, 100)
        except Exception:
            pass

        hud_close = int(CONFIG.get("hud", {}).get("auto_close_sec", 25))
        if hud_close > 0:
            self.auto_timer.start(hud_close * 1000)

    def _fetch_stats_async(self):
        counts, _ = calculate_zwischenstand()
        if counts:
            overlay_signal.update_stats.emit(counts)

    def highlight_button(self, btn, border_color):
        hud = CONFIG.get("hud", {})
        colors = get_theme_colors(hud)
        scale = float(hud.get("scale", 1.0))
        font_size = int(hud.get("font_size", 11))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['btn_hover']};
                color: #ffffff;
                border-radius: {int(6 * scale)}px;
                padding: {int(6 * scale)}px {int(8 * scale)}px;
                font-size: {font_size}px;
                font-weight: bold;
                border: 2px solid {border_color};
                text-align: left;
            }}
        """)

    def reset_button_styles(self):
        self.btn_inhaftierung.setStyleSheet(self.btn_base_style)
        self.btn_inhaftierung.setText("[1] 🟢 Inhaftierung")
        self.btn_global.setStyleSheet(self.btn_base_style)
        self.btn_global.setText("[2] 🔴 Global")
        self.btn_local.setStyleSheet(self.btn_base_style)
        self.btn_local.setText("[3] 🔵 Local")
        self.btn_event.setStyleSheet(self.btn_base_style)
        self.btn_event.setText("[4] 🟣 Event")
        self.btn_shoprob.setStyleSheet(self.btn_base_style)
        self.btn_fz.setStyleSheet(self.btn_base_style)
        self.btn_streifenpartner.setStyleSheet(self.btn_base_style)

    def handle_action(self, title, count):
        self.auto_timer.stop()
        self.show_notification(f"⏳ Sende {title}...")
        threading.Thread(target=self._send_async, args=(title, [self.current_screenshot]), daemon=True).start()

    def handle_event_action(self, title):
        self.auto_timer.stop()
        if self.pending_two_shot and self.pending_two_shot.get("type") == "Event":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification("⏳ Sende Event (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("Event", [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "Event", "path": self.current_screenshot, "time": time.time()})
            self.show_notification("📌 Foto 1 gespeichert! Warte auf Foto 2.")
            try:
                winsound.Beep(900, 80)
                winsound.Beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_shoprob_action(self, title):
        self.auto_timer.stop()
        if self.pending_two_shot and self.pending_two_shot.get("type") == "Ammu-Rob":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification("⏳ Sende Shoprob (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("Ammu-Rob", [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "Ammu-Rob", "path": self.current_screenshot, "time": time.time()})
            self.show_notification("📌 Foto 1 gespeichert! Warte auf Foto 2.")
            try:
                winsound.Beep(900, 80)
                winsound.Beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_fz_action(self, title):
        self.auto_timer.stop()
        if self.pending_two_shot and self.pending_two_shot.get("type") == "FZ Raid":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification("⏳ Sende FZ-Raid (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("FZ Raid", [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "FZ Raid", "path": self.current_screenshot, "time": time.time()})
            self.show_notification("📌 Foto 1 gespeichert! Warte auf Foto 2.")
            try:
                winsound.Beep(900, 80)
                winsound.Beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_send_summary(self):
        self.auto_timer.stop()
        self.show_notification("⏳ Berechne & sende Zwischenstand...")
        threading.Thread(target=self._send_summary_async, daemon=True).start()

    def _send_summary_async(self):
        token = get_discord_token()
        if not token:
            self.show_notification("❌ Kein Discord Token gefunden!")
            QTimer.singleShot(2500, self.close_overlay)
            return

        thread_id = get_active_thread_id(token)
        if not thread_id:
            self.show_notification("❌ Forum-Thread nicht gefunden!")
            QTimer.singleShot(2500, self.close_overlay)
            return

        counts, formatted = calculate_zwischenstand(token, thread_id)
        if not counts or not formatted:
            self.show_notification("❌ Fehler beim Zählen!")
            QTimer.singleShot(2500, self.close_overlay)
            return

        success, resp = send_to_discord(token, thread_id, formatted, [])
        if success:
            try:
                winsound.Beep(1400, 100)
                winsound.Beep(1800, 150)
            except Exception:
                pass
            self.show_notification("✅ Zwischenstand in Discord gepostet!")
            overlay_signal.update_stats.emit(counts)
            QTimer.singleShot(1800, self.close_overlay)
        else:
            log(f"[Summary Send Error] {resp}")
            self.show_notification("❌ Sende-Fehler!")
            QTimer.singleShot(2500, self.close_overlay)

    def _send_async(self, title, file_paths):
        token = get_discord_token()
        if not token:
            self.show_notification("❌ Kein Discord Token gefunden!")
            QTimer.singleShot(2500, self.close_overlay)
            return

        thread_id = get_active_thread_id(token)
        if not thread_id:
            self.show_notification("❌ Forum-Thread nicht gefunden!")
            QTimer.singleShot(2500, self.close_overlay)
            return

        success, resp = send_to_discord(token, thread_id, title, file_paths)
        if success:
            try:
                winsound.Beep(1500, 100)
                winsound.Beep(1900, 150)
            except Exception:
                pass
            self.show_notification("✅ Erfolgreich in Discord gepostet!")
            threading.Thread(target=self._fetch_stats_async, daemon=True).start()
            QTimer.singleShot(1500, self.close_overlay)
        else:
            log(f"[Upload Error] {resp}")
            self.show_notification("❌ Fehler beim Senden!")
            QTimer.singleShot(2500, self.close_overlay)

    def show_notification(self, text):
        self.notify_label.setText(text)
        self.notify_label.setVisible(True)

    def close_overlay(self):
        self.auto_timer.stop()
        self.hide()

    def on_hotkey_pressed(self, key_char):
        if not self.isVisible():
            return
        log(f"[Hotkey] Taste gedrückt: {key_char}")
        if key_char == "1":
            self.handle_action("Inhaftierung", 1)
        elif key_char == "2":
            self.handle_action("Global", 1)
        elif key_char == "3":
            self.handle_action("Local", 1)
        elif key_char == "4":
            self.handle_event_action("Event")
        elif key_char == "5":
            self.handle_shoprob_action("Ammu-Rob")
        elif key_char == "6":
            self.handle_fz_action("FZ Raid")
        elif key_char == "7":
            self.handle_action("Streifenpartner mitnehmen", 1)
        elif key_char in ["8", "z"]:
            self.handle_send_summary()
        elif key_char == "esc":
            self.close_overlay()

def watch_medal_folder():
    seen_files = set()
    current_watch_dir = CONFIG.get("watch_dir") or get_default_watch_dir()
    if os.path.exists(current_watch_dir):
        seen_files = set(os.listdir(current_watch_dir))

    log(f"[Watcher] Überwache: {current_watch_dir} ({len(seen_files)} Dateien vorhanden)")

    while True:
        try:
            time.sleep(0.5)
            watch_path = CONFIG.get("watch_dir") or get_default_watch_dir()
            if not os.path.exists(watch_path):
                time.sleep(2.0)
                continue
            current_files = set(os.listdir(watch_path))
            new_files = current_files - seen_files
            for fname in new_files:
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    full_path = os.path.join(watch_path, fname)
                    time.sleep(0.3)
                    log(f"[Watcher] Neuer Screenshot: {fname}")
                    rec = analyze_image_recommendation(full_path)
                    log(f"[Watcher] Empfehlung: {rec}")
                    overlay_signal.show_overlay.emit(full_path, rec or "")
            seen_files = current_files
        except Exception as e:
            log(f"[Watcher Exception] {e}")

def midnight_summary_scheduler():
    log("[Midnight Scheduler] Aktiviert für 00:00 Uhr.")
    while True:
        try:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")

            last_sent = None
            if os.path.exists(MIDNIGHT_STATE_FILE):
                try:
                    with open(MIDNIGHT_STATE_FILE, "r") as f:
                        last_sent = json.load(f).get("last_sent")
                except Exception:
                    pass

            if now.hour == 0 and now.minute in [0, 1] and last_sent != today_str:
                log(f"[Midnight Scheduler] 00:00 Uhr! Sende Zusammenfassung...")
                token = get_discord_token()
                if token:
                    thread_id = get_active_thread_id(token)
                    if thread_id:
                        counts, formatted = calculate_zwischenstand(token, thread_id)
                        if counts and formatted:
                            success, resp = send_to_discord(token, thread_id, formatted, [])
                            if success:
                                log(f"[Midnight Scheduler] Gesendet:\n{formatted}")
                                try:
                                    with open(MIDNIGHT_STATE_FILE, "w") as f:
                                        json.dump({"last_sent": today_str, "time": str(now)}, f)
                                except Exception:
                                    pass
                            else:
                                log(f"[Midnight Scheduler] Sende-Fehler: {resp}")
            time.sleep(30)
        except Exception as e:
            log(f"[Midnight Scheduler Exception] {e}")
            time.sleep(60)

def start_keyboard_listener():
    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char:
                c = key.char.lower()
                if c in ['1', '2', '3', '4', '5', '6', '7', '8', 'z']:
                    overlay_signal.key_pressed.emit(c)
            elif key == keyboard.Key.esc:
                overlay_signal.key_pressed.emit("esc")
            elif key == keyboard.Key.f12:
                overlay_signal.toggle_calculator.emit()
        except Exception:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

def create_tray_icon():
    colors = get_theme_colors()
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(colors['accent']))
    p.setPen(QColor(colors['border']))
    p.drawRoundedRect(4, 4, 56, 56, 14, 14)
    p.setFont(QFont("Segoe UI Emoji", 26))
    p.drawText(pix.rect(), int(Qt.AlignCenter), "🚨")
    p.end()
    return QIcon(pix)

def main():
    log(f"[Main] Starte QApplication (v{CURRENT_VERSION})...")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    global CONFIG
    CONFIG = load_config()

    badge = str(CONFIG.get("user_badge", "")).strip()
    if not badge or badge in ["", "DEINE_REISEPASSNUMMER", "000000"]:
        setup = SetupDialog()
        if setup.exec() != QDialog.Accepted:
            log("[Main] Setup abgebrochen, beende.")
            sys.exit(0)
        CONFIG = load_config()

    overlay = PDOverlayWindow()

    overlay_signal.show_overlay.connect(overlay.display_screenshot)
    overlay_signal.key_pressed.connect(overlay.on_hotkey_pressed)
    overlay_signal.update_stats.connect(overlay.update_stats_ui)

    calc_overlay = GrandCalculatorOverlay(get_theme_colors())

    def toggle_calc():
        if calc_overlay.isVisible():
            calc_overlay.hide()
        else:
            calc_overlay.show_calculator()

    overlay_signal.toggle_calculator.connect(toggle_calc)

    def reload_hud_theme():
        overlay.apply_theme()
        calc_overlay.update_theme(get_theme_colors())
        tray.setIcon(create_tray_icon())
        tray.setToolTip(f"LSPD Log Assistent v{CURRENT_VERSION} | Badge: [{CONFIG.get('user_badge')}]")

    overlay_signal.reload_theme.connect(reload_hud_theme)

    def show_settings_dialog():
        dlg = SetupDialog()
        if dlg.exec() == QDialog.Accepted:
            global CONFIG
            CONFIG = load_config()
            reload_hud_theme()
            threading.Thread(target=lambda: overlay._fetch_stats_async(), daemon=True).start()

    overlay_signal.open_settings.connect(show_settings_dialog)

    # Update dialog slot
    def handle_show_update(info):
        UpdateDialog(info).exec()

    overlay_signal.show_update_dialog.connect(handle_show_update)

    def handle_show_msg(title, text, mtype):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(text)
        colors = get_theme_colors()
        box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {colors['bg']};
                color: {colors['text']};
            }}
            QLabel {{
                color: {colors['text']};
                font-size: 12px;
            }}
            QPushButton {{
                background-color: {colors['accent']};
                color: #ffffff;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
        """)
        box.setIcon(QMessageBox.Information if mtype == "info" else QMessageBox.Warning)
        box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        box.exec()

    overlay_signal.show_msg.connect(handle_show_msg)

    # System Tray Icon
    tray = QSystemTrayIcon(create_tray_icon(), app)
    tray.setToolTip(f"LSPD Log Assistent v{CURRENT_VERSION} | Badge: [{CONFIG.get('user_badge')}]")

    colors = get_theme_colors()
    tray_menu = QMenu()
    tray_menu.setStyleSheet(f"""
        QMenu {{
            background-color: {colors['bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 20px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {colors['accent']};
            color: #ffffff;
        }}
    """)

    def trigger_test_overlay():
        wdir = CONFIG.get("watch_dir") or get_default_watch_dir()
        latest_file = None
        if os.path.exists(wdir):
            files = [os.path.join(wdir, f) for f in os.listdir(wdir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if files:
                latest_file = max(files, key=os.path.getmtime)
        
        if not latest_file:
            dummy_path = os.path.join(BASE_DIR, "test_preview.png")
            dummy = np.zeros((720, 1280, 3), dtype=np.uint8)
            dummy[:] = (30, 20, 15)
            cv2.putText(dummy, "LSPD TEST PREVIEW", (380, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.imwrite(dummy_path, dummy)
            latest_file = dummy_path

        overlay_signal.show_overlay.emit(latest_file, "inhaftierung")

    act_test = QAction("📸 Test-Overlay öffnen", tray_menu)
    act_test.triggered.connect(trigger_test_overlay)
    tray_menu.addAction(act_test)

    act_calc = QAction("⚖️ Bußgeld- & TOW-Rechner (F12)", tray_menu)
    act_calc.triggered.connect(toggle_calc)
    tray_menu.addAction(act_calc)

    act_summary = QAction("📊 Zwischenstand jetzt senden", tray_menu)
    act_summary.triggered.connect(overlay.handle_send_summary)
    tray_menu.addAction(act_summary)

    def manual_check_updates():
        tray.showMessage("LSPD Update", "Prüfe auf Updates...", QSystemTrayIcon.Information, 2000)
        def run_check():
            info = check_remote_version()
            if info and info.get("has_update"):
                overlay_signal.show_update_dialog.emit(info)
            elif info:
                overlay_signal.show_msg.emit(
                    "LSPD Update",
                    f"✅ <b>Du nutzt bereits die aktuellste Version (v{CURRENT_VERSION})!</b><br><br>Es ist kein neues Update erforderlich.",
                    "info"
                )
            else:
                overlay_signal.show_msg.emit(
                    "LSPD Update",
                    "⚠️ <b>Update-Prüfung fehlgeschlagen.</b><br><br>Konnte keine Verbindung zum GitHub-Server herstellen.",
                    "warn"
                )
        threading.Thread(target=run_check, daemon=True).start()

    act_update = QAction("🔄 Nach Updates suchen", tray_menu)
    act_update.triggered.connect(manual_check_updates)
    tray_menu.addAction(act_update)

    act_settings = QAction("⚙️ Einstellungen (HUD / Badge / Pfade)", tray_menu)
    act_settings.triggered.connect(show_settings_dialog)
    tray_menu.addAction(act_settings)

    def open_watch_folder():
        wdir = CONFIG.get("watch_dir") or get_default_watch_dir()
        if os.path.exists(wdir):
            os.startfile(wdir)
        else:
            QMessageBox.information(None, "Ordner nicht gefunden", f"Der Ordner existiert noch nicht:\n{wdir}")

    act_folder = QAction("📂 Medal-Ordner öffnen", tray_menu)
    act_folder.triggered.connect(open_watch_folder)
    tray_menu.addAction(act_folder)

    tray_menu.addSeparator()

    act_exit = QAction("❌ Beenden", tray_menu)
    act_exit.triggered.connect(app.quit)
    tray_menu.addAction(act_exit)

    tray.setContextMenu(tray_menu)
    tray.show()

    badge_str = CONFIG.get("user_badge", "317108")
    tray.showMessage(
        f"LSPD Log Assistent v{CURRENT_VERSION} aktiv!",
        f"Reisepass #{badge_str} geladen. HUD: {CONFIG.get('hud', {}).get('theme', 'Schwarz-Lila')}.",
        QSystemTrayIcon.Information,
        3000
    )

    def initial_fetch():
        c, _ = calculate_zwischenstand()
        if c:
            overlay_signal.update_stats.emit(c)
    threading.Thread(target=initial_fetch, daemon=True).start()

    def auto_check_updates():
        time.sleep(6)
        info = check_remote_version()
        if info and info.get("has_update"):
            log(f"[Updater] Neues Update gefunden: {info.get('version')}")
            overlay_signal.show_update_dialog.emit(info)
    threading.Thread(target=auto_check_updates, daemon=True).start()

    watcher_thread = threading.Thread(target=watch_medal_folder, daemon=True)
    watcher_thread.start()

    midnight_thread = threading.Thread(target=midnight_summary_scheduler, daemon=True)
    midnight_thread.start()

    start_keyboard_listener()

    log(f"[Main] Bereit und aktiv für Badge {badge_str} (v{CURRENT_VERSION}).")
    sys.exit(app.exec())

import traceback

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"[FATAL ERROR] {e}\n{traceback.format_exc()}")
