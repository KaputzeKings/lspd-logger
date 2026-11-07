from window_animator import WindowAnimator
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
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint, QSize
from PySide6.QtGui import QPixmap, QColor, QFont, QFontDatabase, QIcon, QPainter, QAction, QKeyEvent
from pynput import keyboard
from grand_calculator import GrandCalculatorOverlay, load_grandkasten_db

CURRENT_VERSION = "1.5.0"
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

def play_beep(freq=1000, duration=150):
    try:
        cfg = globals().get("CONFIG", {})
        if cfg.get("sound_enabled", True):
            import winsound
            winsound.Beep(freq, duration)
    except Exception:
        pass

def find_data_file(filename):
    candidates = []
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        candidates.append(os.path.join(meipass, filename))
        candidates.append(os.path.join(meipass, '_internal', filename))
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, '_internal', filename))
        candidates.append(os.path.join(exe_dir, filename))
    file_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(file_dir, '_internal', filename))
    candidates.append(os.path.join(file_dir, filename))
    candidates.append(os.path.join(r"C:\Users\theop\.gemini\antigravity\scratch\pd_logger", filename))
    candidates.append(os.path.join(r"C:\Users\theop\.gemini\antigravity\scratch\pd_logger", "_internal", filename))
    candidates.append(os.path.join(r"C:\Users\theop\AppData\Local\Programs\LSPD_Log_Assistent", filename))
    candidates.append(os.path.join(r"C:\Users\theop\AppData\Local\Programs\LSPD_Log_Assistent", "_internal", filename))

    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def create_dot_pixmap(color_hex, size=8):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(color_hex))
    p.setPen(Qt.NoPen)
    p.drawEllipse(0, 0, size, size)
    p.end()
    return pix

def create_dot_icon(color_hex, size=8):
    return QIcon(create_dot_pixmap(color_hex, size))

def init_custom_fonts(app=None):
    font_path = find_data_file("InterVariable.ttf")
    loaded = False
    if font_path and os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id >= 0:
            log(f"[Font] Inter Font erfolgreich geladen: {font_path} (ID: {font_id})")
            loaded = True
        else:
            log(f"[Font] Fehler beim Laden von Inter: {font_path}")
    if app:
        font = QFont("Inter" if loaded else "Segoe UI Variable Text", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        app.setFont(font)
    return "Inter" if loaded else "Segoe UI Variable Text"


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
    "Ember Dark (Velvet Obsidian)": {
        "bg": "#161616",
        "card_bg": "#101012",
        "border": "#262628",
        "accent": "#222226",
        "accent_hover": "#2a2a30",
        "accent_pressed": "#18181a",
        "text": "#ffffff",
        "text_muted": "#71717a",
        "btn_bg": "#18181a",
        "btn_hover": "#222226",
        "thumb_bg": "#0c0c0e"
    },
    "Schwarz-Grau-Weiß (Monochrome)": {
        "bg": "#161616",
        "card_bg": "#101012",
        "border": "#262628",
        "accent": "#222226",
        "accent_hover": "#2a2a30",
        "accent_pressed": "#18181a",
        "text": "#ffffff",
        "text_muted": "#71717a",
        "btn_bg": "#18181a",
        "btn_hover": "#222226",
        "thumb_bg": "#0c0c0e"
    },
    "Grandkasten Cyberpunk": {
        "bg": "#0a0a0c",
        "card_bg": "#13141a",
        "border": "#00d2ff",
        "accent": "#0077b6",
        "accent_hover": "#00d2ff",
        "accent_pressed": "#023e8a",
        "text": "#f3f4f6",
        "text_muted": "#94a3b8",
        "btn_bg": "#181820",
        "btn_hover": "#22222c",
        "thumb_bg": "#050505"
    },
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
    theme_name = hud_conf.get("theme", "Ember Dark (Velvet Obsidian)")
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
        "sound_enabled": True,
        "prompter_seconds": 3,
        "calc_scale": 0.82,
        "calc_theme": "Ember Dark (Velvet Obsidian)",
        "log_titles": {
            "Inhaftierung": "{nr}. Inhaftierung",
            "Global": "{nr}. Global",
            "Local": "{nr}. Local",
            "Event": "{nr}. Event",
            "Shoprob": "{nr}. Shoprob",
            "FZ Raid": "{nr}. FZ-Raid",
            "Streifenpartner": "{nr}. Streifenpartner"
        },
        "log_style": {
            "bold": False,
            "underline": False,
            "italic": False
        },
        "counter_overrides": {},
        "hud": {
            "theme": "Ember Dark (Velvet Obsidian)",
            "scale": 1.0,
            "position": "Oben Rechts",
            "font_family": "Inter",
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
                if "log_titles" in loaded and isinstance(loaded["log_titles"], dict):
                    config["log_titles"] = {**get_default_config()["log_titles"], **loaded["log_titles"]}
                if "log_style" in loaded and isinstance(loaded["log_style"], dict):
                    config["log_style"] = {**get_default_config()["log_style"], **loaded["log_style"]}
                if "counter_overrides" in loaded and isinstance(loaded["counter_overrides"], dict):
                    config["counter_overrides"] = loaded["counter_overrides"]
        except Exception as e:
            log(f"[Config Load Error] {e}")
    else:
        save_config(config)
    return config

def format_log_title_for_discord(cat_key, base_title, num, config=None):
    cfg = config or CONFIG
    titles = cfg.get("log_titles", {})
    default_tmpl = f"{{nr}}. {base_title}"
    tmpl = titles.get(cat_key, default_tmpl).strip()
    if not tmpl:
        tmpl = default_tmpl

    if "{nr}" in tmpl:
        text = tmpl.replace("{nr}", str(num))
    else:
        text = f"{num}. {tmpl}"

    style = cfg.get("log_style", {})
    is_italic = bool(style.get("italic", False))
    is_bold = bool(style.get("bold", False))
    is_underline = bool(style.get("underline", False))

    if is_italic and is_bold:
        text = f"***{text}***"
    elif is_bold:
        text = f"**{text}**"
    elif is_italic:
        text = f"*{text}*"

    if is_underline:
        text = f"__{text}__"

    return text

def delete_last_discord_log(token=None, thread_id=None):
    if not token:
        token = get_discord_token()
    if not token:
        return False, "Kein Discord Token gefunden"
    if not thread_id:
        thread_id = get_active_thread_id(token)
    if not thread_id:
        return False, "Kein Forum-Thread gefunden"

    headers = {"Authorization": token}
    try:
        r_me = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=6)
        my_id = r_me.json().get("id") if r_me.status_code == 200 else None
    except Exception:
        my_id = None

    url = f"https://discord.com/api/v9/channels/{thread_id}/messages?limit=25"
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code != 200:
            return False, f"Fehler {res.status_code} beim Abrufen der Nachrichten"
        
        msgs = res.json()
        target_msg = None
        for m in msgs:
            if my_id and m.get("author", {}).get("id") != my_id:
                continue
            content = m.get("content", "")
            if "Zwischenstand:" in content or "Uprank-Punktesystem" in content:
                continue
            has_media = bool(m.get("attachments")) or ("http://" in content or "https://" in content)
            if has_media:
                target_msg = m
                break

        if not target_msg:
            return False, "Kein eigener Log-Post im Thread gefunden"

        msg_id = target_msg.get("id")
        content_preview = target_msg.get("content", "Log-Eintrag")
        del_url = f"https://discord.com/api/v9/channels/{thread_id}/messages/{msg_id}"
        del_res = requests.delete(del_url, headers=headers, timeout=8)
        
        if del_res.status_code in (200, 204):
            return True, content_preview
        else:
            return False, f"Discord API Fehler {del_res.status_code}"
    except Exception as e:
        return False, str(e)

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

def extract_kw_number(thread_name):
    """
    Extrahiert die Kalenderwoche (KW) aus dem Thread-Namen im Discord-Forum.
    Beispiele:
      'KW 46 I Justin Liebermann I 317108' -> 46
      'KW45 | Justin Liebermann' -> 45
      'Kalenderwoche 47' -> 47
    Gibt int >= 0 zurueck, sonst -1.
    """
    if not thread_name:
        return -1
    m = re.search(r'(?:kw|kalenderwoche)\s*[:#-]?\s*(\d+)', thread_name, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return -1

_cached_thread_info = {"id": None, "time": 0, "badge": None, "name": "", "kw": -1}

def get_active_thread_id(token, badge=None, thread_override=None, force_refresh=False):
    if thread_override and thread_override.strip():
        return thread_override.strip()
    manual_thread = CONFIG.get("thread_id", "").strip()
    if manual_thread:
        return manual_thread

    badge = str(badge or CONFIG.get("user_badge", "")).strip()
    now = time.time()
    if not force_refresh and _cached_thread_info["id"] and _cached_thread_info["badge"] == badge:
        if now - _cached_thread_info["time"] < 45:
            return _cached_thread_info["id"]

    forum_channel = CONFIG.get("forum_channel_id", "1551241898340122756").strip()
    headers = {'Authorization': token}
    candidates = {}

    # 1. Gezielte Suche nach Badge im Forum
    if badge:
        try:
            url = f'https://discord.com/api/v9/channels/{forum_channel}/threads/search?name={badge}'
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                for t in res.json().get('threads', []):
                    if badge in t.get('name', ''):
                        candidates[t['id']] = t
        except Exception as e:
            log(f"[Thread Search by Badge Error] {e}")

    # 2. Ergaenzende Suche nach aktiven Threads
    try:
        url = f'https://discord.com/api/v9/channels/{forum_channel}/threads/search?sort_by=last_message_time&sort_order=desc'
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            for t in res.json().get('threads', []):
                if badge and badge in t.get('name', ''):
                    candidates[t['id']] = t
    except Exception as e:
        log(f"[Thread Search Fallback Error] {e}")

    if candidates:
        # Sortiere strikt nach:
        # 1. Hoechste Kalenderwoche (KW-Nummer z.B. 46 > 45 > 44)
        # 2. Nicht archiviert (aktive Threads bevorzugen)
        # 3. Neueste Discord Snowflake ID (Erstellungszeitpunkt)
        sorted_threads = sorted(
            candidates.values(),
            key=lambda t: (
                extract_kw_number(t.get('name', '')),
                not t.get('thread_metadata', {}).get('archived', False),
                int(t.get('id', 0))
            ),
            reverse=True
        )

        chosen = sorted_threads[0]
        kw = extract_kw_number(chosen.get('name', ''))
        kw_label = f"KW {kw}" if kw >= 0 else "Keine KW"

        if _cached_thread_info["id"] != chosen['id']:
            log(f"[Thread Finder] Aktives Logbuch gewaehlt ({kw_label}, hoechste KW): '{chosen.get('name')}' (ID: {chosen.get('id')})")

        _cached_thread_info["id"] = chosen['id']
        _cached_thread_info["time"] = now
        _cached_thread_info["badge"] = badge
        _cached_thread_info["name"] = chosen.get('name', '')
        _cached_thread_info["kw"] = kw
        return chosen['id']

    if _cached_thread_info["id"] and _cached_thread_info["badge"] == badge:
        return _cached_thread_info["id"]

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
        detailed_counts = {
            'Inhaftierung': 0,
            'Global': 0,
            'Local': 0,
            'Event': 0,
            'Shoprob': 0,
            'FZ Raid': 0,
            'Streifenpartner': 0
        }
        highest_prefix = {k: 0 for k in detailed_counts}

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
            clean_text = clean.replace('*', '').replace('_', '').replace('~', '').replace('#', '').strip()
            match_num = re.match(r'^([0-9]+)\s*[\.\-\)]?\s*(.*)', clean_text)
            prefix_num = int(match_num.group(1)) if match_num else 0

            if 'event' in clean:
                counts['Events'] += 1
                detailed_counts['Event'] += 1
                if prefix_num > highest_prefix['Event']:
                    highest_prefix['Event'] = prefix_num
            elif 'fz' in clean or 'fort zancudo' in clean:
                counts['FZ-Raid'] += 1
                detailed_counts['FZ Raid'] += 1
                if prefix_num > highest_prefix['FZ Raid']:
                    highest_prefix['FZ Raid'] = prefix_num
            elif any(k in clean for k in ['shop', 'ammu', 'geisel']):
                counts['Shoprob etc.'] += 1
                detailed_counts['Shoprob'] += 1
                if prefix_num > highest_prefix['Shoprob']:
                    highest_prefix['Shoprob'] = prefix_num
            elif 'inhaftierung' in clean or 'knast' in clean or 'sg' in clean or re.search(r'\binh\b', clean) or clean.startswith('inh'):
                counts['Inhaftierungen'] += 1
                detailed_counts['Inhaftierung'] += 1
                if prefix_num > highest_prefix['Inhaftierung']:
                    highest_prefix['Inhaftierung'] = prefix_num
            elif any(k in clean for k in ['streifenpartner', 'partner', 'rookie']):
                counts['Streifenpartner'] += 1
                detailed_counts['Streifenpartner'] += 1
                if prefix_num > highest_prefix['Streifenpartner']:
                    highest_prefix['Streifenpartner'] = prefix_num
            elif 'global' in clean or re.search(r'\bgl\b', clean):
                counts['GL/LO'] += 1
                detailed_counts['Global'] += 1
                if prefix_num > highest_prefix['Global']:
                    highest_prefix['Global'] = prefix_num
            elif 'local' in clean or re.search(r'\blo\b', clean):
                counts['GL/LO'] += 1
                detailed_counts['Local'] += 1
                if prefix_num > highest_prefix['Local']:
                    highest_prefix['Local'] = prefix_num

        next_numbers = {}
        overrides = CONFIG.get("counter_overrides", {})
        for cat in detailed_counts:
            cnt = detailed_counts[cat]
            pref = highest_prefix.get(cat, 0)
            # Schutz: Wenn eine Nachricht alte Nummern aus einer vorherigen Woche enthaelt (z.B. 17 bei nur 2 Logs),
            # darf sie die Zaehlung der aktuellen Woche nicht ruinieren.
            if pref > 0 and pref <= cnt + 1:
                base_num = max(cnt, pref)
            else:
                base_num = cnt
            auto_next = base_num + 1

            if cat in overrides:
                try:
                    ov = int(overrides[cat])
                    if ov > 0:
                        next_numbers[cat] = ov
                        continue
                except (ValueError, TypeError):
                    pass

            next_numbers[cat] = auto_next

        counts['next_numbers'] = next_numbers
        counts['detailed_counts'] = detailed_counts

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
    primary = QApplication.primaryScreen()
    if primary:
        avail = primary.availableGeometry()
    else:
        avail = None

    avail_x = avail.x() if avail else 0
    avail_y = avail.y() if avail else 0
    avail_w = avail.width() if avail else 1920
    avail_h = avail.height() if avail else 1080

    base_w = 415
    base_h = 595
    w = int(base_w * scale)
    h = int(base_h * scale)

    # Adaptive limits: Overlay never exceeds available screen space on small resolutions (e.g. 720p/1366x768)
    w = min(w, max(260, avail_w - 30))
    h = min(h, max(380, avail_h - 30))

    margin_x = 30
    margin_y = 35

    if position == "Oben Links":
        x = avail_x + margin_x
        y = avail_y + margin_y
    elif position == "Unten Rechts":
        x = avail_x + avail_w - w - margin_x
        y = avail_y + avail_h - h - margin_y
    elif position == "Unten Links":
        x = avail_x + margin_x
        y = avail_y + avail_h - h - margin_y
    elif position == "Mitte":
        x = avail_x + (avail_w - w) // 2
        y = avail_y + (avail_h - h) // 2
    else: # Oben Rechts
        x = avail_x + avail_w - w - margin_x
        y = avail_y + margin_y

    # Safe clamp within available screen geometry
    x = max(avail_x, min(x, avail_x + avail_w - w))
    y = max(avail_y, min(y, avail_y + avail_h - h))

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
    toggle_prompter = Signal()

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

        title = QLabel(f"<span style='color: #ffffff; font-size: 15px;'><b>Neues Update verfügbar</b></span>")
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

# Full Customizable Grandkasten Setup Dialog with Pure Monochrome Design (Schwarz-Weiß-Grau)
class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LSPD Dienst-Assistent - Einstellungen")
        self.setFixedSize(720, 680)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowOpacity(0.0)
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, '_anim_opened', False):
            self._anim_opened = True
            WindowAnimator.animate_open(self, target_opacity=1.0, duration=170, slide_distance=12)

    def reject(self):
        if getattr(self, '_is_animating_close', False):
            return
        WindowAnimator.animate_close(self, on_finished=lambda: super(SetupDialog, self).reject(), duration=130, slide_distance=8)

    def _create_card(self, title_text, subtitle_text=""):
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(6)

        header = QLabel(
            f"<span style='color: #ffffff; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;'>{title_text}</span> "
            f"<span style='color: #888888; font-size: 10px; font-weight: normal;'>{subtitle_text}</span>"
        )
        card_layout.addWidget(header)
        return card, card_layout

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0c0c0e;
                border: 1px solid #23232b;
                border-radius: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #23232b;
                background: #101014;
                border-radius: 12px;
                top: 6px;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
            QTabBar::tab {
                background: #141418;
                color: #71717a;
                padding: 8px 18px;
                border-radius: 9px;
                font-weight: 600;
                font-size: 11px;
                margin-right: 6px;
                border: 1px solid #23232b;
            }
            QTabBar::tab:selected {
                background: #212128;
                color: #ffffff;
                border: 1px solid #383848;
                font-weight: 700;
            }
            QTabBar::tab:hover:!selected {
                background: #181820;
                color: #d4d4d8;
                border-color: #2c2c36;
            }
            QFrame#cardFrame {
                background-color: #141418;
                border: 1px solid #22222a;
                border-radius: 12px;
            }
            QLabel {
                color: #e4e4e7;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#hintLabel {
                color: #71717a;
                font-size: 10px;
                font-weight: normal;
            }
            QLineEdit, QComboBox {
                background-color: #111114;
                color: #ffffff;
                border: 1px solid #23232b;
                border-radius: 8px;
                padding: 7px 11px;
                font-size: 11px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
                background-color: #14141b;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #23232b;
            }
            QComboBox QAbstractItemView {
                background-color: #141418;
                color: #ffffff;
                selection-background-color: #212128;
                selection-color: #ffffff;
                border: 1px solid #2a2a34;
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton {
                background-color: #16161b;
                color: #d4d4d8;
                border: 1px solid #23232b;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #212128;
                color: #ffffff;
                border: 1px solid #383848;
            }
            QPushButton#btnSave {
                background-color: #4bd4a3;
                color: #0c0c0e;
                border: 1px solid #4bd4a3;
                border-radius: 8px;
                padding: 9px 24px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnSave:hover {
                background-color: #34d399;
                border-color: #34d399;
            }
            QPushButton#btnCancel {
                background-color: #141418;
                color: #71717a;
                border: 1px solid #23232b;
                border-radius: 8px;
                padding: 9px 18px;
                font-size: 12px;
            }
            QPushButton#btnCancel:hover {
                background-color: #1a1a20;
                color: #d4d4d8;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1c1c22;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #3b82f6;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QCheckBox {
                color: #f4f4f5;
                font-size: 11px;
                font-weight: 600;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border: 1px solid #2a2a34;
                border-radius: 5px;
                background: #111114;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background: #10b981;
                border: 1px solid #4bd4a3;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Header Title (Pure Monochrome)
        title_bar = QHBoxLayout()
        title_lbl = QLabel(
            "<span style='color: #ffffff; font-size: 14px;'><b>LSPD</b> <span style='font-weight: 500; color: #a1a1aa;'>Einstellungen</span></span> "
            "<span style='color: #52525b; font-size: 11px; font-weight: normal;'>• Velvet Obsidian</span>"
        )
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        version_lbl = QLabel(f"<span style='color: #888888; font-size: 10px; font-weight: bold;'>v{CURRENT_VERSION}</span>")
        title_bar.addWidget(version_lbl)
        layout.addLayout(title_bar)

        self.tabs = QTabWidget()

        # ==================== TAB 1: Dienst & Discord ====================
        tab_service = QWidget()
        l_serv = QVBoxLayout(tab_service)
        l_serv.setContentsMargins(12, 12, 12, 12)
        l_serv.setSpacing(10)

        # Card 1: Beamten-Profil
        c1, c1_lay = self._create_card("Beamten-Profil & Dienstnummer", "Wichtig für Protokolle")
        c1_lay.addWidget(QLabel("Reisepassnummer / Badge-ID:"))
        self.badge_input = QLineEdit()
        self.badge_input.setPlaceholderText("z. B. 317595")
        self.badge_input.setText(str(CONFIG.get("user_badge", "")))
        c1_lay.addWidget(self.badge_input)
        h1 = QLabel("Wird für deine automatischen Arrest-Logs, Bußgeld-Akten und Funkmeldungen verwendet.")
        h1.setObjectName("hintLabel")
        c1_lay.addWidget(h1)
        l_serv.addWidget(c1)

        # Card 2: Screenshot Überwachung
        c2, c2_lay = self._create_card("Medal Screenshot-Ordner", "Lokale Überwachung")
        c2_lay.addWidget(QLabel("Überwachter Ordner für Logs & Berechnungen:"))
        dir_lay = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(CONFIG.get("watch_dir", get_default_watch_dir()))
        dir_lay.addWidget(self.dir_input)
        browse_btn = QPushButton("Durchsuchen")
        browse_btn.clicked.connect(self.choose_directory)
        dir_lay.addWidget(browse_btn)
        c2_lay.addLayout(dir_lay)
        h2 = QLabel("Standard: Medal Clips oder GTA V Screenshot-Ordner (automatischer Upload bei neuem Bild).")
        h2.setObjectName("hintLabel")
        c2_lay.addWidget(h2)
        l_serv.addWidget(c2)

        # Card 3: Discord Forum
        c3, c3_lay = self._create_card("Discord Forum-Thread", "Server-Synchronisation")
        c3_lay.addWidget(QLabel("Forum Thread-ID (Optional):"))
        self.thread_input = QLineEdit()
        self.thread_input.setPlaceholderText("Leer lassen für automatische Erkennung (höchste KW)")
        self.thread_input.setText(CONFIG.get("thread_id", ""))
        c3_lay.addWidget(self.thread_input)
        
        kw_hint = QLabel("<span style='color: #888888; font-size: 10px; font-weight: normal;'>"
                         "<b>Automatisches Logbuch:</b> Das System wählt immer automatisch das Logbuch mit der <b>höchsten Kalenderwoche (KW)</b>. "
                         "Jeden Samstag kannst du einfach dein neues Logbuch (z.B. KW 46) erstellen – der Assistent wechselt sofort nahtlos.</span>")
        kw_hint.setStyleSheet("border: none; margin-top: 2px;")
        kw_hint.setWordWrap(True)
        c3_lay.addWidget(kw_hint)
        
        token_box = QFrame()
        token_box.setStyleSheet("background: #111111; border: 1px solid #242424; border-radius: 5px; padding: 6px;")
        tb_lay = QHBoxLayout(token_box)
        tb_lay.setContentsMargins(8, 4, 8, 4)
        t_ico = QLabel("<span style='color: #4bd4a3;'>●</span>")
        t_ico.setStyleSheet("font-size: 14px; border: none;")
        tb_lay.addWidget(t_ico)
        t_lbl = QLabel("<span style='color: #888888; font-size: 10px; font-weight: normal;'>"
                       "<b>Discord-Token:</b> Wird automatisch und sicher aus deiner Desktop-App gelesen. "
                       "Keine manuelle Eingabe erforderlich.</span>")
        t_lbl.setStyleSheet("border: none;")
        tb_lay.addWidget(t_lbl, 1)
        c3_lay.addWidget(token_box)
        l_serv.addWidget(c3)

        l_serv.addStretch()
        self.tabs.addTab(tab_service, "Dienst & Discord")

        # ==================== TAB 2: Log-Beschriftung & Stil ====================
        tab_formatting = QWidget()
        l_form = QVBoxLayout(tab_formatting)
        l_form.setContentsMargins(12, 12, 12, 12)
        l_form.setSpacing(10)

        # Card 1: Schriftstil (Markdown)
        cf1, cf1_lay = self._create_card("Discord Schriftstil beim Senden", "Markdown-Formatierung")
        style_cfg = CONFIG.get("log_style", {})
        
        chk_lay = QHBoxLayout()
        chk_lay.setSpacing(16)
        self.cb_bold = QCheckBox("Fett (**Text**)")
        self.cb_bold.setChecked(style_cfg.get("bold", False))
        self.cb_bold.stateChanged.connect(self._update_style_preview)
        chk_lay.addWidget(self.cb_bold)

        self.cb_underline = QCheckBox("Unterstrichen (__Text__)")
        self.cb_underline.setChecked(style_cfg.get("underline", False))
        self.cb_underline.stateChanged.connect(self._update_style_preview)
        chk_lay.addWidget(self.cb_underline)

        self.cb_italic = QCheckBox("Kursiv (*Text*)")
        self.cb_italic.setChecked(style_cfg.get("italic", False))
        self.cb_italic.stateChanged.connect(self._update_style_preview)
        chk_lay.addWidget(self.cb_italic)
        chk_lay.addStretch()
        cf1_lay.addLayout(chk_lay)

        # Live Preview Box
        preview_box = QFrame()
        preview_box.setStyleSheet("background: #0d0d0d; border: 1px solid #333333; border-radius: 5px; padding: 8px;")
        pv_lay = QHBoxLayout(preview_box)
        pv_lay.setContentsMargins(8, 4, 8, 4)
        pv_ico = QLabel("<span style='color: #5ea2ef;'>●</span>")
        pv_ico.setStyleSheet("font-size: 14px; border: none;")
        pv_lay.addWidget(pv_ico)
        self.lbl_style_preview = QLabel()
        self.lbl_style_preview.setStyleSheet("border: none; font-size: 12px;")
        pv_lay.addWidget(self.lbl_style_preview, 1)
        cf1_lay.addWidget(preview_box)
        l_form.addWidget(cf1)

        # Card 2: Titel-Vorlagen & Zähler der Kategorien
        cf2, cf2_lay = self._create_card("Log-Beschriftungen & Zähler-Steuerung", "{nr} = Zähler | Nr = Manuelle nächste Zahl")
        h_tmpl = QLabel("Verwende <b>{nr}</b> für die fortlaufende Nummer. Unter <b>Nächste Nr.</b> kannst du den Zähler bei Bedarf manuell anpassen (leer lassen für vollautomatische Zählung aus dem Wochen-Logbuch).")
        h_tmpl.setObjectName("hintLabel")
        h_tmpl.setWordWrap(True)
        cf2_lay.addWidget(h_tmpl)

        titles_cfg = CONFIG.get("log_titles", {})
        ov_cfg = CONFIG.get("counter_overrides", {})
        
        t_grid = QGridLayout()
        t_grid.setHorizontalSpacing(12)
        t_grid.setVerticalSpacing(6)

        t_grid.addWidget(QLabel("<span style='color: #888888; font-size: 10px; font-weight: bold;'>KATEGORIE</span>"), 0, 0)
        t_grid.addWidget(QLabel("<span style='color: #888888; font-size: 10px; font-weight: bold;'>DISCORD-VORLAGE</span>"), 0, 1)
        t_grid.addWidget(QLabel("<span style='color: #888888; font-size: 10px; font-weight: bold;'>NÄCHSTE NR.</span>"), 0, 2)

        def _make_num_inp(cat_k):
            inp = QLineEdit()
            inp.setFixedWidth(65)
            inp.setPlaceholderText("Auto")
            cur = ov_cfg.get(cat_k, "")
            inp.setText(str(cur) if cur else "")
            return inp

        t_grid.addWidget(QLabel("<span style='color: #4bd4a3;'>●</span> Inhaftierung:"), 1, 0)
        self.title_inh = QLineEdit()
        self.title_inh.setText(titles_cfg.get("Inhaftierung", "{nr}. Inhaftierung"))
        self.title_inh.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_inh, 1, 1)
        self.override_inh = _make_num_inp("Inhaftierung")
        t_grid.addWidget(self.override_inh, 1, 2)

        t_grid.addWidget(QLabel("<span style='color: #ef4444;'>●</span> Global:"), 2, 0)
        self.title_global = QLineEdit()
        self.title_global.setText(titles_cfg.get("Global", "{nr}. Global"))
        self.title_global.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_global, 2, 1)
        self.override_global = _make_num_inp("Global")
        t_grid.addWidget(self.override_global, 2, 2)

        t_grid.addWidget(QLabel("<span style='color: #5ea2ef;'>●</span> Local:"), 3, 0)
        self.title_local = QLineEdit()
        self.title_local.setText(titles_cfg.get("Local", "{nr}. Local"))
        self.title_local.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_local, 3, 1)
        self.override_local = _make_num_inp("Local")
        t_grid.addWidget(self.override_local, 3, 2)

        t_grid.addWidget(QLabel("<span style='color: #a87ffb;'>●</span> Event:"), 4, 0)
        self.title_event = QLineEdit()
        self.title_event.setText(titles_cfg.get("Event", "{nr}. Event"))
        self.title_event.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_event, 4, 1)
        self.override_event = _make_num_inp("Event")
        t_grid.addWidget(self.override_event, 4, 2)

        t_grid.addWidget(QLabel("<span style='color: #f7bd2e;'>●</span> Shoprob:"), 5, 0)
        self.title_shoprob = QLineEdit()
        self.title_shoprob.setText(titles_cfg.get("Shoprob", "{nr}. Shoprob"))
        self.title_shoprob.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_shoprob, 5, 1)
        self.override_shoprob = _make_num_inp("Shoprob")
        t_grid.addWidget(self.override_shoprob, 5, 2)

        t_grid.addWidget(QLabel("<span style='color: #2dd4bf;'>●</span> FZ-Raid:"), 6, 0)
        self.title_fz = QLineEdit()
        self.title_fz.setText(titles_cfg.get("FZ Raid", "{nr}. FZ-Raid"))
        self.title_fz.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_fz, 6, 1)
        self.override_fz = _make_num_inp("FZ Raid")
        t_grid.addWidget(self.override_fz, 6, 2)

        t_grid.addWidget(QLabel("<span style='color: #ec5ba3;'>●</span> Streifenpartner:"), 7, 0)
        self.title_partner = QLineEdit()
        self.title_partner.setText(titles_cfg.get("Streifenpartner", "{nr}. Streifenpartner"))
        self.title_partner.textChanged.connect(self._update_style_preview)
        t_grid.addWidget(self.title_partner, 7, 1)
        self.override_partner = _make_num_inp("Streifenpartner")
        t_grid.addWidget(self.override_partner, 7, 2)

        cf2_lay.addLayout(t_grid)

        btn_reset_titles = QPushButton("Beschriftungen & Zähler auf Automatik zurücksetzen")
        btn_reset_titles.clicked.connect(self._reset_titles_to_defaults)
        cf2_lay.addWidget(btn_reset_titles)

        l_form.addWidget(cf2)
        l_form.addStretch()
        self.tabs.addTab(tab_formatting, "Log-Beschriftung & Stil")

        # ==================== TAB 3: Grandkasten Rechner & F10 ====================
        tab_calc = QWidget()
        l_calc = QVBoxLayout(tab_calc)
        l_calc.setContentsMargins(12, 12, 12, 12)
        l_calc.setSpacing(10)

        # Card 1: F12 Dienst-Rechner
        cc1, cc1_lay = self._create_card("F12 Dienst-Rechner", "Grandkasten DE1 Bußgeld & Wanted Rechner")
        
        calc_grid = QGridLayout()
        calc_grid.setHorizontalSpacing(14)
        calc_grid.setVerticalSpacing(8)

        calc_grid.addWidget(QLabel("F12 Rechner Design-Theme:"), 0, 0)
        self.calc_theme_combo = QComboBox()
        self.calc_theme_combo.addItems([
            "Ember Dark (Velvet Obsidian)",
            "Schwarz-Grau-Weiß (Monochrome)",
            "Grandkasten Cyberpunk",
            "Schwarz-Lila (Standard)",
            "LSPD Cyber Blue",
            "Tactical Stealth Red",
            "Emerald Special Forces"
        ])
        curr_ct = CONFIG.get("calc_theme", "Schwarz-Grau-Weiß (Monochrome)")
        c_idx = self.calc_theme_combo.findText(curr_ct)
        if c_idx >= 0:
            self.calc_theme_combo.setCurrentIndex(c_idx)
        calc_grid.addWidget(self.calc_theme_combo, 0, 1)

        calc_grid.addWidget(QLabel("F12 Fenstergröße / Skalierung:"), 1, 0)
        self.calc_scale_combo = QComboBox()
        self.calc_scale_combo.addItem("Mini (25% - 1 Spalte)", 0.25)
        self.calc_scale_combo.addItem("Halb (50% - 2 Spalten)", 0.50)
        self.calc_scale_combo.addItem("Kompakt (75% - 3 Spalten)", 0.75)
        self.calc_scale_combo.addItem("Standard (82% - 3 Spalten)", 0.82)
        self.calc_scale_combo.addItem("Groß (88%)", 0.88)
        self.calc_scale_combo.addItem("Sehr groß (95%)", 0.95)
        self.calc_scale_combo.addItem("Vollbild (100%)", 1.00)
        c_scale = float(CONFIG.get("calc_scale", 0.82))
        for i in range(self.calc_scale_combo.count()):
            if abs(self.calc_scale_combo.itemData(i) - c_scale) < 0.02:
                self.calc_scale_combo.setCurrentIndex(i)
                break
        calc_grid.addWidget(self.calc_scale_combo, 1, 1)

        cc1_lay.addLayout(calc_grid)
        hc1 = QLabel("Tipp: Du kannst die Größe auch direkt im geöffneten F12-Rechner oben rechts per Dropdown umschalten.")
        hc1.setObjectName("hintLabel")
        cc1_lay.addWidget(hc1)
        l_calc.addWidget(cc1)

        # Card 2: F10 Teleprompter
        cc2, cc2_lay = self._create_card("F10 Teleprompter & Rechte", "Automatische Miranda-Warnung")
        
        promp_grid = QGridLayout()
        promp_grid.setHorizontalSpacing(14)
        promp_grid.setVerticalSpacing(8)

        promp_grid.addWidget(QLabel("Teleprompter Seiten-Takt:"), 0, 0)
        self.prompter_speed_combo = QComboBox()
        self.prompter_speed_combo.addItem("3 Sekunden (Empfohlen)", 3)
        self.prompter_speed_combo.addItem("4 Sekunden", 4)
        self.prompter_speed_combo.addItem("5 Sekunden", 5)
        self.prompter_speed_combo.addItem("6 Sekunden", 6)
        self.prompter_speed_combo.addItem("7 Sekunden", 7)
        self.prompter_speed_combo.addItem("8 Sekunden", 8)
        self.prompter_speed_combo.addItem("9 Sekunden", 9)
        self.prompter_speed_combo.addItem("10 Sekunden (Langsam)", 10)
        curr_ps = int(CONFIG.get("prompter_seconds", 3))
        for i in range(self.prompter_speed_combo.count()):
            if self.prompter_speed_combo.itemData(i) == curr_ps:
                self.prompter_speed_combo.setCurrentIndex(i)
                break
        promp_grid.addWidget(self.prompter_speed_combo, 0, 1)
        cc2_lay.addLayout(promp_grid)

        auto_box = QFrame()
        auto_box.setStyleSheet("background: #111111; border: 1px solid #242424; border-radius: 5px; padding: 6px;")
        ab_lay = QHBoxLayout(auto_box)
        ab_lay.setContentsMargins(8, 4, 8, 4)
        ab_ico = QLabel("<span style='color: #f7bd2e;'>●</span>")
        ab_ico.setStyleSheet("font-size: 14px; border: none;")
        ab_lay.addWidget(ab_ico)
        ab_lbl = QLabel("<span style='color: #888888; font-size: 10px; font-weight: normal;'>"
                        "<b>Automatische Rechte:</b> Nach Druck auf [F10] wechselt der Teleprompter alle eingestellten Sekunden "
                        "automatisch zur nächsten Seite und schließt sich nach dem Durchlauf selbstständig.</span>")
        ab_lbl.setStyleSheet("border: none;")
        ab_lay.addWidget(ab_lbl, 1)
        cc2_lay.addWidget(auto_box)
        l_calc.addWidget(cc2)

        l_calc.addStretch()
        self.tabs.addTab(tab_calc, "Grandkasten Rechner & F10")

        # ==================== TAB 4: Ingame-HUD & Audio ====================
        tab_hud = QWidget()
        l_hud = QVBoxLayout(tab_hud)
        l_hud.setContentsMargins(12, 12, 12, 12)
        l_hud.setSpacing(10)

        hud_conf = CONFIG.get("hud", {})

        # Card 1: Ingame HUD
        ch1, ch1_lay = self._create_card("Ingame Stats-HUD (Overlay)", "Live-Anzeige im Spiel")
        
        hud_grid = QGridLayout()
        hud_grid.setHorizontalSpacing(14)
        hud_grid.setVerticalSpacing(8)

        hud_grid.addWidget(QLabel("HUD Farb-Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        theme_names = list(THEMES.keys()) + ["Benutzerdefiniert"]
        self.theme_combo.addItems(theme_names)
        curr_theme = hud_conf.get("theme", "Schwarz-Grau-Weiß (Monochrome)")
        idx = self.theme_combo.findText(curr_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        hud_grid.addWidget(self.theme_combo, 0, 1)

        # Custom colors
        hud_grid.addWidget(QLabel("Farben (Benutzerdefiniert):"), 1, 0)
        custom_row = QHBoxLayout()
        self.btn_bg_color = QPushButton("Hintergrund")
        self.btn_bg_color.clicked.connect(self.pick_bg_color)
        custom_row.addWidget(self.btn_bg_color)
        self.btn_accent_color = QPushButton("Akzent/Border")
        self.btn_accent_color.clicked.connect(self.pick_accent_color)
        custom_row.addWidget(self.btn_accent_color)
        self.btn_text_color = QPushButton("Textfarbe")
        self.btn_text_color.clicked.connect(self.pick_text_color)
        custom_row.addWidget(self.btn_text_color)
        hud_grid.addLayout(custom_row, 1, 1)

        self.custom_bg = hud_conf.get("custom_bg", "#0a0a0a")
        self.custom_accent = hud_conf.get("custom_accent", "#555555")
        self.custom_text = hud_conf.get("custom_text", "#ffffff")

        hud_grid.addWidget(QLabel("Bildschirm-Position:"), 2, 0)
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(["Oben Rechts", "Oben Links", "Unten Rechts", "Unten Links", "Mitte"])
        self.pos_combo.setCurrentText(hud_conf.get("position", "Oben Rechts"))
        hud_grid.addWidget(self.pos_combo, 2, 1)

        hud_grid.addWidget(QLabel("HUD-Skalierung:"), 3, 0)
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
        hud_grid.addWidget(self.scale_combo, 3, 1)

        hud_grid.addWidget(QLabel("Schriftart & Schriftgröße:"), 4, 0)
        f_row = QHBoxLayout()
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Bahnschrift", "Roboto", "Montserrat", "Arial", "Consolas"])
        curr_font = hud_conf.get("font_family", "Segoe UI")
        f_idx = self.font_combo.findText(curr_font)
        if f_idx >= 0:
            self.font_combo.setCurrentIndex(f_idx)
        f_row.addWidget(self.font_combo, 2)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItem("10pt", 10)
        self.font_size_combo.addItem("11pt", 11)
        self.font_size_combo.addItem("12pt", 12)
        self.font_size_combo.addItem("13pt", 13)
        curr_fsize = int(hud_conf.get("font_size", 11))
        for i in range(self.font_size_combo.count()):
            if self.font_size_combo.itemData(i) == curr_fsize:
                self.font_size_combo.setCurrentIndex(i)
                break
        f_row.addWidget(self.font_size_combo, 1)
        hud_grid.addLayout(f_row, 4, 1)

        hud_grid.addWidget(QLabel("Transparenz / Deckkraft:"), 5, 0)
        op_lay = QHBoxLayout()
        self.op_slider = QSlider(Qt.Horizontal)
        self.op_slider.setRange(75, 100)
        curr_op = int(float(hud_conf.get("opacity", 0.96)) * 100)
        self.op_slider.setValue(curr_op)
        self.op_label = QLabel(f"{curr_op}%")
        self.op_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 38px;")
        self.op_slider.valueChanged.connect(lambda v: self.op_label.setText(f"{v}%"))
        op_lay.addWidget(self.op_slider)
        op_lay.addWidget(self.op_label)
        hud_grid.addLayout(op_lay, 5, 1)

        ch1_lay.addLayout(hud_grid)
        l_hud.addWidget(ch1)

        # Card 2: Audio & Feedback
        ch2, ch2_lay = self._create_card("Akustik & Feedback", "Soundeffekte")
        self.cb_sound = QCheckBox("Signalton bei Uploads & Rechner-Aktionen abspielen")
        self.cb_sound.setChecked(CONFIG.get("sound_enabled", True))
        ch2_lay.addWidget(self.cb_sound)
        l_hud.addWidget(ch2)

        # Card 3: Preview
        ch3, ch3_lay = self._create_card("Schnell-Test", "Live-Vorschau")
        self.btn_preview = QPushButton("Ingame-HUD Vorschau testen")
        self.btn_preview.clicked.connect(self.trigger_hud_preview)
        ch3_lay.addWidget(self.btn_preview)
        l_hud.addWidget(ch3)

        l_hud.addStretch()
        self.tabs.addTab(tab_hud, "Ingame-HUD & Audio")

        layout.addWidget(self.tabs)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(10)

        self.save_btn = QPushButton("Einstellungen speichern & anwenden")
        self.save_btn.setObjectName("btnSave")
        self.save_btn.clicked.connect(self.save_and_close)
        bottom_bar.addWidget(self.save_btn, 2)

        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.setObjectName("btnCancel")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_bar.addWidget(self.cancel_btn, 1)

        layout.addLayout(bottom_bar)
        self._update_style_preview()

    def _update_style_preview(self):
        tmpl = self.title_inh.text().strip() or "{nr}. Inhaftierung"
        raw = tmpl.replace("{nr}", "12") if "{nr}" in tmpl else f"12. {tmpl}"
        
        is_b = self.cb_bold.isChecked()
        is_u = self.cb_underline.isChecked()
        is_i = self.cb_italic.isChecked()

        # Build discord representation
        disc = raw
        if is_i and is_b: disc = f"***{disc}***"
        elif is_b: disc = f"**{disc}**"
        elif is_i: disc = f"*{disc}*"
        if is_u: disc = f"__{disc}__"

        # Build HTML styling
        css_styles = []
        if is_b: css_styles.append("font-weight: bold; color: #ffffff;")
        else: css_styles.append("font-weight: normal; color: #dddddd;")
        if is_u: css_styles.append("text-decoration: underline;")
        if is_i: css_styles.append("font-style: italic;")
        
        style_attr = " ".join(css_styles)
        self.lbl_style_preview.setText(
            f"<span style='color: #888888;'>Discord-Vorschau:</span> <span style='{style_attr}'>{raw}</span> "
            f"<span style='color: #666666; font-size: 10px;'>({disc})</span>"
        )

    def _reset_titles_to_defaults(self):
        self.title_inh.setText("{nr}. Inhaftierung")
        self.title_global.setText("{nr}. Global")
        self.title_local.setText("{nr}. Local")
        self.title_event.setText("{nr}. Event")
        self.title_shoprob.setText("{nr}. Shoprob")
        self.title_fz.setText("{nr}. FZ-Raid")
        self.title_partner.setText("{nr}. Streifenpartner")
        for w in [getattr(self, 'override_inh', None), getattr(self, 'override_global', None),
                  getattr(self, 'override_local', None), getattr(self, 'override_event', None),
                  getattr(self, 'override_shoprob', None), getattr(self, 'override_fz', None),
                  getattr(self, 'override_partner', None)]:
            if w:
                w.clear()
        CONFIG["counter_overrides"] = {}
        self._update_style_preview()

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
        if hasattr(self, 'calc_theme_combo'):
            CONFIG["calc_theme"] = self.calc_theme_combo.currentText()
        if hasattr(self, 'prompter_speed_combo'):
            CONFIG["prompter_seconds"] = int(self.prompter_speed_combo.currentData())
        if hasattr(self, 'cb_sound'):
            CONFIG["sound_enabled"] = self.cb_sound.isChecked()

        CONFIG["log_style"] = {
            "bold": self.cb_bold.isChecked(),
            "underline": self.cb_underline.isChecked(),
            "italic": self.cb_italic.isChecked()
        }

        CONFIG["log_titles"] = {
            "Inhaftierung": self.title_inh.text().strip() or "{nr}. Inhaftierung",
            "Global": self.title_global.text().strip() or "{nr}. Global",
            "Local": self.title_local.text().strip() or "{nr}. Local",
            "Event": self.title_event.text().strip() or "{nr}. Event",
            "Shoprob": self.title_shoprob.text().strip() or "{nr}. Shoprob",
            "FZ Raid": self.title_fz.text().strip() or "{nr}. FZ-Raid",
            "Streifenpartner": self.title_partner.text().strip() or "{nr}. Streifenpartner"
        }

        overrides = {}
        for cat, w in [
            ("Inhaftierung", getattr(self, 'override_inh', None)),
            ("Global", getattr(self, 'override_global', None)),
            ("Local", getattr(self, 'override_local', None)),
            ("Event", getattr(self, 'override_event', None)),
            ("Shoprob", getattr(self, 'override_shoprob', None)),
            ("FZ Raid", getattr(self, 'override_fz', None)),
            ("Streifenpartner", getattr(self, 'override_partner', None))
        ]:
            if w:
                txt = w.text().strip()
                if txt.isdigit() and int(txt) > 0:
                    overrides[cat] = int(txt)
        CONFIG["counter_overrides"] = overrides

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
        global _cached_thread_info
        _cached_thread_info = {"id": None, "time": 0, "badge": None, "name": "", "kw": -1}
        log(f"[Setup] Gespeichert: Badge={badge}, HUD Theme={CONFIG['hud']['theme']}, Scale={CONFIG['hud']['scale']}")
        overlay_signal.reload_theme.emit()
        WindowAnimator.animate_close(self, on_finished=self.accept, duration=130, slide_distance=8)

class PDOverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowOpacity(0.0)
        self.current_screenshot = None
        self.pending_two_shot = self.load_pending_state()
        self.next_numbers = {
            'Inhaftierung': 1,
            'Global': 1,
            'Local': 1,
            'Event': 1,
            'Shoprob': 1,
            'FZ Raid': 1,
            'Streifenpartner': 1
        }
        self.init_ui()
        threading.Thread(target=self._fetch_stats_async, daemon=True).start()

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

        self.stats_title = QLabel("AKTUELLE STATISTIK")
        self.stats_title.setStyleSheet("font-size: 10px; font-weight: 700; color: #71717a; letter-spacing: 0.5px;")
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

        # Action Buttons Grid (3 rows x 2 columns)
        self.grid = QGridLayout()
        self.grid.setSpacing(6)

        self.btn_inhaftierung = QPushButton(" [1] 1. Inhaftierung")
        self.btn_inhaftierung.setIcon(create_dot_icon("#4bd4a3", 10))
        self.btn_inhaftierung.setIconSize(QSize(10, 10))
        self.btn_inhaftierung.clicked.connect(lambda: self.handle_action("Inhaftierung", "Inhaftierung"))
        self.grid.addWidget(self.btn_inhaftierung, 0, 0)

        self.btn_global = QPushButton(" [2] 1. Global")
        self.btn_global.setIcon(create_dot_icon("#ef4444", 10))
        self.btn_global.setIconSize(QSize(10, 10))
        self.btn_global.clicked.connect(lambda: self.handle_action("Global", "Global"))
        self.grid.addWidget(self.btn_global, 0, 1)

        self.btn_local = QPushButton(" [3] 1. Local")
        self.btn_local.setIcon(create_dot_icon("#5ea2ef", 10))
        self.btn_local.setIconSize(QSize(10, 10))
        self.btn_local.clicked.connect(lambda: self.handle_action("Local", "Local"))
        self.grid.addWidget(self.btn_local, 1, 0)

        self.btn_event = QPushButton(" [4] 1. Event (1/2)")
        self.btn_event.setIcon(create_dot_icon("#a87ffb", 10))
        self.btn_event.setIconSize(QSize(10, 10))
        self.btn_event.clicked.connect(lambda: self.handle_event_action("Event"))
        self.grid.addWidget(self.btn_event, 1, 1)

        self.btn_shoprob = QPushButton(" [5] 1. Shoprob (1/2)")
        self.btn_shoprob.setIcon(create_dot_icon("#f7bd2e", 10))
        self.btn_shoprob.setIconSize(QSize(10, 10))
        self.btn_shoprob.clicked.connect(lambda: self.handle_shoprob_action("Shoprob"))
        self.grid.addWidget(self.btn_shoprob, 2, 0)

        self.btn_fz = QPushButton(" [6] 1. FZ-Raid (1/2)")
        self.btn_fz.setIcon(create_dot_icon("#2dd4bf", 10))
        self.btn_fz.setIconSize(QSize(10, 10))
        self.btn_fz.clicked.connect(lambda: self.handle_fz_action("FZ Raid"))
        self.grid.addWidget(self.btn_fz, 2, 1)

        self.card_layout.addLayout(self.grid)

        # Streifenpartner Button
        self.btn_streifenpartner = QPushButton(" [7] 1. Streifenpartner")
        self.btn_streifenpartner.setIcon(create_dot_icon("#ec5ba3", 10))
        self.btn_streifenpartner.setIconSize(QSize(10, 10))
        self.btn_streifenpartner.clicked.connect(lambda: self.handle_action("Streifenpartner", "Streifenpartner"))
        self.card_layout.addWidget(self.btn_streifenpartner)

        # Intermediate Summary Button
        self.btn_send_summary = QPushButton("[8] / [Z] Zwischenstand in Chat senden")
        self.btn_send_summary.clicked.connect(self.handle_send_summary)
        self.card_layout.addWidget(self.btn_send_summary)

        # Delete Last Log Button
        self.btn_delete_last = QPushButton("[9] / [ENTF] Letzten Log löschen")
        self.btn_delete_last.clicked.connect(self.handle_delete_last_log)
        self.card_layout.addWidget(self.btn_delete_last)

        # Cancel Button
        self.btn_cancel = QPushButton("[ESC] Verwerfen (Nicht posten)")
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
        font_family = hud.get("font_family", "Inter")
        font_size = int(hud.get("font_size", 11))
        opacity = float(hud.get("opacity", 0.96))
        
        self.setWindowOpacity(opacity)
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        pos = hud.get("position", "Oben Rechts")
        x, y, w, h = calculate_overlay_geometry(scale, pos)
        self.setGeometry(x, y, w, h)

        badge_text = str(CONFIG.get("user_badge", "317108"))
        kw_val = _cached_thread_info.get("kw", -1)
        kw_pill = f" <span style='background: #151d28; color: #5ea2ef; border: 1px solid #1e2c3f; border-radius: 6px; padding: 2px 7px; font-size: {int(font_size * 0.82)}px; font-weight: 700;'>KW {kw_val}</span>" if kw_val > 0 else ""
        self.header_label.setText(
            f"<span style='font-size: {int(font_size * 1.15)}px; font-weight: 800; color: #ffffff;'>LSPD</span> "
            f"<span style='font-size: {int(font_size * 1.05)}px; font-weight: 600; color: #71717a;'>Log Assistent</span> "
            f"<span style='background: #181820; color: #a1a1aa; border: 1px solid #282835; border-radius: 6px; padding: 2px 7px; font-size: {int(font_size * 0.82)}px; font-weight: 600;'>#{badge_text}</span>"
            f"{kw_pill}"
        )
        self.header_label.setStyleSheet(f"font-size: {int(font_size * 1.15)}px; border: none; font-family: '{font_family}';")

        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg']};
                border: 1px solid {colors['border']};
                border-radius: {int(14 * scale)}px;
                font-family: "{font_family}";
            }}
        """)

        self.stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['card_bg']};
                border: 1px solid #22222a;
                border-radius: {int(10 * scale)}px;
                padding: {int(6 * scale)}px {int(8 * scale)}px;
            }}
        """)
        self.stats_title.setStyleSheet(f"color: #71717a; font-size: {int(font_size * 0.88)}px; font-weight: 700; letter-spacing: 0.6px; border: none;")
        self.stats_line1.setStyleSheet(f"color: {colors['text']}; font-size: {int(font_size * 0.92)}px; border: none;")
        self.stats_line2.setStyleSheet(f"color: {colors['text']}; font-size: {int(font_size * 0.92)}px; border: none;")

        self.status_label.setStyleSheet(f"color: #3b82f6; font-size: {int(font_size * 0.95)}px; font-weight: bold; border: none;")
        self.notify_label.setStyleSheet(f"color: #10b981; font-size: {int(font_size * 1.05)}px; font-weight: bold; border: none;")

        thumb_w = int(350 * scale)
        thumb_h = int(155 * scale)
        self.thumb_label.setFixedSize(thumb_w, thumb_h)
        self.thumb_label.setStyleSheet(f"background-color: {colors['thumb_bg']}; border-radius: {int(8 * scale)}px; border: 1px solid #22222a;")

        self.btn_base_style = f"""
            QPushButton {{
                background-color: {colors['btn_bg']};
                color: {colors['text']};
                border-radius: {int(9 * scale)}px;
                padding: {int(6 * scale)}px {int(8 * scale)}px;
                font-size: {font_size}px;
                font-weight: 600;
                border: 1px solid #23232b;
                text-align: left;
                font-family: "{font_family}";
            }}
            QPushButton:hover {{
                background-color: {colors['btn_hover']};
                color: #ffffff;
                border: 1px solid #383848;
            }}
            QPushButton:pressed {{
                background-color: #111114;
            }}
        """

        self.btn_send_summary.setStyleSheet(f"""
            QPushButton {{
                background-color: #212128;
                color: #ffffff;
                border-radius: {int(9 * scale)}px;
                padding: {int(8 * scale)}px {int(12 * scale)}px;
                font-size: {font_size}px;
                font-weight: 700;
                border: 1px solid #353546;
                text-align: center;
                font-family: "{font_family}";
            }}
            QPushButton:hover {{
                background-color: #2d2d3a;
                border-color: #4f4f66;
            }}
            QPushButton:pressed {{
                background-color: #181820;
            }}
        """)

        self.btn_delete_last.setStyleSheet(f"""
            QPushButton {{
                background-color: #181113;
                color: #f87171;
                border-radius: {int(9 * scale)}px;
                padding: {int(7 * scale)}px {int(12 * scale)}px;
                font-size: {font_size}px;
                font-weight: 600;
                border: 1px solid #381a1f;
                font-family: "{font_family}";
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #261317;
                color: #fecaca;
                border-color: #ef4444;
            }}
            QPushButton:pressed {{
                background-color: #120a0b;
            }}
        """)

        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #141418;
                color: #a1a1aa;
                border-radius: {int(9 * scale)}px;
                padding: {int(7 * scale)}px {int(12 * scale)}px;
                font-size: {font_size}px;
                font-weight: 600;
                border: 1px solid #23232b;
                font-family: "{font_family}";
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #1c1c22;
                color: #ffffff;
                border-color: #3f3f4e;
            }}
            QPushButton:pressed {{
                background-color: #0d0d10;
            }}
        """)

        self.reset_button_styles()

    def get_next_number(self, cat):
        return self.next_numbers.get(cat, 1)

    def update_button_labels(self, recommendation=None):
        inh_num = self.get_next_number("Inhaftierung")
        gl_num = self.get_next_number("Global")
        lo_num = self.get_next_number("Local")
        ev_num = self.get_next_number("Event")
        sh_num = self.get_next_number("Shoprob")
        fz_num = self.get_next_number("FZ Raid")
        sp_num = self.get_next_number("Streifenpartner")

        hud = CONFIG.get("hud", {})
        scale = float(hud.get("scale", 1.0))
        dot_sz = max(8, int(10 * scale))

        self.btn_inhaftierung.setIcon(create_dot_icon("#4bd4a3", dot_sz))
        self.btn_inhaftierung.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_global.setIcon(create_dot_icon("#ef4444", dot_sz))
        self.btn_global.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_local.setIcon(create_dot_icon("#5ea2ef", dot_sz))
        self.btn_local.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_event.setIcon(create_dot_icon("#a87ffb", dot_sz))
        self.btn_event.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_shoprob.setIcon(create_dot_icon("#f7bd2e", dot_sz))
        self.btn_shoprob.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_fz.setIcon(create_dot_icon("#2dd4bf", dot_sz))
        self.btn_fz.setIconSize(QSize(dot_sz, dot_sz))
        self.btn_streifenpartner.setIcon(create_dot_icon("#ec5ba3", dot_sz))
        self.btn_streifenpartner.setIconSize(QSize(dot_sz, dot_sz))

        self.btn_inhaftierung.setText(f" [1] {inh_num}. Inhaftierung")
        self.btn_global.setText(f" [2] {gl_num}. Global")
        self.btn_local.setText(f" [3] {lo_num}. Local")

        if self.pending_two_shot and self.pending_two_shot.get("type") == "Event":
            self.status_label.setText("Event: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_event.setText(f" [4] {ev_num}. Event (2/2)")
            self.highlight_button(self.btn_event, "#a87ffb", "#1c1428")
        else:
            self.btn_event.setText(f" [4] {ev_num}. Event (1/2)")

        if self.pending_two_shot and self.pending_two_shot.get("type") == "Ammu-Rob":
            self.status_label.setText("Shoprob: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_shoprob.setText(f" [5] {sh_num}. Shoprob (2/2)")
            self.highlight_button(self.btn_shoprob, "#f7bd2e", "#261a10")
        else:
            self.btn_shoprob.setText(f" [5] {sh_num}. Shoprob (1/2)")

        if self.pending_two_shot and self.pending_two_shot.get("type") == "FZ Raid":
            self.status_label.setText("FZ-Raid: Foto 1 aktiv. Das hier als Foto 2 senden?")
            self.status_label.setVisible(True)
            self.btn_fz.setText(f" [6] {fz_num}. FZ-Raid (2/2)")
            self.highlight_button(self.btn_fz, "#2dd4bf", "#102320")
        else:
            self.btn_fz.setText(f" [6] {fz_num}. FZ-Raid (1/2)")

        self.btn_streifenpartner.setText(f" [7] {sp_num}. Streifenpartner")

        if not self.pending_two_shot:
            self.status_label.setVisible(False)
            if recommendation == "inhaftierung":
                self.highlight_button(self.btn_inhaftierung, "#4bd4a3", "#122019")
                self.btn_inhaftierung.setText(f" [1] {inh_num}. Inhaftierung")
            elif recommendation == "global":
                self.highlight_button(self.btn_global, "#ef4444", "#241215")
                self.btn_global.setText(f" [2] {gl_num}. Global")
            elif recommendation == "local":
                self.highlight_button(self.btn_local, "#5ea2ef", "#121a28")
                self.btn_local.setText(f" [3] {lo_num}. Local")

    def update_stats_ui(self, counts):
        if counts:
            if 'next_numbers' in counts and isinstance(counts['next_numbers'], dict):
                self.next_numbers.update(counts['next_numbers'])
                self.update_button_labels()
            gl = f"<b>{counts.get('GL/LO', 0)}</b>/3"
            sh = f"<b>{counts.get('Shoprob etc.', 0)}</b>/3"
            ev = f"<b>{counts.get('Events', 0)}</b>/5"
            fz = f"<b>{counts.get('FZ-Raid', 0)}</b>/1"
            inh = f"<b>{counts.get('Inhaftierungen', 0)}</b>/7"
            part = f"<b>{counts.get('Streifenpartner', 0)}</b>/2"
            self.stats_line1.setText(f"GL/LO: {gl}  •  Shop: {sh}  •  Events: {ev}")
            self.stats_line2.setText(f"FZ: {fz}  •  Inh: {inh}  •  Partner: {part}")
            
            # Aktualisiere KW-Pill im Header
            badge_text = str(CONFIG.get("user_badge", "317108"))
            kw_val = _cached_thread_info.get("kw", -1)
            hud = CONFIG.get("hud", {})
            font_size = int(hud.get("font_size", 11))
            kw_pill = f" <span style='background: #151d28; color: #5ea2ef; border: 1px solid #1e2c3f; border-radius: 6px; padding: 2px 7px; font-size: {int(font_size * 0.82)}px; font-weight: 700;'>KW {kw_val}</span>" if kw_val > 0 else ""
            self.header_label.setText(
                f"<span style='font-size: {int(font_size * 1.15)}px; font-weight: 800; color: #ffffff;'>LSPD</span> "
                f"<span style='font-size: {int(font_size * 1.05)}px; font-weight: 600; color: #71717a;'>Log Assistent</span> "
                f"<span style='background: #181820; color: #a1a1aa; border: 1px solid #282835; border-radius: 6px; padding: 2px 7px; font-size: {int(font_size * 0.82)}px; font-weight: 600;'>#{badge_text}</span>"
                f"{kw_pill}"
            )
            log(f"[UI] Stats: GL/LO={gl}, Shop={sh}, Ev={ev}, FZ={fz}, Inh={inh}, Partner={part} | KW={kw_val}")

    def display_screenshot(self, screenshot_path, recommendation=None):
        log(f"[UI] display_screenshot: {screenshot_path}")
        self.current_screenshot = screenshot_path
        self.pending_two_shot = self.load_pending_state()
        
        pix = QPixmap(screenshot_path)
        if not pix.isNull():
            hud = CONFIG.get("hud", {})
            scale = float(hud.get("scale", 1.0))
            thumb_w = int(350 * scale)
            thumb_h = int(155 * scale)
            scaled = pix.scaled(thumb_w, thumb_h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.thumb_label.setPixmap(scaled)

        self.reset_button_styles()
        self.update_button_labels(recommendation)

        self.notify_label.setVisible(False)
        self.apply_theme()
        self._normal_pos = self.pos()
        target_op = float(CONFIG.get("hud", {}).get("opacity", 0.96))
        WindowAnimator.animate_open(self, target_opacity=target_op, duration=190, slide_distance=14)
        auto_sec = float(CONFIG.get("hud", {}).get("auto_close_sec", 25))
        if auto_sec > 0:
            self.auto_timer.start(int(auto_sec * 1000))

        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception as e:
            log(f"[Win32 Error] {e}")

        threading.Thread(target=self._fetch_stats_async, daemon=True).start()

    def _fetch_stats_async(self):
        counts, _ = calculate_zwischenstand()
        if counts:
            overlay_signal.update_stats.emit(counts)

    def highlight_button(self, btn, border_color, bg_color=None):
        hud = CONFIG.get("hud", {})
        scale = float(hud.get("scale", 1.0))
        font_size = int(hud.get("font_size", 11))
        bg = bg_color or "#18241d"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: #ffffff;
                border-radius: {int(9 * scale)}px;
                padding: {int(6 * scale)}px {int(8 * scale)}px;
                font-size: {font_size}px;
                font-weight: 700;
                border: 1.5px solid {border_color};
                text-align: left;
                font-family: "{hud.get('font_family', 'Segoe UI')}";
            }}
            QPushButton:hover {{
                background-color: {adjust_color(bg, 1.25)};
                border-color: {border_color};
            }}
        """)

    def reset_button_styles(self):
        self.btn_inhaftierung.setStyleSheet(self.btn_base_style)
        self.btn_global.setStyleSheet(self.btn_base_style)
        self.btn_local.setStyleSheet(self.btn_base_style)
        self.btn_event.setStyleSheet(self.btn_base_style)
        self.btn_shoprob.setStyleSheet(self.btn_base_style)
        self.btn_fz.setStyleSheet(self.btn_base_style)
        self.btn_streifenpartner.setStyleSheet(self.btn_base_style)
        self.update_button_labels()

    def handle_action(self, cat_key, base_title):
        num = self.get_next_number(cat_key)
        send_title = format_log_title_for_discord(cat_key, base_title, num)
        self.auto_timer.stop()
        self.show_notification(f"Sende {send_title}...")
        threading.Thread(target=self._send_async, args=(cat_key, send_title, [self.current_screenshot]), daemon=True).start()

    def handle_event_action(self, base_title="Event"):
        self.auto_timer.stop()
        num = self.get_next_number("Event")
        send_title = format_log_title_for_discord("Event", base_title, num)
        if self.pending_two_shot and self.pending_two_shot.get("type") == "Event":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification(f"Sende {send_title} (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("Event", send_title, [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "Event", "path": self.current_screenshot, "time": time.time()})
            self.show_notification(f"{num}. Event (Foto 1/2) gespeichert. Warte auf Foto 2.")
            try:
                play_beep(900, 80)
                play_beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_shoprob_action(self, base_title="Shoprob"):
        self.auto_timer.stop()
        num = self.get_next_number("Shoprob")
        send_title = format_log_title_for_discord("Shoprob", base_title, num)
        if self.pending_two_shot and self.pending_two_shot.get("type") == "Ammu-Rob":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification(f"Sende {send_title} (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("Shoprob", send_title, [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "Ammu-Rob", "path": self.current_screenshot, "time": time.time()})
            self.show_notification(f"{num}. Shoprob (Foto 1/2) gespeichert. Warte auf Foto 2.")
            try:
                play_beep(900, 80)
                play_beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_fz_action(self, base_title="FZ-Raid"):
        self.auto_timer.stop()
        num = self.get_next_number("FZ Raid")
        send_title = format_log_title_for_discord("FZ Raid", base_title, num)
        if self.pending_two_shot and self.pending_two_shot.get("type") == "FZ Raid":
            p1 = self.pending_two_shot.get("path")
            p2 = self.current_screenshot
            self.clear_pending_state()
            self.show_notification(f"Sende {send_title} (2 Fotos)...")
            threading.Thread(target=self._send_async, args=("FZ Raid", send_title, [p1, p2]), daemon=True).start()
        else:
            self.save_pending_state({"type": "FZ Raid", "path": self.current_screenshot, "time": time.time()})
            self.show_notification(f"{num}. FZ-Raid (Foto 1/2) gespeichert. Warte auf Foto 2.")
            try:
                play_beep(900, 80)
                play_beep(1300, 80)
            except Exception:
                pass
            QTimer.singleShot(1800, self.close_overlay)

    def handle_delete_last_log(self):
        self.auto_timer.stop()
        self.show_notification("Suche & lösche letzten Log aus Discord...")
        threading.Thread(target=self._delete_last_log_async, daemon=True).start()

    def _delete_last_log_async(self):
        success, info = delete_last_discord_log()
        if success:
            try:
                play_beep(1200, 80)
                play_beep(700, 120)
            except Exception:
                pass
            clean_title = info.replace('*', '').replace('_', '').replace('~', '').strip()
            self.show_notification(f"'{clean_title}' erfolgreich gelöscht.")
            threading.Thread(target=self._fetch_stats_async, daemon=True).start()
            QTimer.singleShot(2200, self.close_overlay)
        else:
            log(f"[Delete Log Error] {info}")
            self.show_notification(f"Fehler: {info}")
            QTimer.singleShot(2500, self.close_overlay)

    def handle_send_summary(self):
        self.auto_timer.stop()
        self.show_notification("Berechne & sende Zwischenstand...")
        threading.Thread(target=self._send_summary_async, daemon=True).start()

    def _send_summary_async(self):
        token = get_discord_token()
        if not token:
            self.show_notification("Kein Discord Token gefunden.")
            QTimer.singleShot(2500, self.close_overlay)
            return

        thread_id = get_active_thread_id(token)
        if not thread_id:
            self.show_notification("Forum-Thread nicht gefunden.")
            QTimer.singleShot(2500, self.close_overlay)
            return

        counts, formatted = calculate_zwischenstand(token, thread_id)
        if not counts or not formatted:
            self.show_notification("Fehler beim Zählen.")
            QTimer.singleShot(2500, self.close_overlay)
            return

        success, resp = send_to_discord(token, thread_id, formatted, [])
        if success:
            try:
                play_beep(1400, 100)
                play_beep(1800, 150)
            except Exception:
                pass
            self.show_notification("Zwischenstand in Discord gepostet.")
            overlay_signal.update_stats.emit(counts)
            QTimer.singleShot(1800, self.close_overlay)
        else:
            log(f"[Summary Send Error] {resp}")
            self.show_notification("Sende-Fehler aufgetreten.")
            QTimer.singleShot(2500, self.close_overlay)

    def _send_async(self, cat_key, title, file_paths):
        token = get_discord_token()
        if not token:
            self.show_notification("Kein Discord Token gefunden.")
            QTimer.singleShot(2500, self.close_overlay)
            return

        thread_id = get_active_thread_id(token)
        if not thread_id:
            self.show_notification("Forum-Thread nicht gefunden.")
            QTimer.singleShot(2500, self.close_overlay)
            return

        success, resp = send_to_discord(token, thread_id, title, file_paths)
        if success:
            if cat_key in self.next_numbers:
                self.next_numbers[cat_key] += 1
                if "counter_overrides" in CONFIG and isinstance(CONFIG["counter_overrides"], dict):
                    if cat_key in CONFIG["counter_overrides"]:
                        CONFIG["counter_overrides"][cat_key] = self.next_numbers[cat_key]
                        save_config(CONFIG)
                self.update_button_labels()
            try:
                play_beep(1500, 100)
                play_beep(1900, 150)
            except Exception:
                pass
            clean_display = title.replace('*', '').replace('_', '').strip()
            self.show_notification(f"{clean_display} gepostet.")
            threading.Thread(target=self._fetch_stats_async, daemon=True).start()
            QTimer.singleShot(1500, self.close_overlay)
        else:
            log(f"[Upload Error] {resp}")
            self.show_notification("Fehler beim Senden.")
            QTimer.singleShot(2500, self.close_overlay)

    def show_notification(self, text):
        self.notify_label.setText(text)
        self.notify_label.setVisible(True)

    def close_overlay(self):
        self.auto_timer.stop()
        WindowAnimator.animate_close(self, on_finished=self.hide, duration=140, slide_distance=10)

    def on_hotkey_pressed(self, key_char):
        if not self.isVisible():
            return
        log(f"[Hotkey] Taste gedrückt: {key_char}")
        if key_char == "1":
            self.handle_action("Inhaftierung", "Inhaftierung")
        elif key_char == "2":
            self.handle_action("Global", "Global")
        elif key_char == "3":
            self.handle_action("Local", "Local")
        elif key_char == "4":
            self.handle_event_action("Event")
        elif key_char == "5":
            self.handle_shoprob_action("Shoprob")
        elif key_char == "6":
            self.handle_fz_action("FZ Raid")
        elif key_char == "7":
            self.handle_action("Streifenpartner", "Streifenpartner")
        elif key_char in ("8", "z", "Z"):
            self.handle_send_summary()
        elif key_char in ("9", "del", "delete", "entf"):
            self.handle_delete_last_log()
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
                if c in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'z']:
                    overlay_signal.key_pressed.emit(c)
            elif key == keyboard.Key.esc:
                overlay_signal.key_pressed.emit("esc")
            elif key in (keyboard.Key.delete, getattr(keyboard.Key, 'delete', None)):
                overlay_signal.key_pressed.emit("del")
            elif key == keyboard.Key.f10 or str(key) == 'Key.f10' or getattr(key, 'name', '') == 'f10':
                log("[Keyboard] F10 Taste erkannt -> Toggle Teleprompter HUD")
                overlay_signal.toggle_prompter.emit()
            elif key == keyboard.Key.f12 or str(key) == 'Key.f12' or getattr(key, 'name', '') == 'f12':
                log("[Keyboard] F12 Taste erkannt -> Toggle Rechner")
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
    p.setFont(QFont("Inter", 24, QFont.Bold))
    p.setPen(QColor("#ffffff"))
    p.drawText(pix.rect(), int(Qt.AlignCenter), "PD")
    p.end()
    return QIcon(pix)

def main():
    log(f"[Main] Starte QApplication (v{CURRENT_VERSION})...")
    app = QApplication(sys.argv)
    init_custom_fonts(app)
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

    calc_overlay = GrandCalculatorOverlay(CONFIG.get("calc_theme", "Grandkasten Cyberpunk"))

    def toggle_calc():
        log("[Calc] toggle_calc getriggert")
        try:
            if calc_overlay.isVisible() and not getattr(calc_overlay, '_is_animating_close', False):
                if hasattr(calc_overlay, 'animate_close'):
                    calc_overlay.animate_close()
                else:
                    calc_overlay.hide()
            else:
                if hasattr(calc_overlay, 'show_calculator'):
                    calc_overlay.show_calculator()
                elif hasattr(calc_overlay, 'show_overlay'):
                    calc_overlay.show_overlay()
                else:
                    calc_overlay.show()
        except Exception as e:
            log(f"[Calc Error] {e}")

    overlay_signal.toggle_calculator.connect(toggle_calc)

    def toggle_prompter_hud():
        log("[Prompter] toggle_prompter_hud getriggert")
        try:
            if hasattr(calc_overlay, 'toggle_floating_prompter'):
                calc_overlay.toggle_floating_prompter()
        except Exception as e:
            log(f"[Prompter Error] {e}")

    overlay_signal.toggle_prompter.connect(toggle_prompter_hud)

    def reload_hud_theme():
        global _cached_thread_info
        _cached_thread_info = {"id": None, "time": 0, "badge": None, "name": "", "kw": -1}
        overlay.apply_theme()
        calc_theme_name = CONFIG.get("calc_theme", "Grandkasten Cyberpunk")
        calc_overlay.update_theme(calc_theme_name)
        tray.setIcon(create_tray_icon())
        tray.setToolTip(f"LSPD Log Assistent v{CURRENT_VERSION} | Badge: [{CONFIG.get('user_badge')}]")

    overlay_signal.reload_theme.connect(reload_hud_theme)

    def show_settings_dialog():
        dlg = SetupDialog()
        if dlg.exec() == QDialog.Accepted:
            global CONFIG
            CONFIG = load_config()
            reload_hud_theme()
            try:
                calc = locals().get('calc_overlay') or globals().get('calc_overlay')
                if calc:
                    if hasattr(calc, 'on_theme_changed_from_ui'):
                        calc.on_theme_changed_from_ui(CONFIG.get("calc_theme", "Schwarz-Grau-Weiß (Monochrome)"))
                    if hasattr(calc, 'combo_header_scale'):
                        c_sc = float(CONFIG.get("calc_scale", 0.82))
                        for i in range(calc.combo_header_scale.count()):
                            if abs(calc.combo_header_scale.itemData(i) - c_sc) < 0.03:
                                calc.combo_header_scale.setCurrentIndex(i)
                                break
            except Exception as e:
                log(f"[Settings Sync Error] {e}")
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

    act_test = QAction("Test-Overlay öffnen", tray_menu)
    act_test.triggered.connect(trigger_test_overlay)
    tray_menu.addAction(act_test)

    act_calc = QAction("Bußgeld- & TOW-Rechner (F12)", tray_menu)
    act_calc.triggered.connect(toggle_calc)
    tray_menu.addAction(act_calc)

    act_prompter = QAction("Teleprompter & Rechte (F10)", tray_menu)
    act_prompter.triggered.connect(toggle_prompter_hud)
    tray_menu.addAction(act_prompter)

    act_summary = QAction("Zwischenstand jetzt senden", tray_menu)
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
                    f"<b>Du nutzt bereits die aktuellste Version (v{CURRENT_VERSION})!</b><br><br>Es ist kein neues Update erforderlich.",
                    "info"
                )
            else:
                overlay_signal.show_msg.emit(
                    "LSPD Update",
                    "<b>Update-Prüfung fehlgeschlagen.</b><br><br>Konnte keine Verbindung zum GitHub-Server herstellen.",
                    "warn"
                )
        threading.Thread(target=run_check, daemon=True).start()

    act_update = QAction("Nach Updates suchen", tray_menu)
    act_update.triggered.connect(manual_check_updates)
    tray_menu.addAction(act_update)

    def toggle_sound_tray():
        new_val = not CONFIG.get("sound_enabled", True)
        CONFIG["sound_enabled"] = new_val
        save_config(CONFIG)
        act_sound.setChecked(new_val)
        if new_val:
            play_beep(1200, 100)

    act_sound = QAction("Signalton (Piep-Sound)", tray_menu)
    act_sound.setCheckable(True)
    act_sound.setChecked(CONFIG.get("sound_enabled", True))
    act_sound.triggered.connect(toggle_sound_tray)
    tray_menu.addAction(act_sound)

    def delete_last_log_from_tray():
        def worker():
            s, info = delete_last_discord_log()
            if s:
                try:
                    play_beep(1200, 80)
                    play_beep(700, 120)
                except Exception:
                    pass
                overlay_signal.show_msg.emit("LSPD Log Assistent", f"Letzter Log wurde erfolgreich aus Discord gelöscht:<br><br><b>{info}</b>", "info")
                c, _ = calculate_zwischenstand()
                if c:
                    overlay_signal.update_stats.emit(c)
            else:
                overlay_signal.show_msg.emit("LSPD Log Assistent", f"Konnte letzten Log nicht löschen:<br><br>{info}", "warn")
        threading.Thread(target=worker, daemon=True).start()

    act_delete_log = QAction("Letzten Discord-Log löschen", tray_menu)
    act_delete_log.triggered.connect(delete_last_log_from_tray)
    tray_menu.addAction(act_delete_log)

    act_settings = QAction("Einstellungen (HUD / Badge / Pfade)", tray_menu)
    act_settings.triggered.connect(show_settings_dialog)
    tray_menu.addAction(act_settings)

    def open_watch_folder():
        wdir = CONFIG.get("watch_dir") or get_default_watch_dir()
        if os.path.exists(wdir):
            os.startfile(wdir)
        else:
            QMessageBox.information(None, "Ordner nicht gefunden", f"Der Ordner existiert noch nicht:\n{wdir}")

    act_folder = QAction("Medal-Ordner öffnen", tray_menu)
    act_folder.triggered.connect(open_watch_folder)
    tray_menu.addAction(act_folder)

    tray_menu.addSeparator()

    act_exit = QAction("Beenden", tray_menu)
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
