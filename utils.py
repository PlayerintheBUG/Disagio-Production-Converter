#!/usr/bin/env python3
"""
Disagio — utils.py
Funzioni helper: video probing, parametri AUTO, mapping risoluzioni/sample rates.
"""

import os
import json
import subprocess
from pathlib import Path

from config import (
    FFMPEG_BIN, FFPROBE_BIN,
    VIDEO_PRESETS, CODEC_EFFICIENCY, PRORES_PROFILE_EFFICIENCY,
    AUTO_BASE_CQ, AUTO_DELTA_RES,
    auto_delta_fps, auto_delta_depth, auto_delta_bpp,
    _IMG_QUAL_LABELS,
    CONFIG_FILE,
)

def image_quality_label(val: int) -> str:
    """Return a localised quality description for the given value (1-100)."""
    from translations import _LANG
    for threshold in (90, 75, 50, 25):
        if val >= threshold:
            d = _IMG_QUAL_LABELS[threshold]
            txt = d.get(_LANG, d["it"])
            return f"{val}%  —  {txt}"
    d = _IMG_QUAL_LABELS[0]
    txt = d.get(_LANG, d["it"])
    return f"{val}%  —  {txt}"

# ── Image ffmpeg args ──────────────────────────────────────
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

# ── Config load/save ───────────────────────────────────────
def load_config():
    from styles import THEMES
    from translations import set_language
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            if "custom_themes" in cfg:
                for k, v in cfg["custom_themes"].items():
                    THEMES[k] = v
            # restore saved language
            if "language" in cfg:
                set_language(cfg["language"])
            return cfg
    except Exception:
        return {"theme": "Dark Classic", "verbose_log": False, "language": "it"}
def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass

# ── Video probing + AUTO ─────────────────────────────────────
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
def _build_video_params(codec_dst: str, gpu: str, cq: int, depth: int,
                        bitrate_target_kbps: int = 0) -> str:
    """
    Costruisce la stringa parametri ffmpeg dato codec/gpu/cq (o bitrate target).
    Se bitrate_target_kbps > 0 usa modalità VBR/CBR two-pass-compatible invece di CQ.
    """
    if bitrate_target_kbps > 0:
        bv = f"{bitrate_target_kbps}k"
        if codec_dst == "AV1":
            pix = "p010le" if depth >= 10 else "yuv420p10le"
            if gpu == "NVIDIA":
                return f"-c:v av1_nvenc -rc vbr -b:v {bv} -maxrate {int(bitrate_target_kbps*1.5)}k -pix_fmt {pix}"
            if gpu == "AMD":
                return f"-c:v av1_amf -rc cbr -b:v {bv} -pix_fmt yuv420p"
            if gpu == "Intel":
                return f"-c:v av1_qsv -b:v {bv} -pix_fmt yuv420p"
            return f"-c:v libsvtav1 -b:v {bv} -pix_fmt {pix}"
        if codec_dst == "H.264":
            pix = "yuv420p"
            if gpu == "NVIDIA":
                return f"-c:v h264_nvenc -rc vbr -b:v {bv} -maxrate {int(bitrate_target_kbps*1.5)}k -pix_fmt {pix}"
            if gpu == "AMD":
                return f"-c:v h264_amf -rc cbr -b:v {bv} -pix_fmt {pix}"
            if gpu == "Intel":
                return f"-c:v h264_qsv -b:v {bv} -pix_fmt {pix}"
            return f"-c:v libx264 -b:v {bv} -pix_fmt {pix}"
        if codec_dst == "H.265":
            pix = "p010le" if depth >= 10 else "yuv420p"
            if gpu == "NVIDIA":
                return f"-c:v hevc_nvenc -rc vbr -b:v {bv} -maxrate {int(bitrate_target_kbps*1.5)}k -pix_fmt {pix}"
            if gpu == "AMD":
                return f"-c:v hevc_amf -rc cbr -b:v {bv} -pix_fmt {pix}"
            if gpu == "Intel":
                return f"-c:v hevc_qsv -b:v {bv} -pix_fmt {pix}"
            return f"-c:v libx265 -b:v {bv} -pix_fmt {pix}"
        return ""
    # modalità CQ
    if codec_dst == "AV1":
        pix = "p010le" if depth >= 10 else "yuv420p10le"
        if gpu == "NVIDIA":
            p7 = "p7" if cq <= 18 else ("p6" if cq <= 28 else "p4")
            return f"-c:v av1_nvenc -preset {p7} -cq {cq} -pix_fmt {pix}"
        if gpu == "AMD":
            q = "quality" if cq <= 18 else ("balanced" if cq <= 28 else "speed")
            return f"-c:v av1_amf -quality {q} -rc cqp -qp_i {cq} -qp_p {cq} -pix_fmt yuv420p"
        if gpu == "Intel":
            p = "veryslow" if cq <= 18 else ("medium" if cq <= 28 else "faster")
            return f"-c:v av1_qsv -preset {p} -global_quality {cq} -pix_fmt yuv420p"
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


def probe_video_bpp(path: str, sample_seconds: int = 0) -> float:
    """
    Calcola il BPP (bits per pixel per frame) effettivo dal video.
    Se sample_seconds > 0 analizza solo i primi N secondi (più veloce).
    Usa ffprobe packet-level per leggere i byte reali frame per frame.
    Ritorna il bpp medio, o 0.0 se non riesce.
    """
    try:
        extra = ["-read_intervals", f"%+{sample_seconds}"] if sample_seconds > 0 else []
        r = subprocess.run(
            [FFPROBE_BIN, "-v", "quiet", "-select_streams", "v:0",
             "-show_packets", "-show_entries", "packet=size,duration_time",
             "-of", "default=noprint_wrappers=1"] + extra + [path],
            capture_output=True, text=True, timeout=60
        )
        sizes = []
        for line in r.stdout.splitlines():
            if line.startswith("size="):
                v = line.split("=", 1)[1].strip()
                if v.isdigit():
                    sizes.append(int(v))
        if not sizes:
            return 0.0
        avg_bytes = sum(sizes) / len(sizes)
        return 0.0  # ritorna solo i bytes, risoluzione serve separata
    except Exception:
        return 0.0


def compute_bpp_from_probe(src_info: dict, sample_path: str = "",
                            sample_seconds: int = 0) -> float:
    """
    Calcola BPP reale da ffprobe packet-level.
    Fallback al BPP stimato dal bitrate se ffprobe fallisce.
    """
    width   = src_info["width"]
    height  = src_info["height"]
    fps     = max(src_info["fps"], 1.0)
    bitrate = src_info["bitrate"]
    pixels  = width * height

    if sample_path:
        try:
            extra = ["-read_intervals", f"%+{sample_seconds}"] if sample_seconds > 0 else []
            r = subprocess.run(
                [FFPROBE_BIN, "-v", "quiet", "-select_streams", "v:0",
                 "-show_packets", "-show_entries", "packet=size",
                 "-of", "default=noprint_wrappers=1"] + extra + [sample_path],
                capture_output=True, text=True, timeout=60
            )
            sizes = []
            for line in r.stdout.splitlines():
                if line.startswith("size="):
                    v = line.split("=", 1)[1].strip()
                    if v.isdigit() and int(v) > 0:
                        sizes.append(int(v))
            if sizes:
                # bytes medi per frame → bits per pixel per frame
                avg_bits = (sum(sizes) / len(sizes)) * 8
                bpp = avg_bits / max(pixels, 1)
                return bpp
        except Exception:
            pass

    # fallback: stima da bitrate dichiarato
    codec_src  = src_info["codec"]
    efficiency = CODEC_EFFICIENCY.get(codec_src, 1.0)
    if codec_src == "prores":
        p = str(src_info.get("profile", "0")).lower()
        for k, v in PRORES_PROFILE_EFFICIENCY.items():
            if k in p or p == k:
                efficiency = v
                break
    bitrate_equiv = bitrate * efficiency
    bpp = (bitrate_equiv / fps) / max(pixels, 1)
    return bpp


def auto_compute_cq(src_info: dict, codec_dst: str, gpu: str,
                    dst_width: int, dst_height: int,
                    auto_params: dict = None) -> str:
    """
    Calcola i parametri video ottimali per il codec di destinazione.
    auto_params: dizionario con le opzioni del dialogo AUTO:
        - use_bpp_probe: bool  (usa packet-level BPP invece di stima bitrate)
        - cap_mode: "none" | "size_mb" | "size_pct"
        - cap_value: float  (MB per file singolo, % per cartella)
        - duration_s: float  (durata del video in secondi, serve per cap)
        - src_file_bytes: int  (peso file sorgente, per cap percentuale)
    Ritorna la stringa di parametri ffmpeg.
    """
    if auto_params is None:
        auto_params = {}

    fps     = max(src_info["fps"], 1.0)
    depth   = src_info["depth"]
    dst_pixels = max(dst_width * dst_height, 1)

    # per DNxHR/ProRes non si usa CQ — profilo fisso
    if codec_dst in ("DNxHR", "ProRes"):
        return auto_mezzanine_profile(codec_dst, dst_width, dst_height, depth)

    # ── cap dimensione: calcola bitrate target ─────────────────────────────
    cap_mode  = auto_params.get("cap_mode", "none")
    cap_value = float(auto_params.get("cap_value", 0))
    duration  = float(auto_params.get("duration_s", 0))
    src_bytes = int(auto_params.get("src_file_bytes", 0))

    bitrate_target_kbps = 0
    if cap_mode != "none" and duration > 0 and cap_value > 0:
        if cap_mode == "size_mb":
            # cap assoluto in MB → bitrate totale (video+audio)
            # togliamo ~192kbps per audio, resto al video
            target_bits = cap_value * 8 * 1024 * 1024
            audio_bits  = 192_000 * duration
            video_bits  = max(target_bits - audio_bits, 0)
            bitrate_target_kbps = int(video_bits / duration / 1000)
        elif cap_mode == "size_pct" and src_bytes > 0:
            # riduzione percentuale sul peso del file sorgente
            target_bytes = src_bytes * (1.0 - cap_value / 100.0)
            target_bits  = target_bytes * 8
            audio_bits   = 192_000 * duration
            video_bits   = max(target_bits - audio_bits, 0)
            bitrate_target_kbps = int(video_bits / duration / 1000)

    if bitrate_target_kbps > 0:
        # minimo ragionevole per non ottenere un file inutilizzabile
        min_kbps = {"H.264": 200, "H.265": 150, "AV1": 100}.get(codec_dst, 150)
        bitrate_target_kbps = max(bitrate_target_kbps, min_kbps)
        return _build_video_params(codec_dst, gpu, 0, depth, bitrate_target_kbps)

    # ── stima CQ da BPP reale ──────────────────────────────────────────────
    use_probe = auto_params.get("use_bpp_probe", False)
    src_file  = auto_params.get("src_file", "")
    bpp = compute_bpp_from_probe(src_info,
                                  sample_path=src_file if use_probe else "",
                                  sample_seconds=0)

    # normalizza il BPP alla risoluzione di DESTINAZIONE
    src_pixels = max(src_info["width"] * src_info["height"], 1)
    bpp_dst = bpp * (src_pixels / dst_pixels)

    # determina range risoluzione destinazione per delta
    dst_height = dst_height or src_info["height"]
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
          + auto_delta_bpp(bpp_dst))
    cq = max(8, min(51, cq))
    return _build_video_params(codec_dst, gpu, cq, depth)

# ============================================================
#  TRADUZIONI / TRANSLATIONS / ÜBERSETZUNGEN / TRADUCCIONES
# ============================================================
LANGUAGES = {
    "Italiano 🇮🇹":  "it",
    "English 🇬🇧":   "en",
    "Deutsch 🇩🇪":   "de",
    "Español 🇪🇸":   "es",
    "Doge 🐕":        "doge",
}

# ── Resolution / SampleRate helpers ─────────────────────────
_RES_DISPLAY = {
    # internal_key: { lang: display_text }
    "Mantieni originale": {
        "it": "Mantieni originale",
        "en": "Keep original",
        "de": "Original beibehalten",
        "es": "Mantener original",
        "doge": "keep as is wow",
    },
    "480p  (854×480)":    {"it": "480p  (854×480)",    "en": "480p  (854×480)",    "de": "480p  (854×480)",    "es": "480p  (854×480)",    "doge": "480p  (854×480)"},
    "720p  (1280×720)":   {"it": "720p  (1280×720)",   "en": "720p  (1280×720)",   "de": "720p  (1280×720)",   "es": "720p  (1280×720)",   "doge": "720p  (1280×720)"},
    "1080p (1920×1080)":  {"it": "1080p (1920×1080)",  "en": "1080p (1920×1080)",  "de": "1080p (1920×1080)",  "es": "1080p (1920×1080)",  "doge": "1080p (1920×1080)"},
    "1440p QHD (2560×1440)": {"it": "1440p QHD (2560×1440)", "en": "1440p QHD (2560×1440)", "de": "1440p QHD (2560×1440)", "es": "1440p QHD (2560×1440)", "doge": "1440p QHD (2560×1440)"},
    "4K UHD (3840×2160)": {"it": "4K UHD (3840×2160)", "en": "4K UHD (3840×2160)", "de": "4K UHD (3840×2160)", "es": "4K UHD (3840×2160)", "doge": "4K UHD (3840×2160)"},
    "8K UHD (7680×4320)": {"it": "8K UHD (7680×4320)", "en": "8K UHD (7680×4320)", "de": "8K UHD (7680×4320)", "es": "8K UHD (7680×4320)", "doge": "8K UHD (7680×4320)"},
}

_SR_DISPLAY = {
    "Mantieni originale": {
        "it": "Mantieni originale",
        "en": "Keep original",
        "de": "Original beibehalten",
        "es": "Mantener original",
        "doge": "keep as is wow",
    },
    "44100 Hz": {"it": "44100 Hz", "en": "44100 Hz", "de": "44100 Hz", "es": "44100 Hz", "doge": "44100 Hz"},
    "48000 Hz": {"it": "48000 Hz", "en": "48000 Hz", "de": "48000 Hz", "es": "48000 Hz", "doge": "48000 Hz"},
    "96000 Hz": {"it": "96000 Hz", "en": "96000 Hz", "de": "96000 Hz", "es": "96000 Hz", "doge": "96000 Hz"},
    "192000 Hz": {"it": "192000 Hz", "en": "192000 Hz", "de": "192000 Hz", "es": "192000 Hz", "doge": "192000 Hz"},
}

def res_display_items():
    """Return localised resolution labels in insertion order."""
    from translations import _LANG
    return [d.get(_LANG, d["it"]) for d in _RES_DISPLAY.values()]

def res_internal_key(display_text: str) -> str:
    """Map a localised display label back to the internal RESOLUTIONS key."""
    for internal, d in _RES_DISPLAY.items():
        if display_text in d.values():
            return internal
    return display_text  # fallback: already internal

def sr_display_items():
    """Return localised sample-rate labels."""
    from translations import _LANG
    return [d.get(_LANG, d["it"]) for d in _SR_DISPLAY.values()]

def sr_internal_key(display_text: str) -> str:
    """Map a localised sample-rate label back to the internal key."""
    for internal, d in _SR_DISPLAY.items():
        if display_text in d.values():
            return internal
    return display_text

def sr_display_for(internal: str) -> str:
    """Return the localised label for a given internal sample-rate key."""
    d = _SR_DISPLAY.get(internal)
    if d:
        from translations import _LANG
        return d.get(_LANG, d["it"])
    return internal

def res_display_for(internal: str) -> str:
    """Return the localised label for a given internal resolution key."""
    d = _RES_DISPLAY.get(internal)
    if d:
        from translations import _LANG
        return d.get(_LANG, d["it"])
    return internal

