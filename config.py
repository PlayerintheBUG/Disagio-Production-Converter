#!/usr/bin/env python3
"""
Disagio — config.py
Costanti globali, tool discovery, preset video/audio/immagini, formati immagini.
"""

import sys
import os
import shutil
import ctypes
from pathlib import Path

def _carica_librerie_cuda():
    home = str(Path.home())

    if sys.platform.startswith("win32"):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(base_path)
            except Exception:
                pass
        os.environ["PATH"] = base_path + os.pathsep + os.environ.get("PATH", "")

    elif sys.platform.startswith("linux"):
        cublas_path = f"{home}/.local/lib/python3.14/site-packages/nvidia/cublas/lib"
        cudnn_path = f"{home}/.local/lib/python3.14/site-packages/nvidia/cudnn/lib"

        current_ld = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = f"{cublas_path}:{cudnn_path}:{current_ld}"

        for path in [cublas_path, cudnn_path]:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.startswith("libcublas.so") or file.startswith("libcudnn.so"):
                        try:
                            ctypes.CDLL(os.path.join(path, file))
                        except Exception:
                            pass

_carica_librerie_cuda()
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
# =====================================================================

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QButtonGroup, QRadioButton, QComboBox,
    QLineEdit, QFileDialog, QPlainTextEdit, QProgressBar,
    QFrame, QScrollArea, QMessageBox, QGroupBox, QCheckBox,
    QDialog, QDialogButtonBox, QTextEdit, QSlider, QSizePolicy,
    QColorDialog, QGridLayout, QFormLayout, QListWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

def _find_tool(name: str) -> str:
    exe = name + (".exe" if sys.platform == "win32" else "")

    # 1. Bundle PyInstaller (sys._MEIPASS esiste solo dentro l'exe)
    if hasattr(sys, "_MEIPASS"):
        candidate = os.path.join(sys._MEIPASS, exe)
        if os.path.isfile(candidate):
            return candidate

    # 2. Stessa cartella dell'eseguibile (utile per distribuzione manuale)
    if getattr(sys, "frozen", False):
        candidate = os.path.join(os.path.dirname(sys.executable), exe)
        if os.path.isfile(candidate):
            return candidate

    # 3. PATH di sistema
    found = shutil.which(name)
    if found:
        return found

    # Fallback – subprocess solleverà un errore leggibile
    return exe

FFMPEG_BIN  = _find_tool("ffmpeg")
FFPROBE_BIN = _find_tool("ffprobe")

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = "disagio_config.json"
# ============================================================
#  MAPPATURE
# ============================================================
CONTAINER_CODECS = {
    "MKV (.mkv)": ["AV1", "H.264", "H.265"],
    "MP4 (.mp4)": ["AV1", "H.264", "H.265"],
    "MOV (.mov)": ["ProRes", "DNxHR"],
}
# GPU → Codec → Qualità → stringa parametri ffmpeg
VIDEO_PRESETS = {
    "NVIDIA": {
        "AV1": {
            "Alto":  "-c:v av1_nvenc -preset p7 -cq 12 -pix_fmt p010le",
            "Medio": "-c:v av1_nvenc -preset p6 -cq 24 -pix_fmt p010le",
            "Basso": "-c:v av1_nvenc -preset p4 -cq 35 -pix_fmt p010le",
        },
        "H.264": {
            "Alto":  "-c:v h264_nvenc -preset p7 -cq 16 -pix_fmt yuv420p",
            "Medio": "-c:v h264_nvenc -preset p5 -cq 24 -pix_fmt yuv420p",
            "Basso": "-c:v h264_nvenc -preset p3 -cq 35 -pix_fmt yuv420p",
        },
        "H.265": {
            "Alto":  "-c:v hevc_nvenc -preset p7 -cq 16 -pix_fmt p010le",
            "Medio": "-c:v hevc_nvenc -preset p5 -cq 24 -pix_fmt p010le",
            "Basso": "-c:v hevc_nvenc -preset p3 -cq 35 -pix_fmt p010le",
        },
    },
    "AMD": {
        "AV1": {
            "Alto":  "-c:v av1_amf -quality quality -rc cqp -qp_i 12 -qp_p 12 -pix_fmt yuv420p",
            "Medio": "-c:v av1_amf -quality balanced -rc cqp -qp_i 22 -qp_p 22 -pix_fmt yuv420p",
            "Basso": "-c:v av1_amf -quality speed -rc cqp -qp_i 32 -qp_p 32 -pix_fmt yuv420p",
        },
        "H.264": {
            "Alto":  "-c:v h264_amf -quality quality -rc cqp -qp_i 16 -qp_p 16 -pix_fmt yuv420p",
            "Medio": "-c:v h264_amf -quality balanced -rc cqp -qp_i 24 -qp_p 24 -pix_fmt yuv420p",
            "Basso": "-c:v h264_amf -quality speed -rc cqp -qp_i 34 -qp_p 34 -pix_fmt yuv420p",
        },
        "H.265": {
            "Alto":  "-c:v hevc_amf -quality quality -rc cqp -qp_i 16 -qp_p 16 -pix_fmt yuv420p",
            "Medio": "-c:v hevc_amf -quality balanced -rc cqp -qp_i 24 -qp_p 24 -pix_fmt yuv420p",
            "Basso": "-c:v hevc_amf -quality speed -rc cqp -qp_i 34 -qp_p 34 -pix_fmt yuv420p",
        },
    },
    "Intel": {
        "AV1": {
            "Alto":  "-c:v av1_qsv -preset veryslow -global_quality 12 -pix_fmt yuv420p",
            "Medio": "-c:v av1_qsv -preset medium -global_quality 22 -pix_fmt yuv420p",
            "Basso": "-c:v av1_qsv -preset faster -global_quality 32 -pix_fmt yuv420p",
        },
        "H.264": {
            "Alto":  "-c:v h264_qsv -preset veryslow -global_quality 16 -pix_fmt yuv420p",
            "Medio": "-c:v h264_qsv -preset medium -global_quality 24 -pix_fmt yuv420p",
            "Basso": "-c:v h264_qsv -preset faster -global_quality 34 -pix_fmt yuv420p",
        },
        "H.265": {
            "Alto":  "-c:v hevc_qsv -preset veryslow -global_quality 16 -pix_fmt yuv420p",
            "Medio": "-c:v hevc_qsv -preset medium -global_quality 24 -pix_fmt yuv420p",
            "Basso": "-c:v hevc_qsv -preset faster -global_quality 34 -pix_fmt yuv420p",
        },
    },
    "CPU": {
        "AV1": {
            "Alto":  "-c:v libsvtav1 -preset 3 -crf 12 -pix_fmt yuv420p10le",
            "Medio": "-c:v libsvtav1 -preset 6 -crf 24 -pix_fmt yuv420p10le",
            "Basso": "-c:v libsvtav1 -preset 9 -crf 35 -pix_fmt yuv420p",
        },
        "H.264": {
            "Alto":  "-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p",
            "Medio": "-c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p",
            "Basso": "-c:v libx264 -preset faster -crf 32 -pix_fmt yuv420p",
        },
        "H.265": {
            "Alto":  "-c:v libx265 -preset slow -crf 16 -pix_fmt yuv420p",
            "Medio": "-c:v libx265 -preset medium -crf 24 -pix_fmt yuv420p",
            "Basso": "-c:v libx265 -preset faster -crf 32 -pix_fmt yuv420p",
        },
    },
    # DNxHR e ProRes: sempre CPU
    "DNxHR": {
        "Alto":  "-c:v dnxhd -profile:v dnxhr_hqx -pix_fmt yuv422p10le",
        "Medio": "-c:v dnxhd -profile:v dnxhr_hq  -pix_fmt yuv422p",
        "Basso": "-c:v dnxhd -profile:v dnxhr_sq  -pix_fmt yuv422p",
    },
    "ProRes": {
        "Alto":  "-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le",
        "Medio": "-c:v prores_ks -profile:v hq   -pix_fmt yuv422p10le",
        "Basso": "-c:v prores_ks -profile:v standard -pix_fmt yuv422p10le",
    },
}
# ── Matrice AUTO ──────────────────────────────────────────────
# Efficienza relativa codec sorgente (moltiplicatore verso H264 equiv)
CODEC_EFFICIENCY = {
    "mpeg2video": 3.0,
    "mpeg4":      1.5,
    "h264":       1.0,
    "hevc":       0.5,
    "vp8":        0.9,
    "vp9":        0.5,
    "av1":        0.4,
    "theora":     1.8,
    "wmv1":       2.0, "wmv2": 2.0, "wmv3": 1.8,
    "prores":     5.0,   # 422 base
    "dnxhd":      4.0,
    "rv30":       2.0, "rv40": 1.8,
}
# Profilo ProRes → moltiplicatore più preciso
PRORES_PROFILE_EFFICIENCY = {
    "0": 4.0,   # proxy
    "1": 4.5,   # lt
    "2": 5.0,   # 422
    "3": 6.0,   # 422 hq
    "4": 7.0,   # 4444
    "5": 9.0,   # 4444 xq
}
# CQ base per codec destinazione
AUTO_BASE_CQ = {
    "AV1":   28,
    "H.264": 20,
    "H.265": 24,
}
# Delta risoluzione (su risoluzione DESTINAZIONE)
AUTO_DELTA_RES = {
    "480p":     +4,
    "720p":     +2,
    "1080p":     0,
    "1440p QHD": -2,
    "4K UHD":   -4,
    "8K UHD":   -6,
    "Originale": 0,  # calcolato dinamicamente dopo
}
# Delta fps
def auto_delta_fps(fps: float) -> int:
    if fps <= 24:   return +1
    if fps <= 30:   return  0
    if fps <= 60:   return -2
    return -4
# Delta bit depth
def auto_delta_depth(depth: int) -> int:
    if depth <= 8:  return  0
    if depth == 10: return -2
    return -3
# Delta complessità (bits per pixel per frame, normalizzato)
def auto_delta_bpp(bpp: float) -> int:
    if bpp < 0.05:  return +6
    if bpp < 0.15:  return +3
    if bpp < 0.40:  return  0
    if bpp < 1.0:   return -3
    if bpp < 3.0:   return -5
    return -7
# Profilo DNxHR/ProRes in base a risoluzione e bit depth sorgente
def auto_mezzanine_profile(codec_dst: str, width: int, height: int, depth: int) -> str:
    is_4k = (width >= 3840 or height >= 2160)
    if codec_dst == "DNxHR":
        if is_4k or depth >= 10:
            return "-c:v dnxhd -profile:v dnxhr_hqx -pix_fmt yuv422p10le"
        return "-c:v dnxhd -profile:v dnxhr_hq -pix_fmt yuv422p"
    if codec_dst == "ProRes":
        if depth >= 10 and is_4k:
            return "-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le"
        if is_4k or depth >= 10:
            return "-c:v prores_ks -profile:v hq -pix_fmt yuv422p10le"
        return "-c:v prores_ks -profile:v standard -pix_fmt yuv422p10le"
    return ""
# ─────────────────────────────────────────────────────────────
AUDIO_CODECS = ["FLAC", "PCM", "AAC", "Opus", "MP3"]
AUDIO_PRESETS = {
    "FLAC": {
        "Alto":  "-c:a flac -compression_level 0",
        "Medio": "-c:a flac -compression_level 5",
        "Basso": "-c:a flac -compression_level 8",
    },
    "PCM": {
        "Alto":  "-c:a pcm_f32le",
        "Medio": "-c:a pcm_s24le",
        "Basso": "-c:a pcm_s16le",
    },
    "AAC": {
        "Alto":  "-c:a aac -b:a 320k",
        "Medio": "-c:a aac -b:a 192k",
        "Basso": "-c:a aac -b:a 128k",
    },
    "Opus": {
        "Alto":  "-c:a libopus -b:a 320k",
        "Medio": "-c:a libopus -b:a 192k",
        "Basso": "-c:a libopus -b:a 96k",
    },
    "MP3": {
        "Alto":  "-c:a libmp3lame -b:a 320k",
        "Medio": "-c:a libmp3lame -b:a 192k",
        "Basso": "-c:a libmp3lame -b:a 128k",
    },
}
AUDIO_ONLY_EXT = {
    "FLAC": "flac", "PCM": "wav", "AAC": "m4a", "Opus": "opus", "MP3": "mp3",
}
SAMPLE_RATES = ["Mantieni originale", "44100 Hz", "48000 Hz", "96000 Hz", "192000 Hz"]
GPU_OPTIONS = ["NVIDIA", "AMD", "Intel", "CPU"]
# Risoluzioni 16:9 con dimensioni esatte
RESOLUTIONS = {
    "Mantieni originale": None,
    "480p  (854×480)":    (854,  480),
    "720p  (1280×720)":   (1280, 720),
    "1080p (1920×1080)":  (1920, 1080),
    "1440p QHD (2560×1440)": (2560, 1440),
    "4K UHD (3840×2160)": (3840, 2160),
    "8K UHD (7680×4320)": (7680, 4320),
}
VIDEO_EXTENSIONS = {".mp4",".mkv",".mov",".avi",".webm",".flv",
                    ".mts",".m2ts",".ts",".wmv",".vob",".mpg",
                    ".mpeg",".ogv",".divx",".m4v",".3gp"}
AUDIO_EXTENSIONS = {".mp3",".flac",".wav",".aac",".m4a",".ogg",
                    ".opus",".wma",".aiff",".aif",".ac3",".dts",
                    ".mka",".wv",".ape",".ra",".voc",".w64"}
IMAGE_EXTENSIONS = {".jpg",".jpeg",".png",".webp",".bmp",".tiff",".tif",
                    ".gif",".tga",".heic",".heif",".avif"}
RAW_EXTENSIONS   = {".cr2",".cr3",".nef",".arw",".dng",".pef",".orf",
                    ".rw2",".raf",".3fr",".mef",".mrw",".sr2",".raw",
                    ".nrw",".srf",".erf",".kdc",".dcr"}
# Formati di output immagini disponibili
IMAGE_OUTPUT_FORMATS = {
    "JPG (.jpg)": "jpg",
    "PNG (.png)": "png",
    "WebP (.webp)": "webp",
    "BMP (.bmp)": "bmp",
}
_IMG_QUAL_LABELS = {
    90: {
        "it": "Massima qualità  (File molto grande)",
        "en": "Maximum quality  (Very large file)",
        "de": "Maximale Qualität  (Sehr große Datei)",
        "es": "Calidad máxima  (Archivo muy grande)",
        "doge": "much quality. very big file wow",
    },
    75: {
        "it": "Alta qualità  (Consigliato)",
        "en": "High quality  (Recommended)",
        "de": "Hohe Qualität  (Empfohlen)",
        "es": "Alta calidad  (Recomendado)",
        "doge": "good quality wow (do this)",
    },
    50: {
        "it": "Qualità media  (Bilanciato)",
        "en": "Medium quality  (Balanced)",
        "de": "Mittlere Qualität  (Ausgewogen)",
        "es": "Calidad media  (Equilibrado)",
        "doge": "medium quality. such balance.",
    },
    25: {
        "it": "Bassa qualità  (Alta compressione)",
        "en": "Low quality  (High compression)",
        "de": "Niedrige Qualität  (Hohe Komprimierung)",
        "es": "Baja calidad  (Alta compresión)",
        "doge": "smol quality. much squish.",
    },
    0: {
        "it": "Qualità minima  (File molto piccolo)",
        "en": "Minimum quality  (Very small file)",
        "de": "Minimale Qualität  (Sehr kleine Datei)",
        "es": "Calidad mínima  (Archivo muy pequeño)",
        "doge": "tiny quality. very smol file. wow",
    },
}

LICENSE_TEXT = """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Copyright (C) 2026 playerinthebug

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISAGIO PRODUCTION CONVERTER
Open source video/audio converter — PyQt6 + FFmpeg
Repository: https://github.com/PlayerintheBUG/Disagio-Production-Converter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[THIRD-PARTY LICENSE COMPLIANCE & BINARY DISTRIBUTION NOTE]

This software relies on FFmpeg and FFprobe to perform media conversions.

- For Windows Distributions (.exe): This standalone package bundles the
  compiled, unmodified binaries of ffmpeg.exe and ffprobe.exe (Version 8.1.1
  Full Build, sourced from https://www.gyan.dev/ffmpeg/builds/).

- For Linux / Source Distributions: The software interfaces directly with the
  FFmpeg binaries installed on the host system.

In accordance with the GNU GPL v3 license, any bundled FFmpeg binaries are
completely unmodified. The official source code of FFmpeg can be freely
downloaded from https://ffmpeg.org. The inclusion or invocation of these
binaries does not alter the open-source and free nature of this software.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
