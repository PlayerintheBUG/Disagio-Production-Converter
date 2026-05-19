#!/usr/bin/env python3
# ============================================================
#  disagio_converter.py  —  DISAGIO PRODUCTION CONVERTER
#  Converte video e audio con GUI PyQt6 + terminale in RT
# ============================================================
#  Copyright (C) 2026 PlayerintheBUG
#
#  Questo programma è software libero: puoi ridistribuirlo e/o
#  modificarlo secondo i termini della Licenza Pubblica Generica
#  GNU (GPL) versione 3, come pubblicata dalla Free Software Foundation.
#
#  Questo programma è distribuito nella speranza che sia utile,
#  ma SENZA ALCUNA GARANZIA; senza nemmeno la garanzia implicita
#  di COMMERCIABILITÀ o IDONEITÀ PER UNO SCOPO PARTICOLARE.
#  Vedi la licenza GNU GPL v3 per maggiori dettagli.
# ============================================================

import sys
import os
import subprocess
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QButtonGroup, QRadioButton, QComboBox,
    QLineEdit, QFileDialog, QPlainTextEdit, QProgressBar,
    QFrame, QScrollArea, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

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
    # DNxHR e ProRes sono sempre CPU — nessun encoder GPU disponibile
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

VIDEO_EXTENSIONS = {".mp4",".mkv",".mov",".avi",".webm",".flv",
                    ".mts",".m2ts",".ts",".wmv",".vob",".mpg",
                    ".mpeg",".ogv",".divx",".m4v",".3gp"}

AUDIO_EXTENSIONS = {".mp3",".flac",".wav",".aac",".m4a",".ogg",
                    ".opus",".wma",".aiff",".aif",".ac3",".dts",
                    ".mka",".wv",".ape",".ra",".voc",".w64"}

# ============================================================
#  STILE
# ============================================================
STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #2d2d4e;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: bold;
    color: #a0a0ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}
QPushButton {
    background-color: #2d2d4e;
    color: #e0e0e0;
    border: 1px solid #3d3d6e;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton:hover { background-color: #3d3d6e; border-color: #6060cc; }
QPushButton:pressed { background-color: #5050aa; }
QPushButton#btn_primary {
    background-color: #4444aa;
    border-color: #6060dd;
    color: #ffffff;
}
QPushButton#btn_primary:hover { background-color: #5555cc; }
QPushButton#btn_primary:disabled {
    background-color: #2a2a3e; color: #555555; border-color: #333355;
}
QPushButton#btn_danger { background-color: #6e2d2d; border-color: #aa4444; }
QPushButton#btn_danger:hover { background-color: #aa3333; }
QRadioButton { spacing: 8px; color: #e0e0e0; padding: 4px; }
QRadioButton::indicator {
    width: 16px; height: 16px; border-radius: 8px;
    border: 2px solid #5050aa; background: #1a1a2e;
}
QRadioButton::indicator:checked { background: #6060dd; border-color: #8080ff; }
QCheckBox { spacing: 8px; color: #e0e0e0; padding: 4px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 4px;
    border: 2px solid #5050aa; background: #1a1a2e;
}
QCheckBox::indicator:checked { background: #6060dd; border-color: #8080ff; }
QComboBox {
    background-color: #2d2d4e; border: 1px solid #3d3d6e;
    border-radius: 6px; padding: 6px 10px; color: #e0e0e0; min-width: 160px;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #2d2d4e; border: 1px solid #5050aa;
    selection-background-color: #4444aa; color: #e0e0e0;
}
QLineEdit {
    background-color: #2d2d4e; border: 1px solid #3d3d6e;
    border-radius: 6px; padding: 6px 10px; color: #e0e0e0;
}
QLineEdit:focus { border-color: #6060dd; }
QPlainTextEdit {
    background-color: #0d0d1a; color: #00ff88;
    border: 1px solid #2d2d4e; border-radius: 6px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 12px;
}
QProgressBar {
    background-color: #2d2d4e; border: 1px solid #3d3d6e;
    border-radius: 4px; height: 10px; text-align: center; color: #ffffff;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4444aa,stop:1 #6060ff);
    border-radius: 4px;
}
QScrollArea { border: none; }
QLabel#section_title {
    color: #8080ff; font-size: 11px; font-weight: bold; letter-spacing: 1px;
}
QLabel#file_label { color: #aaaaff; font-size: 12px; padding: 4px; }
QFrame#separator { background-color: #2d2d4e; max-height: 1px; }
"""

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
        self.jobs   = jobs
        self.params = params
        self._stop  = False

    def stop(self):
        self._stop = True

    def get_video_preset(self):
        gpu    = self.params.get("gpu", "NVIDIA")
        vcodec = self.params.get("vcodec", "AV1")
        vqual  = self.params.get("vqual", "Medio")

        # DNxHR e ProRes non hanno varianti GPU
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS[vcodec][vqual]

        gpu_presets = VIDEO_PRESETS.get(gpu, {})
        codec_presets = gpu_presets.get(vcodec, {})
        return codec_presets.get(vqual, "")

    def build_cmd(self, src, dst):
        # modalità manuale
        manual = self.params.get("manual_cmd", "")
        if manual:
            filled = manual.replace("{INPUT}", src).replace(
                "{OUTPUT}", str(Path(dst).with_suffix("")))
            parts = filled.split()
            parts = parts[:-1] + ["-progress", "pipe:1"] + [parts[-1]]
            return parts

        mode   = self.params["mode"]
        sample = self.params["sample_rate"]
        hwaccel = self.params.get("hwaccel", True)

        sr_flag = [] if sample == "Mantieni originale" else ["-ar", sample.replace(" Hz", "")]
        hw_flag = ["-hwaccel", "auto"] if hwaccel else []

        audio_opts = self.params["audio_preset"].split()
        cmd = ["ffmpeg"] + hw_flag + ["-i", src]

        if mode == "audio":
            cmd += ["-vn"] + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]
        else:
            video_opts = self.get_video_preset().split()
            cmd += video_opts + audio_opts + sr_flag + [dst, "-y", "-progress", "pipe:1"]

        return cmd

    def get_duration(self, src):
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", src],
                capture_output=True, text=True, timeout=15
            )
            return float(r.stdout.strip())
        except Exception:
            return 0.0

    def run(self):
        ok = err = 0
        total = len(self.jobs)

        for idx, (src, dst) in enumerate(self.jobs):
            if self._stop:
                break

            fname = os.path.basename(src)
            self.log_line.emit(f"\n{'─'*50}")
            self.log_line.emit(f"[{idx+1}/{total}] {fname}")
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
                        proc.terminate()
                        break
                    line = line.rstrip()
                    if line.startswith("out_time_ms="):
                        try:
                            ms = int(line.split("=")[1])
                            t  = ms / 1_000_000
                            if duration > 0:
                                pct = min(int(t / duration * 100), 99)
                                self.progress.emit(int((idx + pct/100) / total * 100))
                        except Exception:
                            pass
                    elif line.startswith("progress=end"):
                        self.progress.emit(int((idx+1) / total * 100))
                    elif line.strip() and not any(line.startswith(p) for p in
                            ["frame=","fps=","stream_","bitrate=","speed=",
                             "out_time","total_size","dup_frames","drop_frames"]):
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
                    if os.path.exists(dst):
                        os.remove(dst)
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
        self.setMinimumSize(860, 820)
        self.resize(940, 900)
        self.params = {}
        self.jobs   = []
        self.thread = None
        self._build_ui()

    # ----------------------------------------------------------
    #  BUILD UI
    # ----------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 16)

        title = QLabel("DISAGIO PRODUCTION CONVERTER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("monospace", 15, QFont.Weight.Bold))
        title.setStyleSheet("color:#8080ff; letter-spacing:2px; padding:6px;")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        opts_w = QWidget()
        self.opts_layout = QVBoxLayout(opts_w)
        self.opts_layout.setSpacing(10)
        scroll.setWidget(opts_w)
        root.addWidget(scroll, stretch=3)

        # ── STEP 1: sorgente ──────────────────────────────────
        self._section("STEP 1 — Sorgente")
        row1 = QHBoxLayout()
        self.bg_mode = QButtonGroup(self)
        self.rb_single = QRadioButton("File singolo")
        self.rb_folder = QRadioButton("Cartella intera")
        self.rb_single.setChecked(True)
        self.bg_mode.addButton(self.rb_single, 0)
        self.bg_mode.addButton(self.rb_folder, 1)
        self.rb_single.toggled.connect(self._on_mode_changed)
        row1.addWidget(self.rb_single)
        row1.addWidget(self.rb_folder)
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

        # ── STEP 2: tipo output ───────────────────────────────
        self._section("STEP 2 — Tipo output")
        row2 = QHBoxLayout()
        self.bg_type = QButtonGroup(self)
        self.rb_video = QRadioButton("Video + Audio")
        self.rb_audio = QRadioButton("Solo Audio")
        self.rb_video.setChecked(True)
        self.bg_type.addButton(self.rb_video, 0)
        self.bg_type.addButton(self.rb_audio, 1)
        self.rb_video.toggled.connect(self._on_type_changed)
        row2.addWidget(self.rb_video)
        row2.addWidget(self.rb_audio)
        row2.addStretch()
        self.opts_layout.addLayout(row2)
        self._sep()

        # ── STEP 3: video ─────────────────────────────────────
        self.grp_video = QGroupBox("STEP 3 — Video")
        vlay = QVBoxLayout(self.grp_video)

        # GPU selector
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

        # hwaccel flag
        hw_row = QHBoxLayout()
        self.chk_hwaccel = QCheckBox("Accelerazione hardware decodifica  (-hwaccel auto)")
        self.chk_hwaccel.setChecked(True)
        self.chk_hwaccel.toggled.connect(self._update_cmd_preview)
        hw_row.addWidget(self.chk_hwaccel)
        hw_row.addStretch()
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
        cc_row.addWidget(self.cmb_vcodec)
        cc_row.addStretch()
        vlay.addLayout(cc_row)

        # qualità video
        vq_row = QHBoxLayout()
        vq_row.addWidget(QLabel("Qualità video:"))
        self.bg_vqual = QButtonGroup(self)
        for i, q in enumerate(["Alto", "Medio", "Basso"]):
            rb = QRadioButton(q)
            if q == "Medio": rb.setChecked(True)
            self.bg_vqual.addButton(rb, i)
            rb.toggled.connect(self._update_cmd_preview)
            vq_row.addWidget(rb)
        vq_row.addStretch()
        vlay.addLayout(vq_row)
        self.opts_layout.addWidget(self.grp_video)

        # ── STEP 4: audio ─────────────────────────────────────
        self.grp_audio = QGroupBox("STEP 4 — Audio")
        alay = QVBoxLayout(self.grp_audio)

        ac_row = QHBoxLayout()
        ac_row.addWidget(QLabel("Codec audio:"))
        self.cmb_acodec = QComboBox()
        self.cmb_acodec.addItems(AUDIO_CODECS)
        self.cmb_acodec.currentTextChanged.connect(self._update_cmd_preview)
        ac_row.addWidget(self.cmb_acodec)
        ac_row.addStretch()
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
        sr_row.addWidget(self.cmb_sample)
        sr_row.addStretch()
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

        # ── STEP 6: comando ffmpeg ────────────────────────────
        self.grp_cmd = QGroupBox("Comando ffmpeg (aggiornato live)")
        clay = QVBoxLayout(self.grp_cmd)
        self.txt_cmd = QLineEdit()
        self.txt_cmd.setReadOnly(True)
        self.txt_cmd.setFont(QFont("monospace", 11))
        self.txt_cmd.setStyleSheet(
            "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
            "border-radius:6px; padding:6px 10px;")
        clay.addWidget(self.txt_cmd)

        cmd_btn_row = QHBoxLayout()
        self.btn_manual = QPushButton("✏  Abilita modifica manuale")
        self.btn_manual.setCheckable(True)
        self.btn_manual.clicked.connect(self._toggle_manual)
        self.lbl_hint = QLabel("Usa {INPUT} e {OUTPUT} come segnaposto per i percorsi file")
        self.lbl_hint.setStyleSheet("color:#666688; font-size:11px;")
        self.lbl_hint.setVisible(False)
        cmd_btn_row.addWidget(self.btn_manual)
        cmd_btn_row.addWidget(self.lbl_hint)
        cmd_btn_row.addStretch()
        clay.addLayout(cmd_btn_row)
        self.opts_layout.addWidget(self.grp_cmd)

        # init
        self._on_container_changed(self.cmb_container.currentText())
        self._on_type_changed()

        # ── pulsante CONVERTI ─────────────────────────────────
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

        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(180)
        self.terminal.setPlaceholderText("L'output di ffmpeg apparirà qui…")
        root.addWidget(self.terminal, stretch=2)

        self.btn_stop = QPushButton("■  INTERROMPI")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setVisible(False)
        self.btn_stop.clicked.connect(self._stop)
        root.addWidget(self.btn_stop)

    # ----------------------------------------------------------
    #  HELPERS UI
    # ----------------------------------------------------------
    def _section(self, text):
        lbl = QLabel(text.upper())
        lbl.setObjectName("section_title")
        self.opts_layout.addWidget(lbl)

    def _sep(self):
        f = QFrame(); f.setObjectName("separator")
        f.setFrameShape(QFrame.Shape.HLine)
        self.opts_layout.addWidget(f)

    # ----------------------------------------------------------
    #  SLOT UI
    # ----------------------------------------------------------
    def _on_mode_changed(self):
        is_single = self.rb_single.isChecked()
        if is_single:
            self.grp_name.setTitle("STEP 5 — Nome file output")
            self.lbl_name.setText("Nome (senza estensione):")
            self.txt_name.setPlaceholderText("Lascia vuoto per mantenere il nome originale")
        else:
            self.grp_name.setTitle("STEP 5 — Prefisso file output")
            self.lbl_name.setText("Prefisso:")
            self.txt_name.setPlaceholderText("Lascia vuoto per nessun prefisso")
        self._update_cmd_preview()

    def _on_type_changed(self):
        is_video = self.rb_video.isChecked()
        self.grp_video.setVisible(is_video)
        step_a = "STEP 4 — Audio" if is_video else "STEP 3 — Audio"
        self.grp_audio.setTitle(step_a)
        step_n = "STEP 5 — Nome file output" if is_video else "STEP 4 — Nome file output"
        self.grp_name.setTitle(step_n if self.rb_single.isChecked() else
                               step_n.replace("Nome file output", "Prefisso file output"))
        self._update_cmd_preview()

    def _on_container_changed(self, container):
        codecs = CONTAINER_CODECS.get(container, [])
        self.cmb_vcodec.clear()
        self.cmb_vcodec.addItems(codecs)
        # nascondi selettore GPU per DNxHR/ProRes
        is_gpu_codec = all(c not in ("DNxHR", "ProRes") for c in codecs)
        for btn in self.bg_gpu.buttons():
            btn.setEnabled(is_gpu_codec)
        self.chk_hwaccel.setEnabled(is_gpu_codec)
        self._update_cmd_preview()

    def _get_selected_gpu(self):
        btn = self.bg_gpu.checkedButton()
        return btn.text() if btn else "NVIDIA"

    def _get_video_preset_str(self):
        gpu    = self._get_selected_gpu()
        vcodec = self.cmb_vcodec.currentText()
        vqual  = (self.bg_vqual.checkedButton().text()
                  if self.bg_vqual.checkedButton() else "Medio")
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS[vcodec][vqual]
        return VIDEO_PRESETS.get(gpu, {}).get(vcodec, {}).get(vqual, "")

    def _update_cmd_preview(self):
        if hasattr(self, "btn_manual") and self.btn_manual.isChecked():
            return

        mode   = "audio" if self.rb_audio.isChecked() else "video"
        acodec = self.cmb_acodec.currentText()
        aqual  = (self.bg_aqual.checkedButton().text()
                  if self.bg_aqual.checkedButton() else "Medio")
        sample = self.cmb_sample.currentText()
        audio_p = AUDIO_PRESETS.get(acodec, {}).get(aqual, "")
        if sample != "Mantieni originale":
            audio_p += f" -ar {sample.replace(' Hz', '')}"

        hwaccel = self.chk_hwaccel.isChecked()
        hw_str  = "-hwaccel auto " if hwaccel else ""

        if mode == "audio":
            ext = AUDIO_ONLY_EXT.get(acodec, "wav")
            cmd = f"ffmpeg {hw_str}-i {{INPUT}} -vn {audio_p} {{OUTPUT}}.{ext} -y"
        else:
            video_p = self._get_video_preset_str()
            ext_map = {"MKV (.mkv)": "mkv", "MP4 (.mp4)": "mp4", "MOV (.mov)": "mov"}
            ext = ext_map.get(self.cmb_container.currentText(), "mkv")
            cmd = f"ffmpeg {hw_str}-i {{INPUT}} {video_p} {audio_p} {{OUTPUT}}.{ext} -y"

        if hasattr(self, "txt_cmd"):
            self.txt_cmd.setText(cmd.strip())

    def _toggle_manual(self, checked):
        self.txt_cmd.setReadOnly(not checked)
        self.lbl_hint.setVisible(checked)

        controls = ([self.rb_video, self.rb_audio, self.rb_single, self.rb_folder,
                     self.cmb_container, self.cmb_vcodec, self.cmb_acodec,
                     self.cmb_sample, self.chk_hwaccel]
                    + self.bg_vqual.buttons()
                    + self.bg_aqual.buttons()
                    + self.bg_gpu.buttons())
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
    #  PARAMETRI E JOBS
    # ----------------------------------------------------------
    def _collect_params(self):
        mode    = "audio" if self.rb_audio.isChecked() else "video"
        vcodec  = self.cmb_vcodec.currentText()
        acodec  = self.cmb_acodec.currentText()
        vqual   = (self.bg_vqual.checkedButton().text()
                   if self.bg_vqual.checkedButton() else "Medio")
        aqual   = (self.bg_aqual.checkedButton().text()
                   if self.bg_aqual.checkedButton() else "Medio")
        gpu     = self._get_selected_gpu()
        sample  = self.cmb_sample.currentText()
        hwaccel = self.chk_hwaccel.isChecked()

        ext_map  = {"MKV (.mkv)": "mkv", "MP4 (.mp4)": "mp4", "MOV (.mov)": "mov"}
        video_ext = ext_map.get(self.cmb_container.currentText(), "mkv")
        audio_ext = AUDIO_ONLY_EXT.get(acodec, "wav")

        audio_preset = AUDIO_PRESETS.get(acodec, {}).get(aqual, "")

        return {
            "mode":         mode,
            "video_ext":    video_ext,
            "audio_ext":    audio_ext,
            "audio_preset": audio_preset,
            "sample_rate":  sample,
            "gpu":          gpu,
            "hwaccel":      hwaccel,
            "vcodec":       vcodec,
            "acodec":       acodec,
            "vqual":        vqual,
            "aqual":        aqual,
        }

    def _unique_path(self, dst):
        if not os.path.exists(dst):
            return dst
        stem = Path(dst).stem
        ext  = Path(dst).suffix
        d    = Path(dst).parent
        i    = 1
        while True:
            c = d / f"{stem}_{i}{ext}"
            if not c.exists():
                return str(c)
            i += 1

    def _collect_jobs(self, params):
        path      = self.lbl_file.text()
        is_single = self.rb_single.isChecked()
        mode      = params["mode"]
        out_ext   = params["audio_ext"] if mode == "audio" else params["video_ext"]
        prefix    = self.txt_name.text().strip()
        jobs      = []

        valid_exts = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS

        if is_single:
            if not os.path.isfile(path):
                return []
            stem = prefix if prefix else Path(path).stem
            dst  = str(Path(path).parent / f"{stem}.{out_ext}")
            jobs.append((path, self._unique_path(dst)))
        else:
            if not os.path.isdir(path):
                return []
            out_dir = os.path.join(path, "CONVERTITI_DISAGIO")
            for root_d, _, files in os.walk(path):
                if root_d.startswith(out_dir):
                    continue
                for f in sorted(files):
                    if Path(f).suffix.lower() not in valid_exts:
                        continue
                    src  = os.path.join(root_d, f)
                    stem = f"{prefix}_{Path(f).stem}" if prefix else Path(f).stem
                    rel  = os.path.relpath(root_d, path)
                    dst  = os.path.join(out_dir, rel, f"{stem}.{out_ext}")
                    jobs.append((src, self._unique_path(dst)))
        return jobs

    # ----------------------------------------------------------
    #  AVVIO / STOP
    # ----------------------------------------------------------
    def _start(self):
        path = self.lbl_file.text()
        if not path or path == "Nessun file selezionato":
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un file o una cartella.")
            return

        params = self._collect_params()
        jobs   = self._collect_jobs(params)

        if not jobs:
            QMessageBox.warning(self, "Nessun file", "Nessun file da convertire trovato.")
            return

        if self.btn_manual.isChecked():
            params["manual_cmd"] = self.txt_cmd.text().strip()
        else:
            params.pop("manual_cmd", None)

        gpu_label = params["gpu"] if params["mode"] == "video" else "—"
        hw_label  = "Sì" if params["hwaccel"] else "No"
        prefix    = self.txt_name.text().strip()

        lines = [f"File da convertire: {len(jobs)}"]
        if params["mode"] == "video":
            lines += [
                f"Encoder GPU: {gpu_label}",
                f"HW decoding: {hw_label}",
                f"Codec video: {params['vcodec']} — {params['vqual']}",
                f"Container: .{params['video_ext']}",
            ]
        lines += [
            f"Codec audio: {params['acodec']} — {params['aqual']}",
            f"Sample rate: {params['sample_rate']}",
        ]
        if prefix and not self.rb_single.isChecked():
            lines.append(f"Prefisso: {prefix}_")

        if QMessageBox.question(
            self, "Conferma", "\n".join(lines),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        ) != QMessageBox.StandardButton.Ok:
            return

        self.jobs   = jobs
        self.params = params

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

    # ----------------------------------------------------------
    #  SLOT THREAD
    # ----------------------------------------------------------
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
    if not shutil.which("ffmpeg"):
        print("ERRORE: ffmpeg non trovato. Installa con: sudo dnf install ffmpeg")
        sys.exit(1)
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setApplicationName("DISAGIO PRODUCTION CONVERTER")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
