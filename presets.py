#!/usr/bin/env python3
"""
Disagio — presets.py
Gestione preset FFmpeg personalizzati (save/load/delete).
"""

import json
import os

from config import CONFIG_FILE

PRESETS_KEY = "ffmpeg_presets"


def load_ffmpeg_presets() -> dict:
    """Restituisce il dizionario {nome: comando} dei preset salvati."""
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        return cfg.get(PRESETS_KEY, {})
    except Exception:
        return {}


def save_ffmpeg_preset(name: str, command: str):
    """Salva o sovrascrive un preset nel config JSON."""
    try:
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        if PRESETS_KEY not in cfg:
            cfg[PRESETS_KEY] = {}
        cfg[PRESETS_KEY][name] = command
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def delete_ffmpeg_preset(name: str):
    """Elimina un preset dal config JSON."""
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        if PRESETS_KEY in cfg and name in cfg[PRESETS_KEY]:
            del cfg[PRESETS_KEY][name]
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=2)
    except Exception:
        pass
