#!/usr/bin/env python3
"""
Disagio — main.py
MainWindow: interfaccia utente principale e orchestrazione.

Per aggiungere un nuovo modulo:
    1. Crea il file nella cartella disagio/
    2. Aggiungilo agli import qui sotto
    3. Usalo in MainWindow
"""

import sys
import os
import json
import shutil
from pathlib import Path

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

# ── Moduli Disagio ────────────────────────────────────────────────────────
from config import (
    CONFIG_FILE, SCRIPT_DIR, FFMPEG_BIN, FFPROBE_BIN,
    CONTAINER_CODECS, VIDEO_PRESETS, AUDIO_CODECS, AUDIO_PRESETS,
    AUDIO_ONLY_EXT, SAMPLE_RATES, GPU_OPTIONS, RESOLUTIONS,
    VIDEO_EXTENSIONS, AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, RAW_EXTENSIONS,
    IMAGE_OUTPUT_FORMATS, LICENSE_TEXT, WHISPER_AVAILABLE,
)
from translations import T, set_language, TRANSLATIONS, LANGUAGES, _LANG
from utils import (
    probe_video, image_quality_label, build_image_ffmpeg_args,
    auto_compute_cq,
    res_display_items, res_display_for, res_internal_key,
    sr_display_items, sr_internal_key, sr_display_for,
    load_config, save_config,
)
from styles import get_stylesheet, THEMES, DEFAULT_THEMES
from presets import (
    PRESETS_KEY, load_ffmpeg_presets, save_ffmpeg_preset, delete_ffmpeg_preset,
)
from video import ConvertThread
from subtitle import SubtitleDialog, SubtitleThread
from dialogs import (
    ThemeEditorDialog, LicenseDialog,
    AutoSettingsDialog,
    FfmpegPresetSaveDialog, FfmpegPresetLoadDialog,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DISAGIO PRODUCTION CONVERTER")
        self.setMinimumSize(880, 860)
        self.resize(960, 940)
        self.params = {}
        self.jobs   = []
        self.thread = None
        # impostazioni dialogo AUTO (persistono durante la sessione)
        self._auto_settings = {
            "use_bpp_probe": False,
            "cap_mode":      "none",
            "cap_value":     0.0,
            "cap_unit":      "",
        }
        # impostazioni sottotitoli (disabled per default)
        self._sub_settings = {"enabled": False}
        self._sub_thread = None
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
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(list(LANGUAGES.keys()))
        # set current language from config
        _cfg_lang = load_config().get("language", "it")
        for display_name, code in LANGUAGES.items():
            if code == _cfg_lang:
                self.cmb_lang.setCurrentText(display_name)
                break
        self.cmb_lang.currentTextChanged.connect(self._change_language)
        title_row.addWidget(self.cmb_lang)
        title_row.addSpacing(10)
        title_row.addWidget(QLabel(T("lbl_theme")))
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(list(THEMES.keys()))
        cfg = load_config()
        self.cmb_theme.setCurrentText(cfg.get("theme", "Dark Classic"))
        self.cmb_theme.currentTextChanged.connect(self._change_theme)
        title_row.addWidget(self.cmb_theme)
        btn_edit_theme = QPushButton(T("btn_edit_theme"))
        # Use a generic icon to indicate theme editing (standard "preferences" icon)
        try:
            from PyQt6.QtGui import QIcon
            btn_edit_theme.setIcon(QIcon.fromTheme("preferences-desktop-theme"))
        except Exception:
            pass
        btn_edit_theme.setToolTip(T("btn_edit_theme_tip"))
        btn_edit_theme.clicked.connect(self._edit_theme)
        title_row.addWidget(btn_edit_theme)
        title_row.addSpacing(10)
        btn_lic = QPushButton(T("btn_license"))
        btn_lic.setObjectName("btn_license")
        btn_lic.setToolTip(T("btn_license_tip"))
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
        self._section(T("step1_title"))
        row1 = QHBoxLayout()
        self.bg_mode = QButtonGroup(self)
        self.rb_single = QRadioButton(T("rb_single"))
        self.rb_folder = QRadioButton(T("rb_folder"))
        self.rb_single.setChecked(True)
        self.bg_mode.addButton(self.rb_single, 0)
        self.bg_mode.addButton(self.rb_folder, 1)
        self.rb_single.toggled.connect(self._on_mode_changed)
        row1.addWidget(self.rb_single); row1.addWidget(self.rb_folder)
        row1.addStretch()
        self.opts_layout.addLayout(row1)
        frow = QHBoxLayout()
        self.lbl_file = QLabel(T("lbl_no_file"))
        self.lbl_file.setObjectName("file_label")
        self.lbl_file.setWordWrap(True)
        self.btn_browse = QPushButton(T("btn_browse"))
        self.btn_browse.clicked.connect(self._browse)
        frow.addWidget(self.lbl_file, stretch=1)
        frow.addWidget(self.btn_browse)
        self.opts_layout.addLayout(frow)
        self._sep()
        # ── STEP 2 ────────────────────────────────────────────
        self._section(T("step2_title"))
        row2 = QHBoxLayout()
        self.bg_type = QButtonGroup(self)
        self.rb_video = QRadioButton(T("rb_video"))
        self.rb_audio = QRadioButton(T("rb_audio"))
        self.rb_image = QRadioButton(T("rb_image"))
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
        self.grp_video = QGroupBox(T("grp_video"))
        vlay = QVBoxLayout(self.grp_video)
        # GPU
        gpu_row = QHBoxLayout()
        gpu_row.addWidget(QLabel(T("lbl_gpu")))
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
        self.chk_hwaccel = QCheckBox(T("chk_hwaccel"))
        self.chk_hwaccel.setChecked(True)
        self.chk_hwaccel.toggled.connect(self._update_cmd_preview)
        hw_row.addWidget(self.chk_hwaccel); hw_row.addStretch()
        vlay.addLayout(hw_row)
        # container + codec
        cc_row = QHBoxLayout()
        cc_row.addWidget(QLabel(T("lbl_container")))
        self.cmb_container = QComboBox()
        self.cmb_container.addItems(CONTAINER_CODECS.keys())
        self.cmb_container.currentTextChanged.connect(self._on_container_changed)
        cc_row.addWidget(self.cmb_container)
        cc_row.addSpacing(20)
        cc_row.addWidget(QLabel(T("lbl_vcodec")))
        self.cmb_vcodec = QComboBox()
        self.cmb_vcodec.currentTextChanged.connect(self._update_cmd_preview)
        cc_row.addWidget(self.cmb_vcodec); cc_row.addStretch()
        vlay.addLayout(cc_row)
        # qualità + AUTO
        vq_row = QHBoxLayout()
        vq_row.addWidget(QLabel(T("lbl_vqual")))
        self.bg_vqual = QButtonGroup(self)
        _qual_keys = ["qual_high", "qual_mid", "qual_low", "qual_auto"]
        for i, q in enumerate([T("qual_high"), T("qual_mid"), T("qual_low"), T("qual_auto")]):
            rb = QRadioButton(q)
            if i == 1: rb.setChecked(True)
            self.bg_vqual.addButton(rb, i)
            rb.toggled.connect(self._on_vqual_changed)
            vq_row.addWidget(rb)
        self.lbl_auto_warn = QLabel(T("lbl_auto_warn"))
        self.lbl_auto_warn.setObjectName("auto_warn")
        self.lbl_auto_warn.setVisible(False)
        vq_row.addWidget(self.lbl_auto_warn)
        self.btn_auto_settings = QPushButton(T("btn_auto_settings"))
        self.btn_auto_settings.setVisible(False)
        self.btn_auto_settings.clicked.connect(self._open_auto_settings)
        vq_row.addWidget(self.btn_auto_settings)
        vq_row.addStretch()
        vlay.addLayout(vq_row)
        # risoluzione output
        res_row = QHBoxLayout()
        res_row.addWidget(QLabel(T("lbl_resolution")))
        self.cmb_res = QComboBox()
        self.cmb_res.addItems(res_display_items())
        self.cmb_res.setCurrentText(res_display_for("Mantieni originale"))
        self.cmb_res.currentTextChanged.connect(self._update_cmd_preview)
        res_row.addWidget(self.cmb_res)
        res_row.addWidget(QLabel(T("lbl_res_note")))
        res_row.addStretch()
        vlay.addLayout(res_row)
        self.opts_layout.addWidget(self.grp_video)

        # ── STEP 3 (immagini): immagini ───────────────────────
        self.grp_image = QGroupBox(T("grp_image"))
        ilay = QVBoxLayout(self.grp_image)
        ifmt_row = QHBoxLayout()
        ifmt_row.addWidget(QLabel(T("lbl_imgfmt")))
        self.cmb_imgfmt = QComboBox()
        self.cmb_imgfmt.addItems(IMAGE_OUTPUT_FORMATS.keys())
        self.cmb_imgfmt.currentTextChanged.connect(self._on_imgfmt_changed)
        ifmt_row.addWidget(self.cmb_imgfmt); ifmt_row.addStretch()
        ilay.addLayout(ifmt_row)
        # Slider qualità
        ilay.addSpacing(4)
        slider_header = QHBoxLayout()
        slider_header.addWidget(QLabel(T("lbl_imgqual_header")))
        slider_header.addStretch()
        ilay.addLayout(slider_header)
        # Etichette sinistra/destra con slider al centro
        slider_row = QHBoxLayout()
        lbl_low = QLabel(T("lbl_img_low").replace("\\n","\n"))
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
        lbl_high = QLabel(T("lbl_img_high").replace("\\n","\n"))
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
        self.lbl_bmp_warn = QLabel(T("lbl_bmp_warn"))
        self.lbl_bmp_warn.setStyleSheet("color:#888888; font-size:11px; font-style:italic;")
        self.lbl_bmp_warn.setVisible(False)
        ilay.addWidget(self.lbl_bmp_warn)
        # Nota RAW (mostrata solo in modalità cartella)
        self.lbl_raw_note = QLabel(T("lbl_raw_note"))
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
        ac_row.addWidget(QLabel(T("lbl_acodec")))
        self.cmb_acodec = QComboBox()
        self.cmb_acodec.addItems(AUDIO_CODECS)
        self.cmb_acodec.currentTextChanged.connect(self._update_cmd_preview)
        ac_row.addWidget(self.cmb_acodec); ac_row.addStretch()
        alay.addLayout(ac_row)
        aq_row = QHBoxLayout()
        aq_row.addWidget(QLabel(T("lbl_aqual")))
        self.bg_aqual = QButtonGroup(self)
        for i, q in enumerate([T("qual_high"), T("qual_mid"), T("qual_low")]):
            rb = QRadioButton(q)
            if i == 1: rb.setChecked(True)
            self.bg_aqual.addButton(rb, i)
            rb.toggled.connect(self._update_cmd_preview)
            aq_row.addWidget(rb)
        aq_row.addStretch()
        alay.addLayout(aq_row)
        sr_row = QHBoxLayout()
        sr_row.addWidget(QLabel(T("lbl_samplerate")))
        self.cmb_sample = QComboBox()
        self.cmb_sample.addItems(sr_display_items())
        self.cmb_sample.setCurrentText(sr_display_for("48000 Hz"))
        self.cmb_sample.currentTextChanged.connect(self._update_cmd_preview)
        sr_row.addWidget(self.cmb_sample); sr_row.addStretch()
        alay.addLayout(sr_row)
        self.opts_layout.addWidget(self.grp_audio)
        # ── STEP 5: nome / prefisso ───────────────────────────
        self.grp_name = QGroupBox(T("grp_name_single_v"))
        nlay = QHBoxLayout(self.grp_name)
        self.lbl_name = QLabel(T("lbl_name_single"))
        nlay.addWidget(self.lbl_name)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText(T("txt_name_ph_single"))
        nlay.addWidget(self.txt_name)
        self.opts_layout.addWidget(self.grp_name)
        # ── comando ffmpeg ─────────────────────────────────────
        self.grp_cmd = QGroupBox(T("grp_cmd"))
        clay = QVBoxLayout(self.grp_cmd)
        self.txt_cmd = QLineEdit()
        self.txt_cmd.setReadOnly(True)
        self.txt_cmd.setFont(QFont("monospace", 11))
        self.txt_cmd.setStyleSheet(
            "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
            "border-radius:6px; padding:6px 10px;")
        clay.addWidget(self.txt_cmd)
        cbr = QHBoxLayout()
        self.btn_manual = QPushButton(T("btn_manual"))
        self.btn_manual.setCheckable(True)
        self.btn_manual.clicked.connect(self._toggle_manual)
        self.lbl_hint = QLabel(T("lbl_hint"))
        self.lbl_hint.setStyleSheet("color:#666688; font-size:11px;")
        self.lbl_hint.setVisible(False)
        self.btn_save_preset = QPushButton(T("btn_save_preset"))
        self.btn_save_preset.clicked.connect(self._save_ffmpeg_preset)
        self.btn_load_preset = QPushButton(T("btn_load_preset"))
        self.btn_load_preset.clicked.connect(self._load_ffmpeg_preset)
        cbr.addWidget(self.btn_manual)
        cbr.addWidget(self.lbl_hint)
        cbr.addStretch()
        cbr.addWidget(self.btn_save_preset)
        cbr.addWidget(self.btn_load_preset)
        clay.addLayout(cbr)
        self.opts_layout.addWidget(self.grp_cmd)
        # init
        self._on_container_changed(self.cmb_container.currentText())
        self._on_type_changed()
        self._on_imgfmt_changed(self.cmb_imgfmt.currentText())
        # ── CONVERTI ──────────────────────────────────────────
        go_row = QHBoxLayout()
        self.btn_subtitles = QPushButton(T("btn_subtitles"))
        self.btn_subtitles.setMinimumHeight(42)
        self.btn_subtitles.setFont(QFont("monospace", 11))
        self.btn_subtitles.clicked.connect(self._open_subtitle_settings)
        self.lbl_sub_active = QLabel(T("lbl_sub_active"))
        self.lbl_sub_active.setStyleSheet(
            "color:#00ff88; font-size:11px; font-weight:bold; padding-left:8px;")
        self.lbl_sub_active.setVisible(False)
        self.btn_go = QPushButton(T("btn_go"))
        self.btn_go.setObjectName("btn_primary")
        self.btn_go.setMinimumHeight(42)
        self.btn_go.setFont(QFont("monospace", 12, QFont.Weight.Bold))
        self.btn_go.clicked.connect(self._start)
        go_row.addWidget(self.btn_subtitles)
        go_row.addWidget(self.lbl_sub_active)
        go_row.addStretch()
        go_row.addWidget(self.btn_go)
        root.addLayout(go_row)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)
        # Intestazione Terminale
        term_lay = QHBoxLayout()
        lbl_term = QLabel(T("lbl_terminal"))
        lbl_term.setStyleSheet("color:#8080ff; font-size:11px; font-weight:bold; background: transparent;")
        term_lay.addWidget(lbl_term)
        term_lay.addStretch()

        self.chk_verbose = QCheckBox(T("chk_verbose"))
        cfg = load_config()
        self.chk_verbose.setChecked(cfg.get("verbose_log", False))
        self.chk_verbose.stateChanged.connect(self._save_verbose)
        term_lay.addWidget(self.chk_verbose)
        root.addLayout(term_lay)
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(160)
        self.terminal.setPlaceholderText(T("terminal_ph"))
        root.addWidget(self.terminal, stretch=2)
        self.btn_stop = QPushButton(T("btn_stop"))
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setVisible(False)
        self.btn_stop.clicked.connect(self._stop)
        root.addWidget(self.btn_stop)
        # ── barra licenza in fondo ────────────────────────────
        lic_bar = QLabel(T("lic_bar"))
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
    def _change_language(self, display_name):
        code = LANGUAGES.get(display_name, "it")
        set_language(code)
        cfg = load_config()
        cfg["language"] = code
        save_config(cfg)
        # Rebuild the UI with the new language
        # We recreate the central widget
        old_central = self.centralWidget()
        self._build_ui()
        if old_central:
            old_central.deleteLater()
        # Re-apply stylesheet
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(cfg.get("theme", "Dark Classic")))

    def _change_theme(self, theme_name):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme_name))
        cfg = load_config()
        cfg["theme"] = theme_name
        cfg["verbose_log"] = getattr(self, 'chk_verbose', QCheckBox()).isChecked()
        cfg["language"] = _LANG
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
                    name = T("dlg_theme_default_name")

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
            name_step = "5"
        else:  # audio o immagine: un pannello in meno
            name_step = "4"
        _sk = "v" if is_video else "a"
        if is_single:
            self.grp_name.setTitle(T(f"grp_name_single_{_sk}"))
            self.lbl_name.setText(T("lbl_name_single"))
            self.txt_name.setPlaceholderText(T("txt_name_ph_single"))
        else:
            self.grp_name.setTitle(T(f"grp_name_folder_{_sk}"))
            self.lbl_name.setText(T("lbl_name_folder"))
            self.txt_name.setPlaceholderText(T("txt_name_ph_folder"))
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
            self.grp_audio.setTitle(T("grp_audio_v"))
            _sk = "v"
        elif is_audio:
            self.grp_audio.setTitle(T("grp_audio_a"))
            _sk = "a"
        else:  # image
            _sk = "a"
        is_single = self.rb_single.isChecked()
        self.grp_name.setTitle(
            T(f"grp_name_single_{_sk}") if is_single
            else T(f"grp_name_folder_{_sk}")
        )
        self._update_cmd_preview()
    def _on_vqual_changed(self):
        btn = self.bg_vqual.checkedButton()
        is_auto = btn and self.bg_vqual.id(btn) == 3
        self.lbl_auto_warn.setVisible(is_auto)
        if hasattr(self, "btn_auto_settings"):
            self.btn_auto_settings.setVisible(is_auto)
        # in AUTO il comando preview non può mostrare valori reali
        if is_auto:
            self.txt_cmd.setText(T("auto_cmd_preview"))
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
        # Blocca i segnali durante il cambio items per evitare crash su Python 3.14
        # (currentTextChanged scatterebbe su items incompleti)
        self.cmb_vcodec.blockSignals(True)
        self.cmb_vcodec.clear()
        self.cmb_vcodec.addItems(codecs)
        self.cmb_vcodec.blockSignals(False)
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
        if not vcodec:
            return ""
        checked = self.bg_vqual.checkedButton()
        if checked and self.bg_vqual.id(checked) == 3:
            return "[AUTO]"
        # Mappa il testo localizzato della qualità back a chiave interna
        _vqual_map = {0: "Alto", 1: "Medio", 2: "Basso", 3: "AUTO"}
        vqual_id = self.bg_vqual.id(checked) if checked else 1
        vqual = _vqual_map.get(vqual_id, "Medio")
        if vcodec in ("DNxHR", "ProRes"):
            return VIDEO_PRESETS.get(vcodec, {}).get(vqual, "")
        return VIDEO_PRESETS.get(gpu, {}).get(vcodec, {}).get(vqual, "")
    def _update_cmd_preview(self):
        if hasattr(self, "btn_manual") and self.btn_manual.isChecked():
            return
        btn = self.bg_vqual.checkedButton() if hasattr(self, "bg_vqual") else None
        if btn and self.bg_vqual.id(btn) == 3 and not (hasattr(self, "rb_image") and self.rb_image.isChecked()):
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
        sample  = self.cmb_sample.currentText()  # display text, mapped to internal in ConvertThread
        audio_p = AUDIO_PRESETS.get(acodec, {}).get(aqual, "")
        if sr_internal_key(sample) != "Mantieni originale":
            audio_p += f" -ar {sr_internal_key(sample).replace(' Hz','')}"
        hw  = "-hwaccel auto " if self.chk_hwaccel.isChecked() else ""
        res = res_internal_key(self.cmb_res.currentText()) if hasattr(self, "cmb_res") else "Mantieni originale"
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
             self.cmb_sample, self.chk_hwaccel, self.cmb_res]
            + list(self.bg_vqual.buttons())
            + list(self.bg_aqual.buttons())
            + list(self.bg_gpu.buttons())
        )
        for w in controls:
            w.setEnabled(not checked)
        if checked:
            self.btn_manual.setText(T("btn_manual_active"))
            self.txt_cmd.setStyleSheet(
                "background:#0d0d1a; color:#ffcc00; border:1px solid #aaaa00;"
                "border-radius:6px; padding:6px 10px;")
        else:
            self.btn_manual.setText(T("btn_manual"))
            self.txt_cmd.setStyleSheet(
                "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
                "border-radius:6px; padding:6px 10px;")
            self._update_cmd_preview()
    def _open_subtitle_settings(self):
        try:
            dlg = SubtitleDialog(self._sub_settings, self)
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                if dlg.disabled:
                    self._sub_settings = {"enabled": False}
                else:
                    self._sub_settings = dlg.get_settings()
                enabled = self._sub_settings.get("enabled", False)
                self.lbl_sub_active.setVisible(enabled)
                # sub compatibili solo con video
                if enabled and hasattr(self, "rb_video") and not self.rb_video.isChecked():
                    self.rb_video.setChecked(True)
                    self._on_type_changed()
        except Exception as e:
            QMessageBox.critical(self, "Errore sottotitoli",
                "Errore apertura dialog sottotitoli:\n" + str(e))

    def _open_auto_settings(self):
        is_folder = self.rb_folder.isChecked()
        dlg = AutoSettingsDialog(is_folder, self._auto_settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._auto_settings = dlg.get_settings()

    # ── AI Upscaling methods ──────────────────────────────────────────────
    def _ai_add_model(self):
        """Apre il file dialog per aggiungere un modello AI."""
        path, _ = QFileDialog.getOpenFileName(
            self, T("dlg_ai_model_title"), "",
            T("dlg_ai_model_filter"))
    def _save_ffmpeg_preset(self):
        """Salva il comando corrente come preset FFmpeg tramite FfmpegPresetSaveDialog."""
        cmd = self.txt_cmd.text().strip()
        if not cmd:
            QMessageBox.warning(self, T("dlg_warn_title"), T("dlg_preset_warn_empty"))
            return
        dlg = FfmpegPresetSaveDialog(cmd, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.txt_name.text().strip()
            command = dlg.txt_cmd.text().strip()
            if name and command:
                save_ffmpeg_preset(name, command)

    def _load_ffmpeg_preset(self):
        dlg = FfmpegPresetLoadDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_cmd:
            # Attiva la modalità manuale e imposta il comando
            if not self.btn_manual.isChecked():
                self.btn_manual.setChecked(True)
                self._toggle_manual(True)
            self.txt_cmd.setText(dlg.selected_cmd)

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
        _vqual_map = {0: "Alto", 1: "Medio", 2: "Basso", 3: "AUTO"}
        _aqual_map = {0: "Alto", 1: "Medio", 2: "Basso"}
        vqual   = _vqual_map.get(self.bg_vqual.id(self.bg_vqual.checkedButton()), "Medio") if self.bg_vqual.checkedButton() else "Medio"
        aqual   = _aqual_map.get(self.bg_aqual.id(self.bg_aqual.checkedButton()), "Medio") if self.bg_aqual.checkedButton() else "Medio"
        gpu     = self._get_selected_gpu()
        sample  = self.cmb_sample.currentText()
        hwaccel = self.chk_hwaccel.isChecked()
        res_key = res_internal_key(self.cmb_res.currentText())
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
            "auto_settings": dict(getattr(self, "_auto_settings", {})),
            "is_folder":    self.rb_folder.isChecked(),
            "sub_settings":   dict(getattr(self, "_sub_settings", {})),
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
        if not path or path == T("lbl_no_file"):
            QMessageBox.warning(self, T("dlg_warn_title"), T("dlg_warn_no_file"))
            return
        params = self._collect_params()
        # se AUTO e cartella: avvisa che il probe richiede tempo
        if params.get("vqual") == "AUTO" and self.rb_folder.isChecked():
            if QMessageBox.question(
                self, T("dlg_auto_folder_title"),
                T("dlg_auto_folder_body"),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            ) != QMessageBox.StandardButton.Ok:
                return
        jobs = self._collect_jobs(params)
        if not jobs:
            QMessageBox.warning(self, T("dlg_no_files_title"), T("dlg_no_files_body"))
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
                lines.append(f"{T('conf_img_conv')} {conv_jobs}")
            if raw_jobs:
                lines.append(f"{T('conf_raw')} {raw_jobs}")
            lines += [
                f"{T('conf_fmt')} .{params['img_fmt'].upper()}",
                f"{T('conf_qual')} {image_quality_label(params['img_quality'])}",
            ]
        else:
            lines.append(f"{T('conf_files')} {len(jobs)}")
            if mode == "video":
                lines += [
                    f"{T('conf_gpu')} {params['gpu']}",
                    f"{T('conf_hw')} {T('conf_hw_yes') if params['hwaccel'] else T('conf_hw_no')}",
                    f"{T('conf_vcodec')} {params['vcodec']} — {params['vqual']}",
                    f"{T('conf_container')} .{params['video_ext']}",
                    f"{T('conf_res')} {res_display_for(params['resolution'])}",
                ]
            lines += [
                f"{T('conf_acodec')} {params['acodec']} — {params['aqual']}",
                f"{T('conf_samplerate')} {params['sample_rate']}",
            ]
        pfx = self.txt_name.text().strip()
        if pfx and not self.rb_single.isChecked():
            lines.append(f"{T('conf_prefix')} {pfx}_")
        if QMessageBox.question(
            self, T("dlg_confirm_title"), "\n".join(lines),
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
        # dopo la conversione, avvia i sottotitoli se abilitati
        sub_cfg = params.get("sub_settings", {})
        if sub_cfg.get("enabled") and params.get("mode") == "video":
            self.thread.all_done.connect(
                lambda ok, err, j=jobs, s=sub_cfg: self._start_subtitle_jobs(j, s)
            )
        self.thread.start()
    def _stop(self):
        if self.thread:
            self.thread.stop()
            self._append_log(T("log_interrupted"))
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
        self._append_log(f"{T('log_completed')} {ok}   {T('log_errors').strip()} {err}")
        self._append_log(f"{'═'*50}")
        QMessageBox.information(
            self, T("dlg_done_title"),
            f"{T('dlg_done_body_ok') if err == 0 else T('dlg_done_body_err')} {ok}"
            + (f"{T('dlg_done_errors')} {err}" if err else "")
        )
    def _start_subtitle_jobs(self, jobs: list, sub_cfg: dict):
        """
        Avvia la generazione sottotitoli in sequenza dopo la conversione.
        Per ogni job video (src, dst, ...) elabora il file DST convertito.
        In modalità SRT-only usa il file sorgente originale.
        """
        out_mode = sub_cfg.get("out_mode", "soft")
        # lista di (src_for_sub, dst_for_sub)
        sub_jobs = []
        for src, dst, _, is_raw in jobs:
            if is_raw:
                continue
            if out_mode == "srt":
                # genera SRT nella stessa cartella del sorgente
                srt_dst = str(Path(src).with_suffix(".srt"))
                sub_jobs.append((src, srt_dst))
            else:
                # usa il video convertito come sorgente; output con suffisso _sub
                stem = Path(dst).stem
                ext  = Path(dst).suffix
                sub_dst = str(Path(dst).parent / f"{stem}_sub{ext}")
                sub_jobs.append((dst, sub_dst))

        if not sub_jobs:
            return

        self._append_log("\n" + "═"*50)
        self._append_log(f"[SUB] Inizio generazione sottotitoli — {len(sub_jobs)} file")

        self._sub_queue   = sub_jobs
        self._sub_cfg     = sub_cfg
        self._sub_idx     = 0
        self._sub_ok      = 0
        self._sub_err     = 0
        self._run_next_subtitle()

    def _run_next_subtitle(self):
        if self._sub_idx >= len(self._sub_queue):
            self._append_log(f"\n[SUB] Completato — \u2713{self._sub_ok}  \u2717{self._sub_err}")
            return
        src, dst = self._sub_queue[self._sub_idx]
        self._sub_thread = SubtitleThread(src, dst, self._sub_cfg)
        self._sub_thread.log_line.connect(self._append_log)
        self._sub_thread.finished.connect(self._on_subtitle_done)
        self._sub_thread.start()

    def _on_subtitle_done(self, success: bool, dst: str):
        if success:
            self._sub_ok += 1
        else:
            self._sub_err += 1
        self._sub_idx += 1
        self._run_next_subtitle()

# ============================================================
#  MAIN
# ============================================================
def main():
    if not os.path.isfile(FFMPEG_BIN) and not shutil.which(FFMPEG_BIN):
        app2 = QApplication(sys.argv)   # serve per mostrare il dialogo
        load_config()  # init language
        QMessageBox.critical(None, T("ffmpeg_not_found_title"), T("ffmpeg_not_found_body"))
        sys.exit(1)
    app = QApplication(sys.argv)
    cfg = load_config()  # also calls set_language() from saved config
    app.setStyleSheet(get_stylesheet(cfg.get("theme", "Dark Classic")))
    app.setApplicationName("DISAGIO PRODUCTION CONVERTER")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
