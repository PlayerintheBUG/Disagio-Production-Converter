#!/usr/bin/env python3
"""
Disagio — subtitle.py
Sottotitoli AI: SubtitleThread (faster-whisper), SubtitleDialog.
"""

import os
import json
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit,
    QCheckBox, QGroupBox, QSizePolicy, QMessageBox, QProgressBar,
    QFrame, QButtonGroup, QRadioButton, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from translations import T
from config import FFMPEG_BIN, WHISPER_AVAILABLE

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

WHISPER_MODELS = [
    ("tiny",     "Tiny   — ~39 MB  | velocissimo, meno preciso"),
    ("base",     "Base   — ~74 MB  | veloce, buona precisione"),
    ("small",    "Small  — ~244 MB | bilanciato  ✓ raccomandato"),
    ("medium",   "Medium — ~769 MB | preciso, più lento"),
    ("large-v3", "Large v3 — ~1.5 GB | massima precisione, richiede GPU"),
]
WHISPER_LANGUAGES = [
    ("auto",  "🌐 Auto-detect"),
    ("it",    "🇮🇹 Italiano"),
    ("en",    "🇬🇧 English"),
    ("de",    "🇩🇪 Deutsch"),
    ("es",    "🇪🇸 Español"),
    ("ja",    "🇯🇵 日本語"),
    ("zh",    "🇨🇳 中文"),
    ("pt",    "🇵🇹 Português"),
    ("ru",    "🇷🇺 Русский"),
    ("ar",    "🇸🇦 العربية"),
    ("ko",    "🇰🇷 한국어"),
]
SUB_COLORS = ["white", "yellow", "#00ffff", "#ff6666", "black"]
SUB_POSITIONS = ["bottom", "top"]

def check_faster_whisper() -> bool:
    """Ritorna True se faster-whisper è importabile."""
    try:
        import importlib
        return importlib.util.find_spec("faster_whisper") is not None
    except Exception:
        return False


class SubtitleDialog(QDialog):
    """
    Dialog per configurare la generazione automatica di sottotitoli
    tramite faster-whisper. Si apre dal pulsante 🎙 Sottotitoli…
    """
    def __init__(self, current: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("dlg_sub_title"))
        self.resize(560, 520)
        self._whisper_ok = check_faster_whisper()

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        # ── Banner "non installato" ────────────────────────────
        self.frm_missing = QFrame()
        self.frm_missing.setStyleSheet(
            "background:#2a1500; border:1px solid #cc5500;"
            "border-radius:8px; padding:10px;")
        ml = QVBoxLayout(self.frm_missing)
        lbl_miss_title = QLabel(T("sub_not_installed_title"))
        lbl_miss_title.setStyleSheet("color:#ff8800; font-weight:bold; font-size:13px;")
        ml.addWidget(lbl_miss_title)
        lbl_miss_body = QLabel(T("sub_not_installed_body"))
        lbl_miss_body.setWordWrap(True)
        lbl_miss_body.setStyleSheet("color:#ffbb66; font-family:monospace; font-size:11px;")
        ml.addWidget(lbl_miss_body)
        lay.addWidget(self.frm_missing)
        self.frm_missing.setVisible(not self._whisper_ok)

        # ── Engine ─────────────────────────────────────────────
        grp_engine = QGroupBox(T("grp_sub_engine"))
        ely = QFormLayout(grp_engine)
        ely.setSpacing(8)

        self.cmb_model = QComboBox()
        for code, label in WHISPER_MODELS:
            self.cmb_model.addItem(label, code)
        saved_model = current.get("model", "small")
        for i in range(self.cmb_model.count()):
            if self.cmb_model.itemData(i) == saved_model:
                self.cmb_model.setCurrentIndex(i)
                break
        ely.addRow(T("lbl_sub_model"), self.cmb_model)

        self.cmb_device = QComboBox()
        self.cmb_device.addItems(["auto", "cpu", "cuda"])
        self.cmb_device.setCurrentText(current.get("device", "auto"))
        ely.addRow(T("lbl_sub_device"), self.cmb_device)

        self.cmb_lang = QComboBox()
        for code, label in WHISPER_LANGUAGES:
            self.cmb_lang.addItem(label, code)
        saved_lang = current.get("language", "auto")
        for i in range(self.cmb_lang.count()):
            if self.cmb_lang.itemData(i) == saved_lang:
                self.cmb_lang.setCurrentIndex(i)
                break
        ely.addRow(T("lbl_sub_lang"), self.cmb_lang)

        lay.addWidget(grp_engine)

        # ── Output mode ────────────────────────────────────────
        grp_out = QGroupBox(T("grp_sub_output"))
        oly = QVBoxLayout(grp_out)
        self.bg_out = QButtonGroup(self)
        self.rb_soft     = QRadioButton(T("rb_sub_soft"))
        self.rb_hard     = QRadioButton(T("rb_sub_hard"))
        self.rb_srt_only = QRadioButton(T("rb_sub_srt_only"))
        self.bg_out.addButton(self.rb_soft,     0)
        self.bg_out.addButton(self.rb_hard,     1)
        self.bg_out.addButton(self.rb_srt_only, 2)
        # blocca i segnali PRIMA di setChecked per evitare
        # che buttonClicked sparino prima che grp_style esista
        self.bg_out.blockSignals(True)
        out_mode = current.get("out_mode", "soft")
        if out_mode == "hard":    self.rb_hard.setChecked(True)
        elif out_mode == "srt":   self.rb_srt_only.setChecked(True)
        else:                     self.rb_soft.setChecked(True)
        self.bg_out.blockSignals(False)
        oly.addWidget(self.rb_soft)
        oly.addWidget(self.rb_hard)
        oly.addWidget(self.rb_srt_only)

        self.lbl_hard_warn = QLabel(T("lbl_sub_hard_warn"))
        self.lbl_hard_warn.setWordWrap(True)
        self.lbl_hard_warn.setStyleSheet(
            "color:#cc8800; font-size:11px; font-style:italic;"
            "background:#1a1000; border:1px solid #cc8800;"
            "border-radius:6px; padding:6px; margin-left:22px;")
        oly.addWidget(self.lbl_hard_warn)
        lay.addWidget(grp_out)

        # ── Stile hard ─────────────────────────────────────────
        self.grp_style = QGroupBox(T("grp_sub_style"))
        sly = QFormLayout(self.grp_style)
        sly.setSpacing(6)

        self.spin_fontsize = QLineEdit(str(current.get("fontsize", 22)))
        self.spin_fontsize.setFixedWidth(60)
        sly.addRow(T("lbl_sub_fontsize"), self.spin_fontsize)

        self.cmb_color = QComboBox()
        self.cmb_color.addItems(SUB_COLORS)
        self.cmb_color.setCurrentText(current.get("color", "white"))
        sly.addRow(T("lbl_sub_color"), self.cmb_color)

        self.cmb_pos = QComboBox()
        self.cmb_pos.addItems(SUB_POSITIONS)
        self.cmb_pos.setCurrentText(current.get("position", "bottom"))
        sly.addRow(T("lbl_sub_position"), self.cmb_pos)

        lay.addWidget(self.grp_style)

        # ── Bottoni ────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_confirm = QPushButton(T("btn_sub_confirm"))
        self.btn_confirm.setObjectName("btn_primary")
        self.btn_confirm.clicked.connect(self.accept)
        self.btn_confirm.setEnabled(self._whisper_ok)
        btn_disable = QPushButton(T("btn_sub_disable"))
        btn_disable.setObjectName("btn_danger")
        btn_disable.clicked.connect(self._disable)
        btn_cancel = QPushButton(T("btn_sub_cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_confirm)
        btn_row.addWidget(btn_disable)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

        self.disabled = False
        # collega il segnale SOLO DOPO che grp_style è stato costruito
        self.bg_out.buttonClicked.connect(self._update_style_visibility)
        # aggiorna visibilità stato iniziale senza emettere segnali
        self._update_style_visibility()

        # disabilita tutto se whisper mancante tranne il banner
        if not self._whisper_ok:
            grp_engine.setEnabled(False)
            grp_out.setEnabled(False)
            self.grp_style.setEnabled(False)

    def _disable(self):
        self.disabled = True
        self.accept()

    def _update_style_visibility(self):
        is_hard = self.rb_hard.isChecked()
        self.lbl_hard_warn.setVisible(is_hard)
        self.grp_style.setVisible(is_hard)
        self.adjustSize()

    def get_settings(self) -> dict:
        return {
            "enabled":  True,
            "model":    self.cmb_model.currentData(),
            "device":   self.cmb_device.currentText(),
            "language": self.cmb_lang.currentData(),
            "out_mode": (
                "hard"  if self.rb_hard.isChecked() else
                "srt"   if self.rb_srt_only.isChecked() else
                "soft"
            ),
            "fontsize": int(self.spin_fontsize.text() or "22"),
            "color":    self.cmb_color.currentText(),
            "position": self.cmb_pos.currentText(),
        }


# ============================================================
#  DIALOG IMPOSTAZIONI AUTO
# ============================================================

class SubtitleThread(QThread):
    """
    Genera sottotitoli per un singolo file video usando faster-whisper,
    poi li integra nel video (soft/hard) o li salva come SRT.
    Emette log_line per il terminale e finished(bool, str) al termine.
    """
    log_line = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, dst_path

    def __init__(self, src: str, dst: str, settings: dict):
        super().__init__()
        self.src      = src
        self.dst      = dst
        self.settings = settings
        self._stop    = False

    def stop(self):
        self._stop = True

    def run(self):
        import tempfile, shutil
        src      = self.src
        dst      = self.dst
        cfg      = self.settings
        model_id = cfg.get("model", "small")
        device   = cfg.get("device", "auto")
        language = cfg.get("language", "auto") or None
        if language == "auto":
            language = None
        out_mode = cfg.get("out_mode", "soft")

        srt_path = str(Path(dst).with_suffix(".srt"))
        self.log_line.emit("\n" + "─"*50)
        self.log_line.emit(f"[SUB] {os.path.basename(src)}")
        self.log_line.emit(f"  modello={model_id}  device={device}  lingua={language or 'auto'}")

        # ── Step 1: trascrizione ──────────────────────────────
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self.log_line.emit("  ✗ faster-whisper non installato — pip install faster-whisper")
            self.finished.emit(False, "")
            return

        # auto device: prova cuda, cade su cpu
        if device == "auto":
            import importlib
            try:
                import torch
                actual_device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                actual_device = "cpu"
        else:
            actual_device = device

        compute_type = "float16" if actual_device == "cuda" else "int8"
        self.log_line.emit(f"  carico modello {model_id} su {actual_device} ({compute_type})…")

        try:
            model = WhisperModel(model_id, device=actual_device, compute_type=compute_type)
        except Exception as e:
            self.log_line.emit(f"  ✗ errore caricamento modello: {e}")
            self.finished.emit(False, "")
            return

        self.log_line.emit("  trascrizione in corso…")
        try:
            segments, info = model.transcribe(
                src,
                language=language,
                beam_size=5,
                vad_filter=True,
            )
            seg_list = list(segments)
        except Exception as e:
            self.log_line.emit(f"  ✗ errore trascrizione: {e}")
            self.finished.emit(False, "")
            return

        if not seg_list:
            self.log_line.emit("  ✗ nessun segmento rilevato — audio assente o silenzio")
            self.finished.emit(False, "")
            return

        self.log_line.emit(f"  lingua rilevata: {info.language}  ({len(seg_list)} segmenti)")

        # ── Step 2: scrittura SRT ────────────────────────────
        def fmt_ts(s):
            h  = int(s // 3600)
            m  = int((s % 3600) // 60)
            se = int(s % 60)
            ms = int((s - int(s)) * 1000)
            return f"{h:02}:{m:02}:{se:02},{ms:03}"

        try:
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, seg in enumerate(seg_list, 1):
                    f.write(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{seg.text.strip()}\n\n")
            self.log_line.emit(f"  SRT salvato: {srt_path}")
        except Exception as e:
            self.log_line.emit(f"  ✗ errore scrittura SRT: {e}")
            self.finished.emit(False, "")
            return

        if self._stop:
            self.finished.emit(False, "")
            return

        if out_mode == "srt":
            self.log_line.emit("  ✓ Solo SRT — video non modificato")
            self.finished.emit(True, srt_path)
            return

        # ── Step 3: integrazione nel video ────────────────────
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)

        if out_mode == "soft":
            # copia stream + aggiungi traccia SRT — nessuna ricodifica
            ext = Path(dst).suffix.lower()
            codec_sub = "mov_text" if ext == ".mp4" else "srt"
            cmd = [
                FFMPEG_BIN, "-i", src, "-i", srt_path,
                "-c", "copy", f"-c:s", codec_sub,
                "-metadata:s:s:0", f"language={info.language}",
                dst, "-y"
            ]
            self.log_line.emit("  modalità SOFT — copia stream + traccia SRT")
        else:
            # hard burn-in: richiede ricodifica video
            fontsize = cfg.get("fontsize", 22)
            color    = cfg.get("color", "white")
            position = cfg.get("position", "bottom")
            # converte colore CSS → ASS (&HAABBGGRR)
            color_map = {
                "white":   "&H00FFFFFF",
                "yellow":  "&H0000FFFF",
                "#00ffff": "&H00FFFF00",
                "#ff6666": "&H006666FF",
                "black":   "&H00000000",
            }
            ass_color  = color_map.get(color, "&H00FFFFFF")
            vmargin    = 20
            valign     = 2 if position == "bottom" else 6  # 2=bottom, 6=top in ASS
            force_style = (
                f"FontSize={fontsize},PrimaryColour={ass_color},"
                f"Alignment={valign},MarginV={vmargin},BorderStyle=1,Outline=1,Shadow=0"
            )
            # escape percorso per ffmpeg subtitles filter (windows compat)
            srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
            cmd = [
                FFMPEG_BIN, "-i", src,
                "-vf", f"subtitles='{srt_escaped}':force_style='{force_style}'",
                "-c:a", "copy",
                dst, "-y"
            ]
            self.log_line.emit(f"  modalità HARD — burn-in font={fontsize} colore={color} pos={position}")

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
                if line.strip() and not any(line.startswith(p) for p in
                        ["frame=","fps=","stream_","bitrate=","speed=",
                         "out_time","total_size","dup_frames","drop_frames","progress="]):
                    self.log_line.emit("  " + line)
            proc.wait()
            success = proc.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 0
        except Exception as e:
            self.log_line.emit(f"  ✗ errore ffmpeg: {e}")
            success = False

        if success:
            self.log_line.emit(f"  ✓ OK → {dst}")
        else:
            self.log_line.emit("  ✗ ERRORE integrazione sottotitoli")
            if os.path.exists(dst):
                try: os.remove(dst)
                except Exception: pass

        self.finished.emit(success, dst if success else "")


# ============================================================
#  THREAD DI CONVERSIONE
# ============================================================
