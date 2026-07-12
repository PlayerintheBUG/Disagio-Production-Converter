#!/usr/bin/env python3
"""
Disagio — upscale.py
UpscaleThread: mini upscaling con nitidezza in singolo passaggio FFmpeg.

NB IMPORTANTE: questo NON è un upscaler a rete neurale (niente modelli
esterni, niente decomposizione in frame). È una pipeline FFmpeg nativa
in tre fasi, pensata per un ingrandimento pulito e nitido:

    1) denoise adattivo (hqdn3d)  → ripulisce gli artefatti di
       compressione PRIMA di ingrandire, così l'upscale non li amplifica
    2) scaling Lanczos ad alta qualità → ingrandimento vero e proprio
    3) unsharp mirato sui bordi → ridà nitidezza percepita dopo
       l'ingrandimento

Tutto in un solo passaggio ffmpeg, niente cartelle di frame PNG da
gestire a mano. In futuro questo modulo potrà essere esteso per
appoggiarsi a un vero modello (filtro dnn_processing/sr di ffmpeg, o
un backend esterno) mantenendo la stessa interfaccia (UpscaleThread).

Encoder e qualità dipendono dal container di destinazione:
  - MP4 / MKV → H.264, H.265, AV1 (CPU o GPU), su 5 step di qualità
    ("max" = massima qualità possibile per quell'encoder, "min" = la
    più bassa, gli altri 3 sono intermedi).
  - MOV → solo ProRes / DNxHR (mezzanine), anch'essi su 5 step di
    qualità (mappati sui rispettivi profili).
L'audio non viene mai ri-codificato: resta sempre "-c:a copy",
qualunque sia il container scelto.
"""

import os
import subprocess

from PyQt6.QtCore import QThread, pyqtSignal

from config import FFMPEG_BIN, FFPROBE_BIN

# Fattori di scala rapidi, alternativi a una risoluzione target fissa
SCALE_FACTORS = {"2x": 2.0, "3x": 3.0, "4x": 4.0}

UPSCALE_CONTAINERS = {
    "MKV (.mkv)": "mkv",
    "MP4 (.mp4)": "mp4",
    "MOV (.mov)": "mov",
}

# Codec disponibili in base al container di destinazione (stessa mappatura
# usata dalla conversione video normale, vedi config.CONTAINER_CODECS):
# MP4/MKV → AV1 / H.264 / H.265 (selezionabili su CPU o GPU).
# MOV → solo ProRes / DNxHR (mezzanine, sempre CPU).
UPSCALE_CODECS_BY_CONTAINER = {
    "MKV (.mkv)": ["AV1", "H.264", "H.265"],
    "MP4 (.mp4)": ["AV1", "H.264", "H.265"],
    "MOV (.mov)": ["ProRes", "DNxHR"],
}

# Codec "mezzanine": sempre CPU, nessuna scelta di backend GPU.
UPSCALE_MEZZANINE_ENCODERS = {
    "ProRes": "prores_ks",
    "DNxHR":  "dnxhd",
}

# Backend di codifica → codec → codice encoder ffmpeg reale.
UPSCALE_ENCODER_MAP = {
    "CPU": {
        "AV1":   "libsvtav1",
        "H.264": "libx264",
        "H.265": "libx265",
    },
    "NVIDIA": {
        "AV1":   "av1_nvenc",
        "H.264": "h264_nvenc",
        "H.265": "hevc_nvenc",
    },
    "AMD": {
        "AV1":   "av1_amf",
        "H.264": "h264_amf",
        "H.265": "hevc_amf",
    },
    "Intel": {
        "AV1":   "av1_qsv",
        "H.264": "h264_qsv",
        "H.265": "hevc_qsv",
    },
}


def resolve_upscale_encoder(codec: str, gpu: str) -> str:
    """Determina il codice encoder ffmpeg finale in base al codec scelto
    (AV1/H.264/H.265/ProRes/DNxHR) e al backend di codifica (CPU/NVIDIA/
    AMD/Intel). I codec mezzanine (ProRes/DNxHR) ignorano il backend,
    essendo sempre CPU."""
    if codec in UPSCALE_MEZZANINE_ENCODERS:
        return UPSCALE_MEZZANINE_ENCODERS[codec]
    backend = UPSCALE_ENCODER_MAP.get(gpu, UPSCALE_ENCODER_MAP["CPU"])
    return backend.get(codec, "libx264")


# Chiave di traduzione (translations.py) per l'etichetta di ogni encoder
UPSCALE_ENCODER_LABEL_KEYS = {
    "libx264":     "enc_libx264",
    "libx265":     "enc_libx265",
    "libsvtav1":   "enc_libsvtav1",
    "h264_nvenc":  "enc_h264_nvenc",
    "hevc_nvenc":  "enc_hevc_nvenc",
    "av1_nvenc":   "enc_av1_nvenc",
    "h264_amf":    "enc_h264_amf",
    "hevc_amf":    "enc_hevc_amf",
    "av1_amf":     "enc_av1_amf",
    "h264_qsv":    "enc_h264_qsv",
    "hevc_qsv":    "enc_hevc_qsv",
    "av1_qsv":     "enc_av1_qsv",
    "prores_ks":   "enc_prores_ks",
    "dnxhd":       "enc_dnxhd",
}

# 5 step di qualità: "max" = massima qualità possibile per quell'encoder,
# "min" = qualità più bassa, gli altri sono intermedi.
UPSCALE_QUALITY_LEVELS = ["max", "high", "mid", "low", "min"]

# CRF (libx264/libx265/libsvtav1) o CQ/QP/global_quality (nvenc/amf/qsv)
# per ciascun encoder e livello di qualità. Valori più bassi = qualità più alta.
UPSCALE_QUALITY_PARAMS = {
    "libx264":    {"max": 14, "high": 18, "mid": 23, "low": 28, "min": 33},
    "libx265":    {"max": 14, "high": 18, "mid": 24, "low": 29, "min": 34},
    "libsvtav1":  {"max": 10, "high": 16, "mid": 24, "low": 32, "min": 40},
    "h264_nvenc": {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "hevc_nvenc": {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "av1_nvenc":  {"max": 10, "high": 18, "mid": 26, "low": 34, "min": 42},
    "h264_amf":   {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "hevc_amf":   {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "av1_amf":    {"max": 10, "high": 18, "mid": 26, "low": 34, "min": 42},
    "h264_qsv":   {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "hevc_qsv":   {"max": 14, "high": 18, "mid": 24, "low": 30, "min": 36},
    "av1_qsv":    {"max": 10, "high": 18, "mid": 26, "low": 34, "min": 42},
}

# ProRes (prores_ks -profile:v N): profilo + pix_fmt per livello qualità
UPSCALE_PRORES_PROFILES = {
    "max":  ("4", "yuva444p10le"),  # 4444
    "high": ("3", "yuv422p10le"),   # HQ
    "mid":  ("2", "yuv422p10le"),   # 422 standard
    "low":  ("1", "yuv422p10le"),   # LT
    "min":  ("0", "yuv422p10le"),   # Proxy
}

# DNxHR (dnxhd -profile:v dnxhr_*): profilo + pix_fmt per livello qualità
UPSCALE_DNXHR_PROFILES = {
    "max":  ("dnxhr_444", "yuv444p10le"),
    "high": ("dnxhr_hqx", "yuv422p10le"),
    "mid":  ("dnxhr_hq",  "yuv422p"),
    "low":  ("dnxhr_sq",  "yuv422p"),
    "min":  ("dnxhr_lb",  "yuv422p"),
}


def build_upscale_filter(src_w, src_h, target, denoise, sharpen):
    """
    Costruisce la catena -vf per il mini upscaling con nitidezza.

    target:  tupla (w, h) per una risoluzione fissa, oppure float
             (es. 2.0) come fattore di scala rispetto alla sorgente.
    denoise: intensità 0-3 del pre-filtro hqdn3d (0 = disattivato).
    sharpen: intensità 0.0-2.0 dell'unsharp finale (0 = disattivato).
    """
    if isinstance(target, tuple):
        dst_w, dst_h = target
    else:
        factor = float(target)
        dst_w = int(round(src_w * factor / 2) * 2)
        dst_h = int(round(src_h * factor / 2) * 2)

    chain = []
    if denoise and denoise > 0:
        luma_s = round(2 * denoise, 2)
        chroma_s = round(1.5 * denoise, 2)
        luma_t = round(luma_s * 1.5, 2)
        chroma_t = round(chroma_s * 1.5, 2)
        chain.append(f"hqdn3d={luma_s}:{chroma_s}:{luma_t}:{chroma_t}")
    chain.append(f"scale={dst_w}:{dst_h}:flags=lanczos")
    if sharpen and sharpen > 0:
        amount = round(0.5 + sharpen, 2)
        chain.append(f"unsharp=5:5:{amount}:5:5:0.0")
    return ",".join(chain)


class UpscaleThread(QThread):
    log_line  = pyqtSignal(str)
    progress  = pyqtSignal(int)
    file_done = pyqtSignal(str, bool)
    all_done  = pyqtSignal(int, int)

    def __init__(self, jobs, params):
        """
        jobs:   lista di tuple (src, dst)
        params: dict con:
            target      -> (w,h) oppure fattore float (default 2.0)
            denoise     -> 0-3 (default 1)
            sharpen     -> 0.0-2.0 (default 0.6)
            codec       -> "AV1"/"H.264"/"H.265"/"ProRes"/"DNxHR"
            gpu         -> backend di codifica: "CPU"/"NVIDIA"/"AMD"/"Intel"
                           (ignorato per i codec mezzanine ProRes/DNxHR)
            quality     -> livello 5 step: "max"/"high"/"mid"/"low"/"min"
            hwaccel     -> bool (hwaccel in decodifica)
            verbose_log -> bool
        """
        super().__init__()
        self.jobs = jobs
        self.params = params
        self._stop = False
        self.verbose_log = params.get("verbose_log", False)

    def stop(self):
        self._stop = True

    def get_duration(self, path: str) -> float:
        try:
            r = subprocess.run(
                [FFPROBE_BIN, "-v", "quiet",
                 "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=20
            )
            v = r.stdout.strip()
            return float(v) if v else 0.0
        except Exception:
            return 0.0

    def get_video_dims(self, path: str):
        try:
            r = subprocess.run(
                [FFPROBE_BIN, "-v", "quiet", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height",
                 "-of", "csv=s=x:p=0", path],
                capture_output=True, text=True, timeout=20
            )
            w_str, h_str = r.stdout.strip().split("x")
            return int(w_str), int(h_str)
        except Exception:
            return 1920, 1080

    def build_cmd(self, src, dst):
        w, h = self.get_video_dims(src)
        target  = self.params.get("target", 2.0)
        denoise = self.params.get("denoise", 1)
        sharpen = self.params.get("sharpen", 0.6)
        vf = build_upscale_filter(w, h, target, denoise, sharpen)

        encoder_code = resolve_upscale_encoder(
            self.params.get("codec", "H.264"),
            self.params.get("gpu", "CPU"),
        )
        quality      = self.params.get("quality", "mid")

        if encoder_code == "prores_ks":
            profile, pix_fmt = UPSCALE_PRORES_PROFILES.get(
                quality, UPSCALE_PRORES_PROFILES["mid"])
            v_params = ["-c:v", "prores_ks", "-profile:v", profile, "-pix_fmt", pix_fmt]
        elif encoder_code == "dnxhd":
            profile, pix_fmt = UPSCALE_DNXHR_PROFILES.get(
                quality, UPSCALE_DNXHR_PROFILES["mid"])
            v_params = ["-c:v", "dnxhd", "-profile:v", profile, "-pix_fmt", pix_fmt]
        else:
            q_map = UPSCALE_QUALITY_PARAMS.get(encoder_code, UPSCALE_QUALITY_PARAMS["libx264"])
            q_val = q_map.get(quality, q_map["mid"])

            if "amf" in encoder_code:
                v_params = ["-c:v", encoder_code, "-rc", "cqp",
                            "-qp_i", str(q_val), "-qp_p", str(q_val), "-pix_fmt", "yuv420p"]
            elif "qsv" in encoder_code:
                v_params = ["-c:v", encoder_code, "-preset", "medium",
                            "-global_quality", str(q_val), "-pix_fmt", "yuv420p"]
            elif "nvenc" in encoder_code:
                v_params = ["-c:v", encoder_code, "-preset", "p5",
                            "-cq", str(q_val), "-pix_fmt", "yuv420p"]
            elif encoder_code == "libsvtav1":
                v_params = ["-c:v", encoder_code, "-preset", "6",
                            "-crf", str(q_val), "-pix_fmt", "yuv420p10le"]
            else:
                v_params = ["-c:v", encoder_code, "-crf", str(q_val), "-preset", "slow", "-pix_fmt", "yuv420p"]

        hwaccel = self.params.get("hwaccel", False)
        hw_flag = ["-hwaccel", "auto"] if hwaccel else []

        cmd = ([FFMPEG_BIN] + hw_flag + ["-i", src, "-vf", vf] + v_params
               + ["-c:a", "copy", dst, "-y", "-progress", "pipe:1"])
        return cmd

    def run(self):
        ok = err = 0
        total = len(self.jobs)
        for idx, job in enumerate(self.jobs):
            if self._stop:
                break
            src, dst = job
            fname = os.path.basename(src)
            self.log_line.emit(f"\n{'─'*50}")
            self.log_line.emit(f"[{idx+1}/{total}] 🔬 Upscaling: {fname}")
            self.log_line.emit(f"  → {dst}")
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)

            duration = self.get_duration(src)
            cmd = self.build_cmd(src, dst)
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
                            ms = int(line.split("=")[1])
                            t = ms / 1_000_000
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
                                 "out_time","total_size","dup_frames","drop_frames","progress="]):
                                self.log_line.emit("  " + line)
                proc.wait()
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
