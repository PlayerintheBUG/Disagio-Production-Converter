#!/usr/bin/env python3
"""
Disagio — video.py
ConvertThread: logica di conversione video/audio/immagini.
"""

import os
import json
import subprocess
import shutil
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from config import FFMPEG_BIN, FFPROBE_BIN, VIDEO_PRESETS, RESOLUTIONS
from translations import T
from utils import (
    probe_video, build_image_ffmpeg_args,
    res_internal_key, sr_internal_key,
    load_config, save_config,
    auto_compute_cq,
)

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
    def get_duration(self, path: str) -> float:
        """Ritorna la durata in secondi del file media tramite ffprobe."""
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

    def get_video_opts(self, src_info, dst_width, dst_height,
                       src_file: str = "", src_file_bytes: int = 0,
                       duration_s: float = 0.0):
        """Ritorna la stringa di parametri video (AUTO o preset fisso)."""
        gpu    = self.params.get("gpu", "NVIDIA")
        vcodec = self.params.get("vcodec", "AV1")
        vqual  = self.params.get("vqual", "Medio")
        if vqual == "AUTO":
            auto_s = dict(self.params.get("auto_settings", {}))
            auto_s["src_file"]       = src_file
            auto_s["src_file_bytes"] = src_file_bytes
            auto_s["duration_s"]     = duration_s
            return auto_compute_cq(src_info, vcodec, gpu, dst_width, dst_height, auto_s)
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS.get(vcodec, {}).get(vqual, "")
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
    def build_cmd(self, src, dst, src_info,
                  src_file_bytes: int = 0, duration_s: float = 0.0):
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
        sample_internal = sr_internal_key(sample)
        sr_flag = [] if sample_internal == "Mantieni originale" else ["-ar", sample_internal.replace(" Hz", "")]
        hw_flag = ["-hwaccel", "auto"] if hwaccel else []
        audio_opts = self.params["audio_preset"].split()
        cmd = [FFMPEG_BIN] + hw_flag + ["-i", src]
        if mode == "audio":
            cmd += ["-vn"] + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]
        else:
            dst_w, dst_h = self.get_dst_dims(src_info, res_key)
            video_opts   = self.get_video_opts(
                src_info, dst_w, dst_h,
                src_file=src,
                src_file_bytes=src_file_bytes,
                duration_s=duration_s,
            ).split()
            scale_filter = self.get_scale_filter(src_info, res_key)
            if scale_filter:
                cmd += ["-vf", scale_filter]
            cmd += video_opts + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]
        return cmd

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
            duration = self.get_duration(src) if self.params["mode"] != "image" else 0.0
            # calcola peso sorgente per cap %
            try:
                src_file_bytes = os.path.getsize(src)
            except Exception:
                src_file_bytes = 0
            # se AUTO, mostra i parametri calcolati
            if self.params.get("vqual") == "AUTO" and self.params["mode"] == "video":
                res_key = self.params.get("resolution", "Mantieni originale")
                dst_w, dst_h = self.get_dst_dims(src_info, res_key)
                computed = self.get_video_opts(src_info, dst_w, dst_h,
                                               src_file=src,
                                               src_file_bytes=src_file_bytes,
                                               duration_s=duration)
                self.log_line.emit(f"  [AUTO] {computed}")

            cmd = self.build_cmd(src, dst, src_info,
                                 src_file_bytes=src_file_bytes,
                                 duration_s=duration)
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
