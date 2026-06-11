#!/usr/bin/env python3
"""
Disagio — upscale.py

UpscaleThread: decomposizione video → frames PNG + audio WAV
               ricomposizione frames → video con audio reinserito.

Flusso AI Upscaling:
  1. DECOMPOSIZIONE  → video.mp4 → FRAMES_nomefile/frame_%06d.png + audio.wav
  2. [utente usa qualsiasi upscaler sulle PNG nella cartella]
  3. RICOMPOSIZIONE  → seleziona la cartella frames → riassembla video con audio
"""

import os
import re
import subprocess
import json
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from config import FFMPEG_BIN, FFPROBE_BIN
from translations import T


# ── helpers ──────────────────────────────────────────────────────────────────

def probe_fps(path: str) -> str:
    """Ritorna il framerate come stringa 'NUM/DEN' oppure '25/1'."""
    try:
        r = subprocess.run(
            [FFPROBE_BIN, "-v", "quiet",
             "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate",
             "-of", "json", path],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(r.stdout)
        streams = data.get("streams", [])
        if streams:
            return streams[0].get("r_frame_rate", "25/1")
    except Exception:
        pass
    return "25/1"


def probe_duration(path: str) -> float:
    """Ritorna la durata in secondi."""
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


def has_audio_stream(path: str) -> bool:
    """Ritorna True se il file ha almeno uno stream audio."""
    try:
        r = subprocess.run(
            [FFPROBE_BIN, "-v", "quiet",
             "-select_streams", "a:0",
             "-show_entries", "stream=codec_type",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=20
        )
        return bool(r.stdout.strip())
    except Exception:
        return False


def count_frames_in_dir(frames_dir: str) -> int:
    """Conta i file PNG nella cartella frames."""
    try:
        return sum(
            1 for f in os.listdir(frames_dir)
            if f.lower().endswith(".png")
        )
    except Exception:
        return 0


def find_audio_wav(frames_dir: str) -> str | None:
    """
    Cerca il file audio.wav salvato dalla decomposizione accanto alla cartella frames.
    Convenzione: <frames_dir>/../<nome_frames_dir>_audio.wav
    oppure       <frames_dir>/audio.wav  (fallback)
    """
    frames_path = Path(frames_dir)
    # Prima scelta: file esterno con stessa naming convention
    candidate = frames_path.parent / f"{frames_path.name}_audio.wav"
    if candidate.exists():
        return str(candidate)
    # Seconda: audio.wav dentro la cartella stessa (caso edge)
    fallback = frames_path / "audio.wav"
    if fallback.exists():
        return str(fallback)
    return None


def detect_frame_pattern(frames_dir: str) -> str | None:
    """
    Rileva il pattern ffmpeg dei frame (es. frame_%06d.png).
    Funziona anche se l'utente ha rinominato i file con un upscaler,
    purché il suffisso numerico sia mantenuto.
    """
    try:
        files = sorted(
            f for f in os.listdir(frames_dir)
            if f.lower().endswith(".png")
        )
        if not files:
            return None
        # Prova a capire il numero di cifre dal primo file
        m = re.search(r"(\d+)\.png$", files[0], re.IGNORECASE)
        if not m:
            return None
        digits = len(m.group(1))
        prefix = files[0][: files[0].rfind(m.group(1))]
        return os.path.join(frames_dir, f"{prefix}%0{digits}d.png")
    except Exception:
        return None


# ── thread decomposizione ─────────────────────────────────────────────────────

class DecomposeThread(QThread):
    """Estrae tutti i frame PNG e l'audio WAV da un video sorgente."""

    log_line  = pyqtSignal(str)
    progress  = pyqtSignal(int)
    all_done  = pyqtSignal(bool, str)   # (success, output_dir)

    def __init__(self, src: str, out_dir: str | None = None, parent=None):
        super().__init__(parent)
        self.src = src
        # Se non specificato, crea la cartella accanto al video
        if out_dir:
            self.out_dir = out_dir
        else:
            p = Path(src)
            self.out_dir = str(p.parent / f"FRAMES_{p.stem}")
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        src       = self.src
        out_dir   = self.out_dir
        audio_out = str(Path(out_dir).parent / f"{Path(out_dir).name}_audio.wav")

        self.log_line.emit(f"\n{'─'*50}")
        self.log_line.emit(f"[DECOMPOSIZIONE] {Path(src).name}")
        self.log_line.emit(f" → frames : {out_dir}")

        # Crea cartella output
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            self.log_line.emit(f" ERRORE creazione cartella: {e}")
            self.all_done.emit(False, "")
            return

        duration = probe_duration(src)

        # ── 1. Estrai frames ──────────────────────────────────────────────
        frame_pattern = os.path.join(out_dir, "frame_%06d.png")
        cmd_frames = [
            FFMPEG_BIN, "-i", src,
            "-vf", "scale=iw:ih",          # copia dimensione originale
            "-pix_fmt", "rgb24",
            "-vsync", "0",
            "-progress", "pipe:1",
            frame_pattern, "-y"
        ]

        self.log_line.emit(" $ " + " ".join(cmd_frames))
        self.progress.emit(2)

        try:
            proc = subprocess.Popen(
                cmd_frames,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in proc.stdout:
                if self._stop:
                    proc.terminate()
                    break
                line = line.rstrip()
                if line.startswith("out_time_ms="):
                    try:
                        ms  = int(line.split("=")[1])
                        t   = ms / 1_000_000
                        if duration > 0:
                            pct = min(int(t / duration * 100 * 0.85), 84)
                            self.progress.emit(pct)
                    except Exception:
                        pass
                elif line.strip() and not line.startswith("progress="):
                    if not any(line.startswith(p) for p in
                               ["frame=","fps=","stream_","bitrate=","speed=",
                                "out_time","total_size","dup_frames","drop_frames"]):
                        self.log_line.emit("  " + line)
            proc.wait()
            frames_ok = (proc.returncode == 0)
        except Exception as e:
            self.log_line.emit(f" ERRORE estrazione frames: {e}")
            self.all_done.emit(False, "")
            return

        if not frames_ok:
            self.log_line.emit(" ✗ Estrazione frames fallita.")
            self.all_done.emit(False, "")
            return

        n_frames = count_frames_in_dir(out_dir)
        self.log_line.emit(f" ✓ {n_frames} frame estratti")
        self.progress.emit(87)

        # ── 2. Estrai audio (se presente) ────────────────────────────────
        if has_audio_stream(src):
            self.log_line.emit(f" → audio  : {audio_out}")
            cmd_audio = [
                FFMPEG_BIN, "-i", src,
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "48000",
                audio_out, "-y"
            ]
            self.log_line.emit(" $ " + " ".join(cmd_audio))
            try:
                r = subprocess.run(
                    cmd_audio, capture_output=True, text=True, timeout=300
                )
                if r.returncode == 0:
                    self.log_line.emit(" ✓ Audio estratto (WAV 48kHz)")
                else:
                    self.log_line.emit(" ⚠ Audio non estratto (video muto?)")
            except Exception as e:
                self.log_line.emit(f" ⚠ Errore estrazione audio: {e}")
        else:
            self.log_line.emit(" ℹ Nessuno stream audio trovato — video muto")

        self.progress.emit(100)
        self.log_line.emit(f"\n✓ DECOMPOSIZIONE COMPLETATA")
        self.log_line.emit(f"  Frames PNG  → {out_dir}")
        self.log_line.emit(f"  Applica il tuo upscaler AI alla cartella frames,")
        self.log_line.emit(f"  poi usa RICOMPOSIZIONE per riassemblare il video.")
        self.all_done.emit(True, out_dir)


# ── thread ricomposizione ────────────────────────────────────────────────────

class RecomposeThread(QThread):
    """Riassembla i frame upscalati in un video, reinserendo l'audio originale."""

    log_line  = pyqtSignal(str)
    progress  = pyqtSignal(int)
    all_done  = pyqtSignal(bool, str)   # (success, output_file)

    def __init__(self, frames_dir: str, fps: str, output_file: str,
                 audio_path: str | None = None,
                 video_params: list[str] | None = None,
                 parent=None):
        super().__init__(parent)
        self.frames_dir   = frames_dir
        self.fps          = fps          # es. "25/1" o "24000/1001"
        self.output_file  = output_file
        self.audio_path   = audio_path  # WAV estratto, può essere None
        self.video_params = video_params or [
            "-c:v", "libx264", "-crf", "18", "-preset", "slow",
            "-pix_fmt", "yuv420p"
        ]
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        frames_dir  = self.frames_dir
        output_file = self.output_file
        fps         = self.fps

        self.log_line.emit(f"\n{'─'*50}")
        self.log_line.emit(f"[RICOMPOSIZIONE] {Path(frames_dir).name}")
        self.log_line.emit(f" → output : {output_file}")

        # Controlla che ci siano frame
        pattern = detect_frame_pattern(frames_dir)
        if not pattern:
            self.log_line.emit(" ✗ Nessun frame PNG trovato nella cartella.")
            self.all_done.emit(False, "")
            return

        n_frames = count_frames_in_dir(frames_dir)
        self.log_line.emit(f" ✓ {n_frames} frame trovati — fps={fps}")

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        # Audio disponibile?
        audio = self.audio_path or find_audio_wav(frames_dir)
        has_audio = audio and os.path.exists(audio)
        if has_audio:
            self.log_line.emit(f" ✓ Audio trovato: {Path(audio).name}")
        else:
            self.log_line.emit(" ℹ Nessun audio — video muto")

        self.progress.emit(3)

        # ── Costruisci comando ffmpeg ─────────────────────────────────────
        cmd = [
            FFMPEG_BIN,
            "-framerate", fps,
            "-i", pattern,
        ]
        if has_audio:
            cmd += ["-i", audio]

        cmd += self.video_params

        if has_audio:
            cmd += ["-c:a", "aac", "-b:a", "192k"]
            cmd += ["-map", "0:v:0", "-map", "1:a:0"]

        cmd += ["-progress", "pipe:1", output_file, "-y"]

        self.log_line.emit(" $ " + " ".join(cmd))

        # Stima durata per la progress bar
        duration_est = n_frames / max(self._parse_fps(fps), 1)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in proc.stdout:
                if self._stop:
                    proc.terminate()
                    break
                line = line.rstrip()
                if line.startswith("out_time_ms="):
                    try:
                        ms  = int(line.split("=")[1])
                        t   = ms / 1_000_000
                        if duration_est > 0:
                            pct = min(int(t / duration_est * 100), 99)
                            self.progress.emit(pct)
                    except Exception:
                        pass
                elif line.startswith("progress=end"):
                    self.progress.emit(100)
                elif line.strip() and not line.startswith("progress="):
                    if not any(line.startswith(p) for p in
                               ["frame=","fps=","stream_","bitrate=","speed=",
                                "out_time","total_size","dup_frames","drop_frames"]):
                        self.log_line.emit("  " + line)
            proc.wait()
            success = (proc.returncode == 0
                       and os.path.exists(output_file)
                       and os.path.getsize(output_file) > 0)
        except Exception as e:
            self.log_line.emit(f" ERRORE ricomposizione: {e}")
            self.all_done.emit(False, "")
            return

        self.progress.emit(100)
        if success:
            self.log_line.emit(f"\n✓ RICOMPOSIZIONE COMPLETATA → {output_file}")
        else:
            self.log_line.emit(" ✗ Ricomposizione fallita.")
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception:
                pass

        self.all_done.emit(success, output_file if success else "")

    @staticmethod
    def _parse_fps(fps_str: str) -> float:
        try:
            parts = fps_str.split("/")
            if len(parts) == 2:
                return int(parts[0]) / int(parts[1])
            return float(fps_str)
        except Exception:
            return 25.0
