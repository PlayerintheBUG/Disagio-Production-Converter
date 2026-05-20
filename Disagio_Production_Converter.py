#!/usr/bin/env python3
# ============================================================
# Disagio_Producition_Converter.py  —  DISAGIO PRODUCTION CONVERTER
#
#  Copyright (C) 2026  playerinthebug
#
#  This program is free software: you can redistribute it
#  and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any
#  later version.
#
#  This program is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE. See the GNU General Public License for more
#  details: <https://www.gnu.org/licenses/>
#
#  Dipendenze: PyQt6, ffmpeg
#  Installazione: pip install PyQt6 --user
# ============================================================
import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QButtonGroup, QRadioButton, QComboBox,
    QLineEdit, QFileDialog, QPlainTextEdit, QProgressBar,
    QFrame, QScrollArea, QMessageBox, QGroupBox, QCheckBox,
    QDialog, QDialogButtonBox, QTextEdit, QSlider, QSizePolicy,
    QColorDialog, QGridLayout
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
def image_quality_label(val: int) -> str:
    """Restituisce una descrizione testuale del livello di qualità (1-100)."""
    if val >= 90: return f"{val}%  —  Massima qualità  (File molto grande)"
    if val >= 75: return f"{val}%  —  Alta qualità  (Consigliato)"
    if val >= 50: return f"{val}%  —  Qualità media  (Bilanciato)"
    if val >= 25: return f"{val}%  —  Bassa qualità  (Alta compressione)"
    return         f"{val}%  —  Qualità minima  (File molto piccolo)"
def build_image_ffmpeg_args(fmt: str, quality: int) -> list:
    """
    Costruisce la lista di argomenti ffmpeg per la conversione immagini.
    quality: 1-100 (100 = massima qualità)
    """
    if fmt == "jpg":
        # ffmpeg -q:v: 2 = alta qualità, 31 = bassa. Rimappiamo 100→2, 1→31.
        qv = max(2, min(31, 31 - int(quality * 29 / 100)))
        return ["-q:v", str(qv)]
    if fmt == "png":
        # PNG: compression_level 0 = nessuna compressione (file grande), 9 = max compressione
        # Invertiamo: qualità 100 → livello 0 (file grande/nitido), qualità 1 → livello 9
        level = max(0, min(9, 9 - int(quality * 9 / 100)))
        return ["-compression_level", str(level)]
    if fmt == "webp":
        return ["-c:v", "libwebp", "-quality", str(quality)]
    if fmt == "bmp":
        return ["-c:v", "bmp"]  # BMP non ha compressione
    return []
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
# ============================================================
#  ANALISI SORGENTE (per modalità AUTO)
# ============================================================
def probe_video(path: str) -> dict:
    """Legge le proprietà video con ffprobe. Ritorna dict con i valori."""
    result = {
        "codec":     "h264",
        "width":     1920,
        "height":    1080,
        "fps":       25.0,
        "bitrate":   8_000_000,
        "depth":     8,
        "profile":   "0",
    }
    try:
        r = subprocess.run(
            [FFPROBE_BIN, "-v", "quiet", "-select_streams", "v:0",
             "-show_entries",
             "stream=codec_name,width,height,r_frame_rate,bit_rate,bits_per_raw_sample,profile",
             "-of", "default=noprint_wrappers=1", path],
            capture_output=True, text=True, timeout=20
        )
        for line in r.stdout.splitlines():
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k == "codec_name"         and v: result["codec"]   = v.lower()
            elif k == "width"            and v.isdigit(): result["width"]  = int(v)
            elif k == "height"           and v.isdigit(): result["height"] = int(v)
            elif k == "bits_per_raw_sample" and v.isdigit() and int(v) > 0:
                result["depth"] = int(v)
            elif k == "bit_rate"         and v.isdigit(): result["bitrate"] = int(v)
            elif k == "profile"          and v: result["profile"] = v
            elif k == "r_frame_rate"     and "/" in v:
                num, den = v.split("/")
                if int(den) > 0:
                    result["fps"] = round(int(num) / int(den), 3)
        # fallback bitrate dal formato se non nel stream
        if result["bitrate"] == 8_000_000:
            r2 = subprocess.run(
                [FFPROBE_BIN, "-v", "quiet", "-show_entries", "format=bit_rate",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=10
            )
            v2 = r2.stdout.strip()
            if v2.isdigit():
                result["bitrate"] = int(v2)
    except Exception:
        pass
    return result
def auto_compute_cq(src_info: dict, codec_dst: str, gpu: str,
                    dst_width: int, dst_height: int) -> str:
    """
    Calcola i parametri video ottimali per il codec di destinazione
    basandosi sulle proprietà del sorgente.
    Ritorna la stringa di parametri ffmpeg.
    """
    codec_src = src_info["codec"]
    bitrate   = src_info["bitrate"]
    fps       = src_info["fps"]
    depth     = src_info["depth"]
    width     = src_info["width"]
    height    = src_info["height"]
    profile   = src_info.get("profile", "0")
    # efficienza codec sorgente
    efficiency = CODEC_EFFICIENCY.get(codec_src, 1.0)
    # ProRes: affina in base al profilo
    if codec_src == "prores":
        p = str(profile).lower()
        for k, v in PRORES_PROFILE_EFFICIENCY.items():
            if k in p or p == k:
                efficiency = v
                break
    # bitrate equivalente H264
    bitrate_equiv = bitrate * efficiency
    # bits per pixel per frame (sulla risoluzione di DESTINAZIONE)
    dst_pixels = dst_width * dst_height
    bpp = (bitrate_equiv / max(fps, 1)) / max(dst_pixels, 1)
    # per DNxHR/ProRes non si usa CQ — profilo fisso
    if codec_dst in ("DNxHR", "ProRes"):
        return auto_mezzanine_profile(codec_dst, dst_width, dst_height, depth)
    # determina range risoluzione destinazione per delta
    if dst_height >= 4320:    res_key = "8K UHD"
    elif dst_height >= 2160:  res_key = "4K UHD"
    elif dst_height >= 1440:  res_key = "1440p QHD"
    elif dst_height >= 1080:  res_key = "1080p"
    elif dst_height >= 720:   res_key = "720p"
    else:                     res_key = "480p"
    cq = (AUTO_BASE_CQ.get(codec_dst, 24)
          + AUTO_DELTA_RES.get(res_key, 0)
          + auto_delta_fps(fps)
          + auto_delta_depth(depth)
          + auto_delta_bpp(bpp))
    # clamp: mai sotto 8 (eccessivo) né sopra 51
    cq = max(8, min(51, cq))
    # costruisce stringa parametri in base a GPU e codec
    if codec_dst == "AV1":
        pix = "p010le" if depth >= 10 else "p010le"
        if gpu == "NVIDIA":
            p7 = "p7" if cq <= 18 else ("p6" if cq <= 28 else "p4")
            return f"-c:v av1_nvenc -preset {p7} -cq {cq} -pix_fmt {pix}"
        if gpu == "AMD":
            q = "quality" if cq <= 18 else ("balanced" if cq <= 28 else "speed")
            return f"-c:v av1_amf -quality {q} -rc cqp -qp_i {cq} -qp_p {cq} -pix_fmt yuv420p"
        if gpu == "Intel":
            p = "veryslow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
            return f"-c:v av1_qsv -preset {p} -global_quality {cq} -pix_fmt yuv420p"
        # CPU
        pr = 3 if cq <= 18 else (6 if cq <= 28 else 9)
        return f"-c:v libsvtav1 -preset {pr} -crf {cq} -pix_fmt {pix}"
    if codec_dst == "H.264":
        pix = "yuv420p"
        if gpu == "NVIDIA":
            p = "p7" if cq <= 18 else ("p5" if cq <= 28 else "p3")
            return f"-c:v h264_nvenc -preset {p} -cq {cq} -pix_fmt {pix}"
        if gpu == "AMD":
            q = "quality" if cq <= 18 else ("balanced" if cq <= 28 else "speed")
            return f"-c:v h264_amf -quality {q} -rc cqp -qp_i {cq} -qp_p {cq} -pix_fmt {pix}"
        if gpu == "Intel":
            p = "veryslow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
            return f"-c:v h264_qsv -preset {p} -global_quality {cq} -pix_fmt {pix}"
        p = "slow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
        return f"-c:v libx264 -preset {p} -crf {cq} -pix_fmt {pix}"
    if codec_dst == "H.265":
        pix = "p010le" if depth >= 10 else "yuv420p"
        if gpu == "NVIDIA":
            p = "p7" if cq <= 18 else ("p5" if cq <= 28 else "p3")
            return f"-c:v hevc_nvenc -preset {p} -cq {cq} -pix_fmt {pix}"
        if gpu == "AMD":
            q = "quality" if cq <= 18 else ("balanced" if cq <= 28 else "speed")
            return f"-c:v hevc_amf -quality {q} -rc cqp -qp_i {cq} -qp_p {cq} -pix_fmt {pix}"
        if gpu == "Intel":
            p = "veryslow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
            return f"-c:v hevc_qsv -preset {p} -global_quality {cq} -pix_fmt {pix}"
        p = "slow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
        return f"-c:v libx265 -preset {p} -crf {cq} -pix_fmt {pix}"
    return ""
# ============================================================
#  CONFIGURAZIONE E TEMI
# ============================================================
CONFIG_FILE = "disagio_config.json"
THEMES = {
    "Dark Classic": {
        "bg_main": "#1a1a2e", "fg_main": "#e0e0e0",
        "bg_panel": "#20203a", "border_panel": "#2d2d4e", "fg_panel_title": "#a0a0ff",
        "btn_bg": "#2d2d4e", "btn_hover": "#3d3d6e", "btn_press": "#5050aa",
        "primary_bg": "#4444aa", "primary_border": "#6060dd", "primary_hover": "#5555cc",
        "danger_bg": "#6e2d2d", "danger_border": "#aa4444", "danger_hover": "#aa3333",
        "lic_bg": "#1a2a1a", "lic_border": "#336633", "lic_fg": "#88cc88", "lic_hover": "#224422",
        "input_bg": "#0d0d1a", "input_fg": "#00ff88",
        "text_edit_bg": "#0d1a0d", "text_edit_border": "#2d4e2d", "text_edit_fg": "#88cc88",
        "bar_bg": "#4444aa", "bar_fg": "#6060ff",
        "title_fg": "#8080ff", "file_lbl_fg": "#aaaaff", "warn_fg": "#cc8800",
        "check_bg": "#1a1a2e", "check_border": "#5050aa", "check_checked": "#6060dd", "check_checked_border": "#8080ff"
    },
    "Light Modern": {
        "bg_main": "#f0f2f5", "fg_main": "#202124",
        "bg_panel": "#ffffff", "border_panel": "#dadce0", "fg_panel_title": "#1a73e8",
        "btn_bg": "#e8eaed", "btn_hover": "#d2d5d9", "btn_press": "#bdc1c6",
        "primary_bg": "#1a73e8", "primary_border": "#174ea6", "primary_hover": "#1b66c9",
        "danger_bg": "#fce8e6", "danger_border": "#d93025", "danger_hover": "#fad2cf",
        "lic_bg": "#e6f4ea", "lic_border": "#137333", "lic_fg": "#137333", "lic_hover": "#ceead6",
        "input_bg": "#f8f9fa", "input_fg": "#202124",
        "text_edit_bg": "#f8f9fa", "text_edit_border": "#dadce0", "text_edit_fg": "#3c4043",
        "bar_bg": "#1a73e8", "bar_fg": "#669df6",
        "title_fg": "#1a73e8", "file_lbl_fg": "#1a73e8", "warn_fg": "#ea4335",
        "check_bg": "#ffffff", "check_border": "#dadce0", "check_checked": "#1a73e8", "check_checked_border": "#174ea6"
    },
    "Cyberpunk": {
        "bg_main": "#050510", "fg_main": "#00ffcc",
        "bg_panel": "#110b19", "border_panel": "#ff007f", "fg_panel_title": "#fcee0a",
        "btn_bg": "#22052a", "btn_hover": "#ff007f", "btn_press": "#d40066",
        "primary_bg": "#00ffcc", "primary_border": "#fcee0a", "primary_hover": "#00ccaa",
        "danger_bg": "#ff003c", "danger_border": "#fcee0a", "danger_hover": "#cc0030",
        "lic_bg": "#0f1108", "lic_border": "#00ffcc", "lic_fg": "#00ffcc", "lic_hover": "#1a1f0f",
        "input_bg": "#020205", "input_fg": "#fcee0a",
        "text_edit_bg": "#050510", "text_edit_border": "#00ffcc", "text_edit_fg": "#00ffcc",
        "bar_bg": "#ff007f", "bar_fg": "#fcee0a",
        "title_fg": "#ff007f", "file_lbl_fg": "#fcee0a", "warn_fg": "#ff003c",
        "check_bg": "#050510", "check_border": "#ff007f", "check_checked": "#fcee0a", "check_checked_border": "#00ffcc"
    },
    "Dracula": {
        "bg_main": "#282a36", "fg_main": "#f8f8f2",
        "bg_panel": "#44475a", "border_panel": "#6272a4", "fg_panel_title": "#bd93f9",
        "btn_bg": "#44475a", "btn_hover": "#6272a4", "btn_press": "#bd93f9",
        "primary_bg": "#bd93f9", "primary_border": "#ff79c6", "primary_hover": "#ff79c6",
        "danger_bg": "#ff5555", "danger_border": "#ffb86c", "danger_hover": "#ff6e6e",
        "lic_bg": "#282a36", "lic_border": "#50fa7b", "lic_fg": "#50fa7b", "lic_hover": "#44475a",
        "input_bg": "#21222c", "input_fg": "#f1fa8c",
        "text_edit_bg": "#21222c", "text_edit_border": "#6272a4", "text_edit_fg": "#8be9fd",
        "bar_bg": "#bd93f9", "bar_fg": "#ff79c6",
        "title_fg": "#ff79c6", "file_lbl_fg": "#8be9fd", "warn_fg": "#ffb86c",
        "check_bg": "#282a36", "check_border": "#6272a4", "check_checked": "#bd93f9", "check_checked_border": "#ff79c6"
    },
    "Nord": {
        "bg_main": "#2e3440", "fg_main": "#d8dee9",
        "bg_panel": "#3b4252", "border_panel": "#4c566a", "fg_panel_title": "#88c0d0",
        "btn_bg": "#434c5e", "btn_hover": "#4c566a", "btn_press": "#5e81ac",
        "primary_bg": "#5e81ac", "primary_border": "#81a1c1", "primary_hover": "#81a1c1",
        "danger_bg": "#bf616a", "danger_border": "#d08770", "danger_hover": "#d08770",
        "lic_bg": "#2e3440", "lic_border": "#a3be8c", "lic_fg": "#a3be8c", "lic_hover": "#3b4252",
        "input_bg": "#2e3440", "input_fg": "#ebcb8b",
        "text_edit_bg": "#2e3440", "text_edit_border": "#4c566a", "text_edit_fg": "#88c0d0",
        "bar_bg": "#81a1c1", "bar_fg": "#88c0d0",
        "title_fg": "#88c0d0", "file_lbl_fg": "#8fbcbb", "warn_fg": "#ebcb8b",
        "check_bg": "#2e3440", "check_border": "#4c566a", "check_checked": "#81a1c1", "check_checked_border": "#88c0d0"
    },
    "Terminal": {
        "bg_main": "#000000", "fg_main": "#00ff00",
        "bg_panel": "#0a0a0a", "border_panel": "#004400", "fg_panel_title": "#00ff00",
        "btn_bg": "#002200", "btn_hover": "#004400", "btn_press": "#006600",
        "primary_bg": "#006600", "primary_border": "#00ff00", "primary_hover": "#008800",
        "danger_bg": "#440000", "danger_border": "#ff0000", "danger_hover": "#660000",
        "lic_bg": "#000000", "lic_border": "#004400", "lic_fg": "#00cc00", "lic_hover": "#001100",
        "input_bg": "#000000", "input_fg": "#00ff00",
        "text_edit_bg": "#000000", "text_edit_border": "#004400", "text_edit_fg": "#00ff00",
        "bar_bg": "#006600", "bar_fg": "#00cc00",
        "title_fg": "#00ff00", "file_lbl_fg": "#00ff00", "warn_fg": "#ffff00",
        "check_bg": "#000000", "check_border": "#004400", "check_checked": "#008800", "check_checked_border": "#00ff00"
    }
}
DEFAULT_THEMES = list(THEMES.keys())
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            if "custom_themes" in cfg:
                for k, v in cfg["custom_themes"].items():
                    THEMES[k] = v
            return cfg
    except Exception:
        return {"theme": "Dark Classic", "verbose_log": False}
def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass
def get_stylesheet(theme_name):
    t = THEMES.get(theme_name, THEMES["Dark Classic"])
    return f"""
    QMainWindow, QWidget {{
        background-color: {t['bg_main']}; color: {t['fg_main']};
        font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px;
    }}
    QGroupBox {{
        border: 1px solid {t['border_panel']}; border-radius: 8px;
        margin-top: 12px; padding: 12px;
        font-weight: bold; color: {t['fg_panel_title']};
        background-color: {t['bg_panel']};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; }}
    QLabel {{ background: transparent; }}
    QPushButton {{
        background-color: {t['btn_bg']}; color: {t['fg_main']};
        border: 1px solid {t['border_panel']}; border-radius: 6px;
        padding: 8px 18px; font-weight: bold;
    }}
    QPushButton:hover  {{ background-color: {t['btn_hover']}; border-color: {t['primary_border']}; }}
    QPushButton:pressed {{ background-color: {t['btn_press']}; }}
    QPushButton#btn_primary {{
        background-color: {t['primary_bg']}; border-color: {t['primary_border']};
        color: #ffffff;
    }}
    QPushButton#btn_primary:hover {{ background-color: {t['primary_hover']}; }}
    QPushButton#btn_primary:disabled {{
        background-color: {t['btn_bg']}; color: #555555; border-color: {t['border_panel']};
    }}
    QPushButton#btn_danger {{ background-color: {t['danger_bg']}; border-color: {t['danger_border']}; color:#ffffff; }}
    QPushButton#btn_danger:hover {{ background-color: {t['danger_hover']}; }}
    QPushButton#btn_license {{
        background-color: {t['lic_bg']}; border-color: {t['lic_border']};
        color: {t['lic_fg']}; font-size: 11px; padding: 4px 10px;
    }}
    QPushButton#btn_license:hover {{ background-color: {t['lic_hover']}; }}
    QRadioButton {{ spacing: 8px; color: {t['fg_main']}; padding: 4px; background: transparent; }}
    QRadioButton::indicator {{
        width: 16px; height: 16px; border-radius: 8px;
        border: 2px solid {t['check_border']}; background: {t['check_bg']};
    }}
    QRadioButton::indicator:checked {{ background: {t['check_checked']}; border-color: {t['check_checked_border']}; }}
    QCheckBox {{ spacing: 8px; color: {t['fg_main']}; padding: 4px; background: transparent; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px; border-radius: 4px;
        border: 2px solid {t['check_border']}; background: {t['check_bg']};
    }}
    QCheckBox::indicator:checked {{ background: {t['check_checked']}; border-color: {t['check_checked_border']}; }}
    QComboBox {{
        background-color: {t['btn_bg']}; border: 1px solid {t['border_panel']};
        border-radius: 6px; padding: 6px 10px; color: {t['fg_main']}; min-width: 160px;
    }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {t['bg_panel']}; border: 1px solid {t['check_border']};
        selection-background-color: {t['primary_bg']}; color: {t['fg_main']};
    }}
    QLineEdit {{
        background-color: {t['btn_bg']}; border: 1px solid {t['border_panel']};
        border-radius: 6px; padding: 6px 10px; color: {t['fg_main']};
    }}
    QLineEdit:focus {{ border-color: {t['primary_border']}; }}
    QPlainTextEdit {{
        background-color: {t['input_bg']}; color: {t['input_fg']};
        border: 1px solid {t['border_panel']}; border-radius: 6px;
        font-family: 'JetBrains Mono','Fira Code','Courier New',monospace;
        font-size: 12px;
    }}
    QTextEdit {{
        background-color: {t['text_edit_bg']}; color: {t['text_edit_fg']};
        border: 1px solid {t['text_edit_border']}; border-radius: 6px;
        font-family: 'Courier New', monospace; font-size: 11px;
    }}
    QProgressBar {{
        background-color: {t['btn_bg']}; border: 1px solid {t['border_panel']};
        border-radius: 4px; height: 10px; text-align: center; color: transparent;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {t['bar_bg']}, stop:1 {t['bar_fg']});
        border-radius: 4px;
    }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QLabel#section_title {{
        color: {t['title_fg']}; font-size: 11px; font-weight: bold; letter-spacing: 1px;
        background: transparent;
    }}
    QLabel#file_label {{ color: {t['file_lbl_fg']}; font-size: 12px; padding: 4px; background: transparent; }}
    QLabel#auto_warn  {{ color: {t['warn_fg']}; font-size: 11px; font-style: italic; background: transparent; }}
    QLabel#license_bar {{
        color: {t['lic_border']}; font-size: 11px;
        padding: 3px 8px;
        background: {t['lic_bg']};
        border-top: 1px solid {t['lic_border']};
    }}
    QFrame#separator {{ background-color: {t['border_panel']}; max-height: 1px; }}
    """
# ============================================================
#  DIALOG EDITOR TEMI
# ============================================================
class ThemeEditorDialog(QDialog):
    def __init__(self, current_theme_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor Tema Personalizzato")
        self.resize(500, 600)
        # Load existing colors for the selected theme (or defaults)
        self.colors = dict(THEMES.get(current_theme_name, THEMES["Dark Classic"]))

        # Mapping for user‑friendly labels (e.g., bg_main → "Background Main")
        self.label_map = {k: k.replace('_', ' ').title() for k in self.colors.keys()}
        # Mapping for user-friendly labels in Italian
        self.label_map = {
            "bg_main": "🎨 Sfondo Principale",
            "fg_main": "✍️ Testo Principale",
            "bg_panel": "📝 Sfondo Pannelli",
            "border_panel": "🔳 Bordo Pannelli",
            "fg_panel_title": "🏷️ Titolo Pannelli",
            "btn_bg": "🔘 Sfondo Pulsanti",
            "btn_hover": "🔘 Pulsanti (mouse sopra)",
            "btn_press": "🔘 Pulsanti (premuto)",
            "primary_bg": "⭐ Pulsante Primario",
            "primary_border": "⭐ Bordo Primario",
            "primary_hover": "⭐ Primario (mouse sopra)",
            "danger_bg": "⚠️ Pulsante Pericolo",
            "danger_border": "⚠️ Bordo Pericolo",
            "danger_hover": "⚠️ Pericolo (mouse sopra)",
            "lic_bg": "📄 Sfondo Licenza",
            "lic_border": "📄 Bordo Licenza",
            "lic_fg": "📄 Testo Licenza",
            "lic_hover": "📄 Licenza (mouse sopra)",
            "input_bg": "💻 Sfondo Terminale",
            "input_fg": "💻 Testo Terminale",
            "text_edit_bg": "🗒️ Sfondo Area Testo",
            "text_edit_border": "🗒️ Bordo Area Testo",
            "text_edit_fg": "🗒️ Testo Area Testo",
            "bar_bg": "📊 Barra Progresso (sfondo)",
            "bar_fg": "📊 Barra Progresso (riempimento)",
            "title_fg": "🏷️ Colore Titoli Sezione",
            "file_lbl_fg": "📁 Colore Nome File",
            "warn_fg": "⚠️ Colore Avvisi",
            "check_bg": "☑️ Sfondo Checkbox/Radio",
            "check_border": "☑️ Bordo Checkbox/Radio",
            "check_checked": "☑️ Checkbox Selezionato",
            "check_checked_border": "☑️ Bordo Selezionato",
        }

        lay = QVBoxLayout(self)

        # Nome Tema
        name_lay = QHBoxLayout()
        name_lay.addWidget(QLabel("Nome Tema:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Es. Mio Tema...")
        if current_theme_name not in DEFAULT_THEMES:
            self.txt_name.setText(current_theme_name)
        name_lay.addWidget(self.txt_name)
        lay.addLayout(name_lay)

        lbl_info = QLabel("Clicca sui colori per modificarli:")
        lbl_info.setStyleSheet("background: transparent; margin-top:10px;")
        lay.addWidget(lbl_info)

        # Scrolling area for color rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        w = QWidget()
        self.grid = QGridLayout(w)

        self.color_buttons = {}
        row = 0
        for key, hex_val in self.colors.items():
            readable = self.label_map.get(key, key)
            lbl = QLabel(readable)
            lbl.setStyleSheet("background: transparent;")
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {hex_val}; border: 1px solid #ffffff;")
            # Tooltip shows current hex value
            btn.setToolTip(f"{hex_val}")
            btn.clicked.connect(lambda checked, k=key, b=btn: self._pick_color(k, b))
            self.color_buttons[key] = btn
            self.grid.addWidget(lbl, row, 0)
            self.grid.addWidget(btn, row, 1)
            row += 1

        scroll.setWidget(w)
        lay.addWidget(scroll)

        # Bottoni Azione
        btn_lay = QHBoxLayout()
        btn_save = QPushButton("Salva Tema")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)

        btn_delete = QPushButton("Elimina Tema")
        btn_delete.setObjectName("btn_danger")
        btn_delete.clicked.connect(self._delete_theme)
        if current_theme_name in DEFAULT_THEMES:
            btn_delete.hide()

        btn_lay.addWidget(btn_delete)
        btn_lay.addStretch()
        btn_lay.addWidget(btn_cancel)
        btn_lay.addWidget(btn_save)
        lay.addLayout(btn_lay)

        self.deleted = False

    def _pick_color(self, key, btn):
        from PyQt6.QtGui import QColor
        color = QColorDialog.getColor(QColor(self.colors[key]), self, "Scegli Colore")
        if color.isValid():
            hex_c = color.name()
            self.colors[key] = hex_c
            btn.setStyleSheet(f"background-color: {hex_c}; border: 1px solid #ffffff;")

    def _delete_theme(self):
        self.deleted = True
        self.accept()
# ============================================================
#  DIALOG LICENZA
# ============================================================
class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Licenza — GNU GPL v3")
        self.resize(620, 480)
        lay = QVBoxLayout(self)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(LICENSE_TEXT)
        lay.addWidget(txt)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.accept)
        lay.addWidget(btn)
# ============================================================
#  THREAD DI CONVERSIONE
# ============================================================
class ConvertThread(QThread):
    log_line  = pyqtSignal(str)
    progress  = pyqtSignal(int)
    file_done = pyqtSignal(str, bool)
    all_done  = pyqtSignal(int, int)
    def __init__(self, jobs, params):
        super().__init__()
        self.jobs   = jobs    # lista di (src, dst, src_info_or_None, is_raw_copy)
        self.params = params
        self._stop  = False
        self.verbose_log = params.get("verbose_log", False)
    def stop(self):
        self._stop = True
    def get_video_opts(self, src_info, dst_width, dst_height):
        """Ritorna la stringa di parametri video (AUTO o preset fisso)."""
        gpu    = self.params.get("gpu", "NVIDIA")
        vcodec = self.params.get("vcodec", "AV1")
        vqual  = self.params.get("vqual", "Medio")
        if vqual == "AUTO":
            return auto_compute_cq(src_info, vcodec, gpu, dst_width, dst_height)
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS[vcodec][vqual]
        return VIDEO_PRESETS.get(gpu, {}).get(vcodec, {}).get(vqual, "")
    def get_scale_filter(self, src_info, res_key):
        """Ritorna il filtro -vf scale=... o stringa vuota se nessun scaling."""
        dims = RESOLUTIONS.get(res_key)
        if dims is None:
            return ""
        dst_w, dst_h = dims
        return f"scale={dst_w}:{dst_h}:flags=lanczos:force_original_aspect_ratio=decrease,pad={dst_w}:{dst_h}:(ow-iw)/2:(oh-ih)/2"
    def get_dst_dims(self, src_info, res_key):
        """Ritorna (width, height) di destinazione per il calcolo AUTO."""
        dims = RESOLUTIONS.get(res_key)
        if dims:
            return dims
        return src_info["width"], src_info["height"]
    def build_cmd(self, src, dst, src_info):
        # modalità manuale
        manual = self.params.get("manual_cmd", "")
        if manual:
            filled = manual.replace("{INPUT}", src).replace(
                "{OUTPUT}", str(Path(dst).with_suffix("")))
            parts = filled.split()
            return parts[:-1] + ["-progress", "pipe:1"] + [parts[-1]]
        mode    = self.params["mode"]
        # ── modalità immagine ──
        if mode == "image":
            fmt     = self.params.get("img_fmt", "jpg")
            quality = self.params.get("img_quality", 80)
            img_args = build_image_ffmpeg_args(fmt, quality)
            return [FFMPEG_BIN, "-i", src] + img_args + [dst, "-y"]
        sample  = self.params["sample_rate"]
        hwaccel = self.params.get("hwaccel", True)
        res_key = self.params.get("resolution", "Mantieni originale")
        sr_flag = [] if sample == "Mantieni originale" else ["-ar", sample.replace(" Hz", "")]
        hw_flag = ["-hwaccel", "auto"] if hwaccel else []
        audio_opts = self.params["audio_preset"].split()
        cmd = [FFMPEG_BIN] + hw_flag + ["-i", src]
        if mode == "audio":
            cmd += ["-vn"] + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]
        else:
            dst_w, dst_h = self.get_dst_dims(src_info, res_key)
            video_opts   = self.get_video_opts(src_info, dst_w, dst_h).split()
            scale_filter = self.get_scale_filter(src_info, res_key)
            if scale_filter:
                cmd += ["-vf", scale_filter]
            cmd += video_opts + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]
        return cmd
    def get_duration(self, src):
        try:
            r = subprocess.run(
                [FFPROBE_BIN, "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", src],
                capture_output=True, text=True, timeout=15
            )
            return float(r.stdout.strip())
        except Exception:
            return 0.0
    def run(self):
        ok = err = 0
        total = len(self.jobs)
        for idx, job in enumerate(self.jobs):
            if self._stop:
                break
            # job è una tupla (src, dst, src_info, is_raw_copy)
            src, dst, src_info, is_raw_copy = job
            fname = os.path.basename(src)
            self.log_line.emit(f"\n{'─'*50}")
            self.log_line.emit(f"[{idx+1}/{total}] {fname}")
            self.log_line.emit(f"  → {dst}")
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            # ── Copia RAW (nessuna conversione) ──
            if is_raw_copy:
                self.log_line.emit("  [RAW] Copia originale intatta...")
                try:
                    shutil.copy2(src, dst)
                    success = os.path.exists(dst) and os.path.getsize(dst) > 0
                except Exception as e:
                    self.log_line.emit(f"  ERRORE copia RAW: {e}")
                    success = False
                self.progress.emit(int((idx+1) / total * 100))
                if success:
                    ok += 1
                    self.log_line.emit("  ✓ OK (RAW copiato)")
                else:
                    err += 1
                    self.log_line.emit("  ✗ ERRORE copia RAW")
                self.file_done.emit(fname, success)
                continue
            # ── Conversione FFmpeg ──
            # se AUTO, mostra i parametri calcolati
            if self.params.get("vqual") == "AUTO" and self.params["mode"] == "video":
                res_key = self.params.get("resolution", "Mantieni originale")
                dst_w, dst_h = self.get_dst_dims(src_info, res_key)
                computed = self.get_video_opts(src_info, dst_w, dst_h)
                self.log_line.emit(f"  [AUTO] {computed}")
            duration = self.get_duration(src) if self.params["mode"] != "image" else 0.0
            cmd = self.build_cmd(src, dst, src_info)
            self.log_line.emit("  $ " + " ".join(cmd))
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                for line in proc.stdout:
                    if self._stop:
                        proc.terminate(); break
                    line = line.rstrip()
                    if line.startswith("out_time_ms="):
                        try:
                            ms  = int(line.split("=")[1])
                            t   = ms / 1_000_000
                            if duration > 0:
                                pct = min(int(t / duration * 100), 99)
                                self.progress.emit(int((idx + pct/100) / total * 100))
                        except Exception:
                            pass
                    elif line.startswith("progress=end"):
                        self.progress.emit(int((idx+1) / total * 100))
                    elif line.strip():
                        if self.verbose_log:
                            if not line.startswith("out_time_ms=") and not line.startswith("progress="):
                                self.log_line.emit("  " + line)
                        else:
                            if not any(line.startswith(p) for p in
                                ["frame=","fps=","stream_","bitrate=","speed=",
                                 "out_time","total_size","dup_frames","drop_frames", "progress="]):
                                self.log_line.emit("  " + line)
                proc.wait()
                # Per le immagini non si usa -progress pipe:1, quindi non arriva progress=end
                if self.params["mode"] == "image":
                    self.progress.emit(int((idx+1) / total * 100))
                success = (proc.returncode == 0 and
                           os.path.exists(dst) and os.path.getsize(dst) > 0)
            except Exception as e:
                self.log_line.emit(f"  ERRORE: {e}")
                success = False
            if success:
                ok += 1
                self.log_line.emit("  ✓ OK")
            else:
                err += 1
                self.log_line.emit("  ✗ ERRORE — file originale intatto")
                try:
                    if os.path.exists(dst): os.remove(dst)
                except Exception:
                    pass
            self.file_done.emit(fname, success)
        self.all_done.emit(ok, err)
# ============================================================
#  FINESTRA PRINCIPALE
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DISAGIO PRODUCTION CONVERTER")
        self.setMinimumSize(880, 860)
        self.resize(960, 940)
        self.params = {}
        self.jobs   = []
        self.thread = None
        self._build_ui()
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(16, 16, 16, 8)
        # ── titolo + licenza + tema ───────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("DISAGIO PRODUCTION CONVERTER")
        title.setFont(QFont("monospace", 14, QFont.Weight.Bold))
        title.setStyleSheet("color:#8080ff; letter-spacing:2px; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(QLabel("Tema:"))
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(list(THEMES.keys()))
        cfg = load_config()
        self.cmb_theme.setCurrentText(cfg.get("theme", "Dark Classic"))
        self.cmb_theme.currentTextChanged.connect(self._change_theme)
        title_row.addWidget(self.cmb_theme)
        btn_edit_theme = QPushButton(" Modifica Tema ")
        # Use a generic icon to indicate theme editing (standard "preferences" icon)
        try:
            from PyQt6.QtGui import QIcon
            btn_edit_theme.setIcon(QIcon.fromTheme("preferences-desktop-theme"))
        except Exception:
            pass
        btn_edit_theme.setToolTip("Modifica o crea un tema personalizzato")
        btn_edit_theme.clicked.connect(self._edit_theme)
        title_row.addWidget(btn_edit_theme)
        title_row.addSpacing(10)
        btn_lic = QPushButton("⚖  GPL v3")
        btn_lic.setObjectName("btn_license")
        btn_lic.setToolTip("Visualizza la licenza GNU GPL v3")
        btn_lic.clicked.connect(self._show_license)
        title_row.addWidget(btn_lic)
        root.addLayout(title_row)
        sep = QFrame(); sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        opts_w = QWidget()
        self.opts_layout = QVBoxLayout(opts_w)
        self.opts_layout.setSpacing(8)
        scroll.setWidget(opts_w)
        root.addWidget(scroll, stretch=3)
        # ── STEP 1 ────────────────────────────────────────────
        self._section("STEP 1 — Sorgente")
        row1 = QHBoxLayout()
        self.bg_mode = QButtonGroup(self)
        self.rb_single = QRadioButton("File singolo")
        self.rb_folder = QRadioButton("Cartella intera")
        self.rb_single.setChecked(True)
        self.bg_mode.addButton(self.rb_single, 0)
        self.bg_mode.addButton(self.rb_folder, 1)
        self.rb_single.toggled.connect(self._on_mode_changed)
        row1.addWidget(self.rb_single); row1.addWidget(self.rb_folder)
        row1.addStretch()
        self.opts_layout.addLayout(row1)
        frow = QHBoxLayout()
        self.lbl_file = QLabel("Nessun file selezionato")
        self.lbl_file.setObjectName("file_label")
        self.lbl_file.setWordWrap(True)
        self.btn_browse = QPushButton("Sfoglia…")
        self.btn_browse.clicked.connect(self._browse)
        frow.addWidget(self.lbl_file, stretch=1)
        frow.addWidget(self.btn_browse)
        self.opts_layout.addLayout(frow)
        self._sep()
        # ── STEP 2 ────────────────────────────────────────────
        self._section("STEP 2 — Tipo output")
        row2 = QHBoxLayout()
        self.bg_type = QButtonGroup(self)
        self.rb_video = QRadioButton("Video + Audio")
        self.rb_audio = QRadioButton("Solo Audio")
        self.rb_image = QRadioButton("Immagini")
        self.rb_video.setChecked(True)
        self.bg_type.addButton(self.rb_video, 0)
        self.bg_type.addButton(self.rb_audio, 1)
        self.bg_type.addButton(self.rb_image, 2)
        self.rb_video.toggled.connect(self._on_type_changed)
        self.rb_audio.toggled.connect(self._on_type_changed)
        self.rb_image.toggled.connect(self._on_type_changed)
        row2.addWidget(self.rb_video); row2.addWidget(self.rb_audio); row2.addWidget(self.rb_image)
        row2.addStretch()
        self.opts_layout.addLayout(row2)
        self._sep()
        # ── STEP 3: video ─────────────────────────────────────
        self.grp_video = QGroupBox("STEP 3 — Video")
        vlay = QVBoxLayout(self.grp_video)
        # GPU
        gpu_row = QHBoxLayout()
        gpu_row.addWidget(QLabel("Encoder GPU:"))
        self.bg_gpu = QButtonGroup(self)
        for i, g in enumerate(GPU_OPTIONS):
            rb = QRadioButton(g)
            if g == "NVIDIA": rb.setChecked(True)
            self.bg_gpu.addButton(rb, i)
            gpu_row.addWidget(rb)
            rb.toggled.connect(self._update_cmd_preview)
        gpu_row.addStretch()
        vlay.addLayout(gpu_row)
        # hwaccel
        hw_row = QHBoxLayout()
        self.chk_hwaccel = QCheckBox("Accelerazione hardware decodifica  (-hwaccel auto)")
        self.chk_hwaccel.setChecked(True)
        self.chk_hwaccel.toggled.connect(self._update_cmd_preview)
        hw_row.addWidget(self.chk_hwaccel); hw_row.addStretch()
        vlay.addLayout(hw_row)
        # container + codec
        cc_row = QHBoxLayout()
        cc_row.addWidget(QLabel("Container:"))
        self.cmb_container = QComboBox()
        self.cmb_container.addItems(CONTAINER_CODECS.keys())
        self.cmb_container.currentTextChanged.connect(self._on_container_changed)
        cc_row.addWidget(self.cmb_container)
        cc_row.addSpacing(20)
        cc_row.addWidget(QLabel("Codec video:"))
        self.cmb_vcodec = QComboBox()
        self.cmb_vcodec.currentTextChanged.connect(self._update_cmd_preview)
        cc_row.addWidget(self.cmb_vcodec); cc_row.addStretch()
        vlay.addLayout(cc_row)
        # qualità + AUTO
        vq_row = QHBoxLayout()
        vq_row.addWidget(QLabel("Qualità video:"))
        self.bg_vqual = QButtonGroup(self)
        for i, q in enumerate(["Alto", "Medio", "Basso", "AUTO"]):
            rb = QRadioButton(q)
            if q == "Medio": rb.setChecked(True)
            self.bg_vqual.addButton(rb, i)
            rb.toggled.connect(self._on_vqual_changed)
            vq_row.addWidget(rb)
        self.lbl_auto_warn = QLabel(
            "⚠ Il sistema AUTO è una stima — può commettere errori su sorgenti atipici"
        )
        self.lbl_auto_warn.setObjectName("auto_warn")
        self.lbl_auto_warn.setVisible(False)
        vq_row.addWidget(self.lbl_auto_warn)
        vq_row.addStretch()
        vlay.addLayout(vq_row)
        # risoluzione output
        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("Risoluzione output:"))
        self.cmb_res = QComboBox()
        self.cmb_res.addItems(RESOLUTIONS.keys())
        self.cmb_res.setCurrentText("Mantieni originale")
        self.cmb_res.currentTextChanged.connect(self._update_cmd_preview)
        res_row.addWidget(self.cmb_res)
        res_row.addWidget(QLabel(
            "<small style='color:#666688'>  Aspect ratio originale preservato  |  filtro: lanczos</small>"
        ))
        res_row.addStretch()
        vlay.addLayout(res_row)
        self.opts_layout.addWidget(self.grp_video)
        # ── STEP 3 (immagini): immagini ───────────────────────
        self.grp_image = QGroupBox("STEP 3 — Immagini")
        ilay = QVBoxLayout(self.grp_image)
        ifmt_row = QHBoxLayout()
        ifmt_row.addWidget(QLabel("Formato di output:"))
        self.cmb_imgfmt = QComboBox()
        self.cmb_imgfmt.addItems(IMAGE_OUTPUT_FORMATS.keys())
        self.cmb_imgfmt.currentTextChanged.connect(self._on_imgfmt_changed)
        ifmt_row.addWidget(self.cmb_imgfmt); ifmt_row.addStretch()
        ilay.addLayout(ifmt_row)
        # Slider qualità
        ilay.addSpacing(4)
        slider_header = QHBoxLayout()
        slider_header.addWidget(QLabel("Qualità / Compressione:"))
        slider_header.addStretch()
        ilay.addLayout(slider_header)
        # Etichette sinistra/destra con slider al centro
        slider_row = QHBoxLayout()
        lbl_low = QLabel("Bassa qualità\n(File piccolo)")
        lbl_low.setStyleSheet("color:#cc7700; font-size:11px; text-align:right;")
        lbl_low.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_low.setFixedWidth(110)
        self.sld_imgqual = QSlider(Qt.Orientation.Horizontal)
        self.sld_imgqual.setMinimum(1)
        self.sld_imgqual.setMaximum(100)
        self.sld_imgqual.setValue(82)
        self.sld_imgqual.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sld_imgqual.setTickInterval(10)
        self.sld_imgqual.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sld_imgqual.valueChanged.connect(self._on_imgqual_changed)
        lbl_high = QLabel("Alta qualità\n(File grande)")
        lbl_high.setStyleSheet("color:#44cc88; font-size:11px;")
        lbl_high.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_high.setFixedWidth(110)
        slider_row.addWidget(lbl_low)
        slider_row.addWidget(self.sld_imgqual)
        slider_row.addWidget(lbl_high)
        ilay.addLayout(slider_row)
        # Etichetta live con la descrizione qualità
        self.lbl_imgqual_val = QLabel(image_quality_label(82))
        self.lbl_imgqual_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imgqual_val.setStyleSheet(
            "color:#a0d0ff; font-size:12px; font-weight:bold; padding:4px;"
        )
        ilay.addWidget(self.lbl_imgqual_val)
        # Avviso BMP (nessuna compressione)
        self.lbl_bmp_warn = QLabel(
            "ℹ  Il formato BMP non supporta la compressione — lo slider non ha effetto."
        )
        self.lbl_bmp_warn.setStyleSheet("color:#888888; font-size:11px; font-style:italic;")
        self.lbl_bmp_warn.setVisible(False)
        ilay.addWidget(self.lbl_bmp_warn)
        # Nota RAW (mostrata solo in modalità cartella)
        self.lbl_raw_note = QLabel(
            "📁  I file RAW trovati nella cartella verranno copiati intatti in una "
            "sottocartella separata  \"FOTO_RAW\"  accanto ai file convertiti."
        )
        self.lbl_raw_note.setWordWrap(True)
        self.lbl_raw_note.setStyleSheet(
            "color:#aaaaff; font-size:11px; font-style:italic; padding:4px 0;"
        )
        ilay.addWidget(self.lbl_raw_note)
        self.opts_layout.addWidget(self.grp_image)
        # ── STEP 4: audio ─────────────────────────────────────
        self.grp_audio = QGroupBox("STEP 4 — Audio")
        alay = QVBoxLayout(self.grp_audio)
        ac_row = QHBoxLayout()
        ac_row.addWidget(QLabel("Codec audio:"))
        self.cmb_acodec = QComboBox()
        self.cmb_acodec.addItems(AUDIO_CODECS)
        self.cmb_acodec.currentTextChanged.connect(self._update_cmd_preview)
        ac_row.addWidget(self.cmb_acodec); ac_row.addStretch()
        alay.addLayout(ac_row)
        aq_row = QHBoxLayout()
        aq_row.addWidget(QLabel("Qualità audio:"))
        self.bg_aqual = QButtonGroup(self)
        for i, q in enumerate(["Alto", "Medio", "Basso"]):
            rb = QRadioButton(q)
            if q == "Medio": rb.setChecked(True)
            self.bg_aqual.addButton(rb, i)
            rb.toggled.connect(self._update_cmd_preview)
            aq_row.addWidget(rb)
        aq_row.addStretch()
        alay.addLayout(aq_row)
        sr_row = QHBoxLayout()
        sr_row.addWidget(QLabel("Sample rate:"))
        self.cmb_sample = QComboBox()
        self.cmb_sample.addItems(SAMPLE_RATES)
        self.cmb_sample.setCurrentText("48000 Hz")
        self.cmb_sample.currentTextChanged.connect(self._update_cmd_preview)
        sr_row.addWidget(self.cmb_sample); sr_row.addStretch()
        alay.addLayout(sr_row)
        self.opts_layout.addWidget(self.grp_audio)
        # ── STEP 5: nome / prefisso ───────────────────────────
        self.grp_name = QGroupBox("STEP 5 — Nome file output")
        nlay = QHBoxLayout(self.grp_name)
        self.lbl_name = QLabel("Nome (senza estensione):")
        nlay.addWidget(self.lbl_name)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Lascia vuoto per mantenere il nome originale")
        nlay.addWidget(self.txt_name)
        self.opts_layout.addWidget(self.grp_name)
        # ── comando ffmpeg ─────────────────────────────────────
        self.grp_cmd = QGroupBox("Comando ffmpeg (aggiornato live)")
        clay = QVBoxLayout(self.grp_cmd)
        self.txt_cmd = QLineEdit()
        self.txt_cmd.setReadOnly(True)
        self.txt_cmd.setFont(QFont("monospace", 11))
        self.txt_cmd.setStyleSheet(
            "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
            "border-radius:6px; padding:6px 10px;")
        clay.addWidget(self.txt_cmd)
        cbr = QHBoxLayout()
        self.btn_manual = QPushButton("✏  Abilita modifica manuale")
        self.btn_manual.setCheckable(True)
        self.btn_manual.clicked.connect(self._toggle_manual)
        self.lbl_hint = QLabel("Usa {INPUT} e {OUTPUT} come segnaposto")
        self.lbl_hint.setStyleSheet("color:#666688; font-size:11px;")
        self.lbl_hint.setVisible(False)
        cbr.addWidget(self.btn_manual)
        cbr.addWidget(self.lbl_hint)
        cbr.addStretch()
        clay.addLayout(cbr)
        self.opts_layout.addWidget(self.grp_cmd)
        # init
        self._on_container_changed(self.cmb_container.currentText())
        self._on_type_changed()
        self._on_imgfmt_changed(self.cmb_imgfmt.currentText())
        # ── CONVERTI ──────────────────────────────────────────
        self.btn_go = QPushButton("▶  CONVERTI")
        self.btn_go.setObjectName("btn_primary")
        self.btn_go.setMinimumHeight(42)
        self.btn_go.setFont(QFont("monospace", 12, QFont.Weight.Bold))
        self.btn_go.clicked.connect(self._start)
        root.addWidget(self.btn_go)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)
        # Intestazione Terminale
        term_lay = QHBoxLayout()
        lbl_term = QLabel("Log Terminale:")
        lbl_term.setStyleSheet("color:#8080ff; font-size:11px; font-weight:bold; background: transparent;")
        term_lay.addWidget(lbl_term)
        term_lay.addStretch()

        self.chk_verbose = QCheckBox("Mostra Log Completo")
        cfg = load_config()
        self.chk_verbose.setChecked(cfg.get("verbose_log", False))
        self.chk_verbose.stateChanged.connect(self._save_verbose)
        term_lay.addWidget(self.chk_verbose)
        root.addLayout(term_lay)
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(160)
        self.terminal.setPlaceholderText("L'output di ffmpeg apparirà qui…")
        root.addWidget(self.terminal, stretch=2)
        self.btn_stop = QPushButton("■  INTERROMPI")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setVisible(False)
        self.btn_stop.clicked.connect(self._stop)
        root.addWidget(self.btn_stop)
        # ── barra licenza in fondo ────────────────────────────
        lic_bar = QLabel(
            "  DISAGIO PRODUCTION CONVERTER  —  Open source, licenza GNU GPL v3  "
            "—  github.com/playerinthebug/disagio-converter"
        )
        lic_bar.setObjectName("license_bar")
        lic_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lic_bar)
    # ----------------------------------------------------------
    def _section(self, text):
        lbl = QLabel(text.upper()); lbl.setObjectName("section_title")
        self.opts_layout.addWidget(lbl)
    def _sep(self):
        f = QFrame(); f.setObjectName("separator")
        f.setFrameShape(QFrame.Shape.HLine)
        self.opts_layout.addWidget(f)
    def _show_license(self):
        LicenseDialog(self).exec()
    def _change_theme(self, theme_name):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme_name))
        cfg = load_config()
        cfg["theme"] = theme_name
        cfg["verbose_log"] = getattr(self, 'chk_verbose', QCheckBox()).isChecked()
        save_config(cfg)
    def _save_verbose(self):
        cfg = load_config()
        cfg["verbose_log"] = self.chk_verbose.isChecked()
        save_config(cfg)
    def _edit_theme(self):
        curr = self.cmb_theme.currentText()
        dlg = ThemeEditorDialog(curr, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            cfg = load_config()
            if "custom_themes" not in cfg:
                cfg["custom_themes"] = {}
            # If theme was deleted via dialog
            if dlg.deleted:
                if curr in cfg["custom_themes"]:
                    del cfg["custom_themes"][curr]
                if curr in THEMES:
                    del THEMES[curr]
                idx = self.cmb_theme.findText(curr)
                if idx >= 0:
                    self.cmb_theme.removeItem(idx)
                self.cmb_theme.setCurrentText("Dark Classic")
            else:
                name = dlg.txt_name.text().strip()
                if not name:
                    name = "Tema Custom"

                # Rimuovi vecchio nome custom se rinominato
                if curr != name and curr not in DEFAULT_THEMES and curr in cfg["custom_themes"]:
                    del cfg["custom_themes"][curr]
                    if curr in THEMES:
                        del THEMES[curr]
                    idx = self.cmb_theme.findText(curr)
                    if idx >= 0:
                        self.cmb_theme.removeItem(idx)

                cfg["custom_themes"][name] = dlg.colors
                THEMES[name] = dlg.colors
                if self.cmb_theme.findText(name) < 0:
                    self.cmb_theme.addItem(name)

                # Salva PRIMA il tema nel JSON, poi cambia tema
                cfg["theme"] = name
                cfg["verbose_log"] = getattr(self, 'chk_verbose', QCheckBox()).isChecked()
                save_config(cfg)

                self.cmb_theme.blockSignals(True)
                self.cmb_theme.setCurrentText(name)
                self.cmb_theme.blockSignals(False)
                self._change_theme(name)
                # Applica solo lo stylesheet, senza ri-salvare (già salvato sopra)
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(get_stylesheet(name))

    def _on_mode_changed(self):
        is_single = self.rb_single.isChecked()
        is_image  = hasattr(self, "rb_image") and self.rb_image.isChecked()
        is_video  = hasattr(self, "rb_video") and self.rb_video.isChecked()
        # Numero step del nome dipende dal tipo di output
        if is_video:
            name_step = "STEP 5"
        else:  # audio o immagine: un pannello in meno
            name_step = "STEP 4"
        if is_single:
            self.grp_name.setTitle(f"{name_step} \u2014 Nome file output")
            self.lbl_name.setText("Nome (senza estensione):")
            self.txt_name.setPlaceholderText("Lascia vuoto per mantenere il nome originale")
        else:
            self.grp_name.setTitle(f"{name_step} \u2014 Prefisso file output")
            self.lbl_name.setText("Prefisso:")
            self.txt_name.setPlaceholderText("Lascia vuoto per nessun prefisso")
        # Nota RAW visibile solo se modalit\u00e0 immagine + cartella
        if hasattr(self, "lbl_raw_note"):
            self.lbl_raw_note.setVisible(is_image and not is_single)
        self._update_cmd_preview()
    def _on_type_changed(self):
        is_video = self.rb_video.isChecked()
        is_audio = self.rb_audio.isChecked()
        is_image = self.rb_image.isChecked()
        is_folder = self.rb_folder.isChecked()
        self.grp_video.setVisible(is_video)
        self.grp_image.setVisible(is_image)
        self.grp_audio.setVisible(not is_image)
        # Nota RAW visibile solo in modalità cartella
        if hasattr(self, "lbl_raw_note"):
            self.lbl_raw_note.setVisible(is_image and is_folder)
        # Numera gli step dinamicamente in base alla modalità
        if is_video:
            self.grp_audio.setTitle("STEP 4 — Audio")
            name_step = "STEP 5"
        elif is_audio:
            self.grp_audio.setTitle("STEP 3 — Audio")
            name_step = "STEP 4"
        else:  # image
            name_step = "STEP 4"
        is_single = self.rb_single.isChecked()
        self.grp_name.setTitle(
            f"{name_step} — Nome file output" if is_single
            else f"{name_step} — Prefisso file output"
        )
        self._update_cmd_preview()
    def _on_vqual_changed(self):
        btn = self.bg_vqual.checkedButton()
        is_auto = btn and btn.text() == "AUTO"
        self.lbl_auto_warn.setVisible(is_auto)
        # in AUTO il comando preview non può mostrare valori reali
        if is_auto:
            self.txt_cmd.setText(
                "ffmpeg [parametri calcolati automaticamente per ogni file — vedi terminale durante la conversione]"
            )
        else:
            self._update_cmd_preview()
    def _on_imgfmt_changed(self, fmt_label):
        fmt = IMAGE_OUTPUT_FORMATS.get(fmt_label, "jpg")
        is_bmp = (fmt == "bmp")
        self.sld_imgqual.setEnabled(not is_bmp)
        self.lbl_bmp_warn.setVisible(is_bmp)
        if not is_bmp:
            self._on_imgqual_changed(self.sld_imgqual.value())
        else:
            self.lbl_imgqual_val.setText("BMP — nessuna compressione")
        self._update_cmd_preview()
    def _on_imgqual_changed(self, val):
        self.lbl_imgqual_val.setText(image_quality_label(val))
        self._update_cmd_preview()
    def _on_container_changed(self, container):
        codecs = CONTAINER_CODECS.get(container, [])
        self.cmb_vcodec.clear()
        self.cmb_vcodec.addItems(codecs)
        is_gpu = all(c not in ("DNxHR", "ProRes") for c in codecs)
        for btn in self.bg_gpu.buttons():
            btn.setEnabled(is_gpu)
        self.chk_hwaccel.setEnabled(is_gpu)
        self._update_cmd_preview()
    def _get_selected_gpu(self):
        btn = self.bg_gpu.checkedButton()
        return btn.text() if btn else "NVIDIA"
    def _get_video_preset_str(self):
        gpu    = self._get_selected_gpu()
        vcodec = self.cmb_vcodec.currentText()
        vqual  = (self.bg_vqual.checkedButton().text()
                  if self.bg_vqual.checkedButton() else "Medio")
        if vqual == "AUTO":
            return "[AUTO]"
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS[vcodec][vqual]
        return VIDEO_PRESETS.get(gpu, {}).get(vcodec, {}).get(vqual, "")
    def _update_cmd_preview(self):
        if hasattr(self, "btn_manual") and self.btn_manual.isChecked():
            return
        btn = self.bg_vqual.checkedButton() if hasattr(self, "bg_vqual") else None
        if btn and btn.text() == "AUTO" and not (hasattr(self, "rb_image") and self.rb_image.isChecked()):
            return  # gestito da _on_vqual_changed
        # ── modalità immagine ──
        if hasattr(self, "rb_image") and self.rb_image.isChecked():
            fmt_label = self.cmb_imgfmt.currentText() if hasattr(self, "cmb_imgfmt") else "JPG (.jpg)"
            fmt  = IMAGE_OUTPUT_FORMATS.get(fmt_label, "jpg")
            qual = self.sld_imgqual.value() if hasattr(self, "sld_imgqual") else 82
            args = build_image_ffmpeg_args(fmt, qual)
            args_str = " ".join(args)
            cmd = f"ffmpeg -i {{INPUT}} {args_str} {{OUTPUT}}.{fmt} -y"
            if hasattr(self, "txt_cmd"):
                self.txt_cmd.setText(cmd.strip())
            return
        mode    = "audio" if self.rb_audio.isChecked() else "video"
        acodec  = self.cmb_acodec.currentText()
        aqual   = (self.bg_aqual.checkedButton().text()
                   if self.bg_aqual.checkedButton() else "Medio")
        sample  = self.cmb_sample.currentText()
        audio_p = AUDIO_PRESETS.get(acodec, {}).get(aqual, "")
        if sample != "Mantieni originale":
            audio_p += f" -ar {sample.replace(' Hz','')}"
        hw  = "-hwaccel auto " if self.chk_hwaccel.isChecked() else ""
        res = self.cmb_res.currentText() if hasattr(self, "cmb_res") else "Mantieni originale"
        res_str = "" if res == "Mantieni originale" else f" -vf scale=W:H:flags=lanczos"
        if mode == "audio":
            ext = AUDIO_ONLY_EXT.get(acodec, "wav")
            cmd = f"ffmpeg {hw}-i {{INPUT}} -vn {audio_p} {{OUTPUT}}.{ext} -y"
        else:
            video_p = self._get_video_preset_str()
            ext_map = {"MKV (.mkv)":"mkv","MP4 (.mp4)":"mp4","MOV (.mov)":"mov"}
            ext = ext_map.get(self.cmb_container.currentText(), "mkv")
            cmd = f"ffmpeg {hw}-i {{INPUT}}{res_str} {video_p} {audio_p} {{OUTPUT}}.{ext} -y"
        if hasattr(self, "txt_cmd"):
            self.txt_cmd.setText(cmd.strip())
    def _toggle_manual(self, checked):
        self.txt_cmd.setReadOnly(not checked)
        self.lbl_hint.setVisible(checked)
        controls = (
            [self.rb_video, self.rb_audio, self.rb_image, self.rb_single, self.rb_folder,
             self.cmb_container, self.cmb_vcodec, self.cmb_acodec,
             self.cmb_sample, self.chk_hwaccel, self.cmb_res,
             self.cmb_imgfmt, self.sld_imgqual]
            + list(self.bg_vqual.buttons())
            + list(self.bg_aqual.buttons())
            + list(self.bg_gpu.buttons())
        )
        for w in controls:
            w.setEnabled(not checked)
        if checked:
            self.btn_manual.setText("🔒  Torna a modalità automatica")
            self.txt_cmd.setStyleSheet(
                "background:#0d0d1a; color:#ffcc00; border:1px solid #aaaa00;"
                "border-radius:6px; padding:6px 10px;")
        else:
            self.btn_manual.setText("✏  Abilita modifica manuale")
            self.txt_cmd.setStyleSheet(
                "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
                "border-radius:6px; padding:6px 10px;")
            self._update_cmd_preview()
    def _browse(self):
        if self.rb_folder.isChecked():
            path = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        elif self.rb_image.isChecked():
            exts_img = " ".join(f"*{e}" for e in sorted(IMAGE_EXTENSIONS))
            exts_raw = " ".join(f"*{e}" for e in sorted(RAW_EXTENSIONS))
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleziona immagine",
                filter=f"Immagini ({exts_img});;File RAW ({exts_raw});;Tutti i file (*)")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleziona file",
                filter="Video e Audio (*.mp4 *.mkv *.mov *.avi *.webm *.flv "
                       "*.mts *.m2ts *.ts *.wmv *.mp3 *.flac *.wav *.aac "
                       "*.m4a *.ogg *.opus *.wma *.aiff);;Tutti i file (*)")
        if path:
            self.lbl_file.setText(path)
            if self.rb_single.isChecked():
                self.txt_name.setText(Path(path).stem)
    # ----------------------------------------------------------
    def _collect_params(self):
        if self.rb_image.isChecked():
            mode = "image"
        elif self.rb_audio.isChecked():
            mode = "audio"
        else:
            mode = "video"
        vcodec  = self.cmb_vcodec.currentText()
        acodec  = self.cmb_acodec.currentText()
        vqual   = (self.bg_vqual.checkedButton().text()
                   if self.bg_vqual.checkedButton() else "Medio")
        aqual   = (self.bg_aqual.checkedButton().text()
                   if self.bg_aqual.checkedButton() else "Medio")
        gpu     = self._get_selected_gpu()
        sample  = self.cmb_sample.currentText()
        hwaccel = self.chk_hwaccel.isChecked()
        res_key = self.cmb_res.currentText()
        ext_map   = {"MKV (.mkv)":"mkv","MP4 (.mp4)":"mp4","MOV (.mov)":"mov"}
        video_ext = ext_map.get(self.cmb_container.currentText(), "mkv")
        audio_ext = AUDIO_ONLY_EXT.get(acodec, "wav")
        # parametri immagine
        img_fmt_label = self.cmb_imgfmt.currentText()
        img_fmt       = IMAGE_OUTPUT_FORMATS.get(img_fmt_label, "jpg")
        img_quality   = self.sld_imgqual.value()
        return {
            "mode":         mode,
            "video_ext":    video_ext,
            "audio_ext":    audio_ext,
            "audio_preset": AUDIO_PRESETS.get(acodec, {}).get(aqual, ""),
            "sample_rate":  sample,
            "gpu":          gpu,
            "hwaccel":      hwaccel,
            "vcodec":       vcodec,
            "acodec":       acodec,
            "vqual":        vqual,
            "aqual":        aqual,
            "resolution":   res_key,
            "img_fmt":      img_fmt,
            "img_quality":  img_quality,
            "verbose_log":  getattr(self, "chk_verbose", QCheckBox()).isChecked(),
        }
    def _unique_path(self, dst):
        if not os.path.exists(dst): return dst
        stem = Path(dst).stem; ext = Path(dst).suffix; d = Path(dst).parent
        i = 1
        while True:
            c = d / f"{stem}_{i}{ext}"
            if not c.exists(): return str(c)
            i += 1
    def _collect_jobs(self, params):
        path      = self.lbl_file.text()
        is_single = self.rb_single.isChecked()
        mode      = params["mode"]
        prefix    = self.txt_name.text().strip()
        is_auto   = (params.get("vqual") == "AUTO" and mode == "video")
        jobs      = []
        dummy_info = {
            "codec":"h264","width":1920,"height":1080,
            "fps":25.0,"bitrate":8_000_000,"depth":8,"profile":"0"
        }
        if mode == "image":
            # ── modalità immagine ──────────────────────────────
            img_fmt    = params["img_fmt"]
            valid_exts = IMAGE_EXTENSIONS | RAW_EXTENSIONS
            if is_single:
                if not os.path.isfile(path): return []
                ext_src = Path(path).suffix.lower()
                if ext_src in RAW_EXTENSIONS:
                    # file singolo RAW → non supportato in modalità singola
                    # lo trattiamo come copia
                    stem = prefix if prefix else Path(path).stem
                    dst  = str(Path(path).parent / f"{stem}{ext_src}")
                    jobs.append((path, self._unique_path(dst), dummy_info, True))
                else:
                    stem = prefix if prefix else Path(path).stem
                    dst  = str(Path(path).parent / f"{stem}.{img_fmt}")
                    jobs.append((path, self._unique_path(dst), dummy_info, False))
            else:
                if not os.path.isdir(path): return []
                out_dir = os.path.join(path, "CONVERTITI_DISAGIO")
                raw_dir = os.path.join(path, "FOTO_RAW")
                for root_d, dirs, files in os.walk(path):
                    # Salta le cartelle di output
                    dirs[:] = [d for d in dirs
                                if os.path.join(root_d, d) != out_dir
                                and os.path.join(root_d, d) != raw_dir]
                    for f in sorted(files):
                        ext_f = Path(f).suffix.lower()
                        if ext_f not in valid_exts: continue
                        src  = os.path.join(root_d, f)
                        rel  = os.path.relpath(root_d, path)
                        stem = f"{prefix}_{Path(f).stem}" if prefix else Path(f).stem
                        if ext_f in RAW_EXTENSIONS:
                            # copia RAW nella cartella FOTO_RAW
                            dst = os.path.join(raw_dir, rel, f"{Path(f).stem}{ext_f}")
                            jobs.append((src, self._unique_path(dst), dummy_info, True))
                        else:
                            dst = os.path.join(out_dir, rel, f"{stem}.{img_fmt}")
                            jobs.append((src, self._unique_path(dst), dummy_info, False))
        else:
            # ── modalità video/audio ───────────────────────────
            out_ext    = params["audio_ext"] if mode == "audio" else params["video_ext"]
            valid_exts = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS
            if is_single:
                if not os.path.isfile(path): return []
                stem = prefix if prefix else Path(path).stem
                dst  = str(Path(path).parent / f"{stem}.{out_ext}")
                info = probe_video(path) if is_auto else dummy_info
                jobs.append((path, self._unique_path(dst), info, False))
            else:
                if not os.path.isdir(path): return []
                out_dir = os.path.join(path, "CONVERTITI_DISAGIO")
                for root_d, dirs, files in os.walk(path):
                    dirs[:] = [d for d in dirs
                                if os.path.join(root_d, d) != out_dir]
                    for f in sorted(files):
                        if Path(f).suffix.lower() not in valid_exts: continue
                        src  = os.path.join(root_d, f)
                        stem = f"{prefix}_{Path(f).stem}" if prefix else Path(f).stem
                        rel  = os.path.relpath(root_d, path)
                        dst  = os.path.join(out_dir, rel, f"{stem}.{out_ext}")
                        info = probe_video(src) if is_auto else dummy_info
                        jobs.append((src, self._unique_path(dst), info, False))
        return jobs
    # ----------------------------------------------------------
    def _start(self):
        path = self.lbl_file.text()
        if not path or path == "Nessun file selezionato":
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un file o una cartella.")
            return
        params = self._collect_params()
        # se AUTO e cartella: avvisa che il probe richiede tempo
        if params.get("vqual") == "AUTO" and self.rb_folder.isChecked():
            if QMessageBox.question(
                self, "Modalità AUTO — cartella",
                "In modalità AUTO ogni file viene analizzato con ffprobe prima della conversione.\n"
                "Su cartelle grandi questo può richiedere qualche minuto in più.\n\nProcedere?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            ) != QMessageBox.StandardButton.Ok:
                return
        jobs = self._collect_jobs(params)
        if not jobs:
            QMessageBox.warning(self, "Nessun file", "Nessun file da convertire trovato.")
            return
        if self.btn_manual.isChecked():
            params["manual_cmd"] = self.txt_cmd.text().strip()
        else:
            params.pop("manual_cmd", None)
        mode = params["mode"]
        raw_jobs   = sum(1 for j in jobs if j[3])
        conv_jobs  = len(jobs) - raw_jobs
        lines = []
        if mode == "image":
            if conv_jobs:
                lines.append(f"Immagini da convertire: {conv_jobs}")
            if raw_jobs:
                lines.append(f"File RAW da copiare in FOTO_RAW: {raw_jobs}")
            lines += [
                f"Formato output: .{params['img_fmt'].upper()}",
                f"Qualità: {image_quality_label(params['img_quality'])}",
            ]
        else:
            lines.append(f"File da convertire: {len(jobs)}")
            if mode == "video":
                lines += [
                    f"Encoder GPU: {params['gpu']}",
                    f"HW decoding: {'Sì' if params['hwaccel'] else 'No'}",
                    f"Codec video: {params['vcodec']} — {params['vqual']}",
                    f"Container: .{params['video_ext']}",
                    f"Risoluzione: {params['resolution']}",
                ]
            lines += [
                f"Codec audio: {params['acodec']} — {params['aqual']}",
                f"Sample rate: {params['sample_rate']}",
            ]
        pfx = self.txt_name.text().strip()
        if pfx and not self.rb_single.isChecked():
            lines.append(f"Prefisso: {pfx}_")
        if QMessageBox.question(
            self, "Conferma", "\n".join(lines),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        ) != QMessageBox.StandardButton.Ok:
            return
        self.jobs = jobs; self.params = params
        self.terminal.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.btn_stop.setVisible(True)
        self.btn_go.setEnabled(False)
        self.thread = ConvertThread(jobs, params)
        self.thread.log_line.connect(self._append_log)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.file_done.connect(self._on_file_done)
        self.thread.all_done.connect(self._on_all_done)
        self.thread.start()
    def _stop(self):
        if self.thread:
            self.thread.stop()
            self._append_log("\n⚠  Conversione interrotta dall'utente.")
    def _append_log(self, text):
        self.terminal.appendPlainText(text)
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)
    def _on_file_done(self, fname, success):
        self._append_log(f"{'✓' if success else '✗'} {fname}")
    def _on_all_done(self, ok, err):
        self.btn_go.setEnabled(True)
        self.btn_stop.setVisible(False)
        self.progress_bar.setValue(100)
        self._append_log(f"\n{'═'*50}")
        self._append_log(f"  COMPLETATO — OK: {ok}   ERRORI: {err}")
        self._append_log(f"{'═'*50}")
        QMessageBox.information(
            self, "Conversione completata",
            f"{'✅' if err == 0 else '⚠️'}  File convertiti: {ok}"
            + (f"\n   Errori: {err}" if err else "")
        )
# ============================================================
#  MAIN
# ============================================================
def main():
    if not os.path.isfile(FFMPEG_BIN) and not shutil.which(FFMPEG_BIN):
        QApplication(sys.argv)   # serve per mostrare il dialogo
        QMessageBox.critical(
            None, "FFmpeg non trovato",
            f"Impossibile trovare ffmpeg.\n\n"
            f"Cercato in:\n"
            f"  • Bundle exe (PyInstaller)\n"
            f"  • Cartella dell'eseguibile\n"
            f"  • PATH di sistema\n\n"
            f"Su Linux installa con:  sudo dnf install ffmpeg\n"
            f"Su Windows scarica da:  https://ffmpeg.org/download.html\n"
            f"e metti ffmpeg.exe nella stessa cartella di questo programma."
        )
        sys.exit(1)
    app = QApplication(sys.argv)
    cfg = load_config()
    app.setStyleSheet(get_stylesheet(cfg.get("theme", "Dark Classic")))
    app.setApplicationName("DISAGIO PRODUCTION CONVERTER")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
