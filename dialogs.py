#!/usr/bin/env python3
"""
Disagio — dialogs.py
Dialog UI: ThemeEditor, License, AutoSettings, FFmpegPreset.
"""

import json
import os

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit, QFileDialog,
    QCheckBox, QGroupBox, QScrollArea, QWidget, QColorDialog,
    QGridLayout, QFormLayout, QListWidget, QSizePolicy, QMessageBox,
    QRadioButton, QButtonGroup, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from translations import T
from config import CONFIG_FILE, LICENSE_TEXT
from styles import get_stylesheet, THEMES, DEFAULT_THEMES
from presets import load_ffmpeg_presets, save_ffmpeg_preset, delete_ffmpeg_preset

class ThemeEditorDialog(QDialog):
    def __init__(self, current_theme_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("dlg_theme_title"))
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
        name_lay.addWidget(QLabel(T("dlg_theme_name_lbl")))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText(T("dlg_theme_name_ph"))
        if current_theme_name not in DEFAULT_THEMES:
            self.txt_name.setText(current_theme_name)
        name_lay.addWidget(self.txt_name)
        lay.addLayout(name_lay)

        lbl_info = QLabel(T("dlg_theme_info"))
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
        btn_save = QPushButton(T("dlg_theme_save"))
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton(T("dlg_theme_cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_delete = QPushButton(T("dlg_theme_delete"))
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
        color = QColorDialog.getColor(QColor(self.colors[key]), self, T("dlg_color_pick"))
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
        self.setWindowTitle(T("dlg_lic_title"))
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
#  GESTIONE PRESET FFMPEG
# ============================================================

class AutoSettingsDialog(QDialog):
    """
    Dialog per configurare la modalità AUTO avanzata:
    - analisi BPP reale via ffprobe packet-level
    - cap dimensione assoluto (MB/GB) per file singolo
    - cap percentuale (riduzione % sul peso originale) per file singolo e cartella
    """
    def __init__(self, is_folder: bool, current: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("dlg_auto_title"))
        self.resize(520, 420)
        self.is_folder = is_folder
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        # ── Sezione analisi qualità ────────────────────────────
        grp_analysis = QGroupBox(T("grp_auto_analysis"))
        aly = QVBoxLayout(grp_analysis)
        self.chk_bpp_probe = QCheckBox(T("chk_auto_bpp_probe"))
        self.chk_bpp_probe.setChecked(current.get("use_bpp_probe", False))
        aly.addWidget(self.chk_bpp_probe)
        lbl_bpp_info = QLabel(T("lbl_auto_bpp_probe_info"))
        lbl_bpp_info.setStyleSheet("color:#888899; font-size:11px; font-style:italic; padding-left:22px;")
        lbl_bpp_info.setWordWrap(True)
        aly.addWidget(lbl_bpp_info)
        lay.addWidget(grp_analysis)

        # ── Sezione cap dimensione ─────────────────────────────
        grp_cap = QGroupBox(T("grp_auto_cap"))
        cly = QVBoxLayout(grp_cap)

        self.bg_cap = QButtonGroup(self)
        self.rb_cap_none = QRadioButton(T("rb_cap_none"))
        self.rb_cap_mb   = QRadioButton(T("rb_cap_mb"))
        self.rb_cap_pct  = QRadioButton(T("rb_cap_pct"))

        # cartella: solo % disponibile
        if is_folder:
            self.rb_cap_mb.setEnabled(False)

        self.bg_cap.addButton(self.rb_cap_none, 0)
        self.bg_cap.addButton(self.rb_cap_mb,   1)
        self.bg_cap.addButton(self.rb_cap_pct,  2)

        cap_mode = current.get("cap_mode", "none")
        if cap_mode == "size_mb" and not is_folder:
            self.rb_cap_mb.setChecked(True)
        elif cap_mode == "size_pct":
            self.rb_cap_pct.setChecked(True)
        else:
            self.rb_cap_none.setChecked(True)

        cly.addWidget(self.rb_cap_none)
        cly.addWidget(self.rb_cap_mb)
        cly.addWidget(self.rb_cap_pct)

        # ── riga valore MB ──
        self.row_mb = QWidget()
        mb_lay = QHBoxLayout(self.row_mb)
        mb_lay.setContentsMargins(22, 0, 0, 0)
        mb_lay.addWidget(QLabel(T("lbl_cap_mb_value")))
        self.spin_mb = QLineEdit()
        self.spin_mb.setPlaceholderText("Es: 500 MB, 1.5 GB")
        self.spin_mb.setFixedWidth(120)
        cap_val = current.get("cap_value", 500)
        cap_unit = current.get("cap_unit", "MB")
        self.spin_mb.setText(str(cap_val))
        self.cmb_mb_unit = QComboBox()
        self.cmb_mb_unit.addItems(["MB", "GB"])
        self.cmb_mb_unit.setCurrentText(cap_unit)
        self.cmb_mb_unit.setFixedWidth(60)
        mb_lay.addWidget(self.spin_mb)
        mb_lay.addWidget(self.cmb_mb_unit)
        mb_lay.addStretch()
        cly.addWidget(self.row_mb)

        # ── riga valore % ──
        self.row_pct = QWidget()
        pct_lay = QHBoxLayout(self.row_pct)
        pct_lay.setContentsMargins(22, 0, 0, 0)
        pct_lay.addWidget(QLabel(T("lbl_cap_pct_value")))
        self.spin_pct = QLineEdit()
        self.spin_pct.setPlaceholderText("1 – 99")
        self.spin_pct.setFixedWidth(80)
        pct_default = current.get("cap_value", 50) if cap_mode == "size_pct" else 50
        self.spin_pct.setText(str(pct_default))
        lbl_pct_sym = QLabel("%")
        pct_lay.addWidget(self.spin_pct)
        pct_lay.addWidget(lbl_pct_sym)
        pct_lay.addStretch()
        cly.addWidget(self.row_pct)

        # ── warning VBR ──
        self.lbl_cap_warn = QLabel(T("lbl_cap_warn"))
        self.lbl_cap_warn.setWordWrap(True)
        self.lbl_cap_warn.setStyleSheet("color:#cc8800; font-size:11px; font-style:italic; padding:4px 0;")
        cly.addWidget(self.lbl_cap_warn)

        lay.addWidget(grp_cap)

        # ── bottoni ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_ok = QPushButton(T("btn_auto_ok"))
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(T("btn_auto_cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

        # collegamento segnali
        self.bg_cap.buttonClicked.connect(self._update_rows)
        self._update_rows()

    def _update_rows(self):
        mode = self.bg_cap.checkedId()
        self.row_mb.setVisible(mode == 1)
        self.row_pct.setVisible(mode == 2)
        self.lbl_cap_warn.setVisible(mode in (1, 2))

    def get_settings(self) -> dict:
        """Ritorna il dizionario con le impostazioni scelte."""
        mode_id = self.bg_cap.checkedId()
        if mode_id == 1:
            cap_mode = "size_mb"
            try:
                raw = float(self.spin_mb.text().replace(",", "."))
            except ValueError:
                raw = 500.0
            unit = self.cmb_mb_unit.currentText()
            cap_value = raw * 1024 if unit == "GB" else raw  # tutto in MB
            cap_unit  = unit
        elif mode_id == 2:
            cap_mode = "size_pct"
            try:
                cap_value = max(1.0, min(99.0, float(self.spin_pct.text().replace(",", "."))))
            except ValueError:
                cap_value = 50.0
            cap_unit = "%"
        else:
            cap_mode  = "none"
            cap_value = 0.0
            cap_unit  = ""
        return {
            "use_bpp_probe": self.chk_bpp_probe.isChecked(),
            "cap_mode":      cap_mode,
            "cap_value":     cap_value,
            "cap_unit":      cap_unit,
        }


class FfmpegPresetSaveDialog(QDialog):
    """Dialogo per salvare il comando corrente come preset."""
    def __init__(self, current_cmd: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("dlg_preset_save_title"))
        self.resize(480, 200)
        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(T("dlg_preset_save_label")))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText(T("dlg_preset_save_placeholder"))
        lay.addWidget(self.txt_name)

        lay.addWidget(QLabel(T("dlg_preset_cmd_label")))
        self.txt_cmd = QLineEdit()
        self.txt_cmd.setText(current_cmd)
        self.txt_cmd.setFont(QFont("monospace", 10))
        self.txt_cmd.setStyleSheet(
            "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
            "border-radius:6px; padding:6px 10px;")
        lay.addWidget(self.txt_cmd)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._on_save)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _on_save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, T("dlg_warn_title"), T("dlg_preset_warn_empty"))
            return
        self.accept()


class FfmpegPresetLoadDialog(QDialog):
    """Dialogo per sfogliare, caricare, esportare e importare preset."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("dlg_preset_load_title"))
        self.resize(620, 440)
        self.selected_cmd = None

        lay = QVBoxLayout(self)

        self.presets = load_ffmpeg_presets()

        if not self.presets:
            lay.addWidget(QLabel(T("dlg_preset_no_presets")))
            btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            btns.rejected.connect(self.reject)
            btn_row = QHBoxLayout()
            btn_import = QPushButton(T("btn_preset_import"))
            btn_import.clicked.connect(self._import_presets)
            btn_row.addWidget(btn_import)
            btn_row.addStretch()
            lay.addLayout(btn_row)
            lay.addWidget(btns)
            return

        from PyQt6.QtWidgets import QListWidget
        self.list_widget = QListWidget()
        for name in self.presets:
            self.list_widget.addItem(name)
        self.list_widget.setCurrentRow(0)
        self.list_widget.currentTextChanged.connect(self._on_selection_changed)
        lay.addWidget(self.list_widget)

        lay.addWidget(QLabel(T("dlg_preset_cmd_label")))
        self.lbl_cmd = QLineEdit()
        self.lbl_cmd.setReadOnly(True)
        self.lbl_cmd.setFont(QFont("monospace", 10))
        self.lbl_cmd.setStyleSheet(
            "background:#0d0d1a; color:#00ff88; border:1px solid #2d2d4e;"
            "border-radius:6px; padding:6px 10px;")
        lay.addWidget(self.lbl_cmd)

        btn_row = QHBoxLayout()
        btn_use = QPushButton(T("dlg_preset_use"))
        btn_use.setObjectName("btn_primary")
        btn_use.clicked.connect(self._use_preset)
        btn_delete = QPushButton(T("dlg_preset_delete"))
        btn_delete.setObjectName("btn_danger")
        btn_delete.clicked.connect(self._delete_preset)
        btn_export = QPushButton(T("btn_preset_export"))
        btn_export.clicked.connect(self._export_presets)
        btn_import = QPushButton(T("btn_preset_import"))
        btn_import.clicked.connect(self._import_presets)
        btn_close = QPushButton(T("dlg_theme_cancel"))
        btn_close.clicked.connect(self.reject)
        btn_row.addWidget(btn_use)
        btn_row.addWidget(btn_delete)
        btn_row.addStretch()
        btn_row.addWidget(btn_export)
        btn_row.addWidget(btn_import)
        btn_row.addWidget(btn_close)
        lay.addLayout(btn_row)

        if self.presets:
            first = next(iter(self.presets))
            self.lbl_cmd.setText(self.presets[first])

    def _on_selection_changed(self, name):
        cmd = self.presets.get(name, "")
        self.lbl_cmd.setText(cmd)

    def _use_preset(self):
        item = self.list_widget.currentItem()
        if item:
            self.selected_cmd = self.presets.get(item.text(), "")
            self.accept()

    def _delete_preset(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        name = item.text()
        delete_ffmpeg_preset(name)
        del self.presets[name]
        row = self.list_widget.currentRow()
        self.list_widget.takeItem(row)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(max(0, row - 1))
            new_item = self.list_widget.currentItem()
            if new_item:
                self.lbl_cmd.setText(self.presets.get(new_item.text(), ""))
        else:
            self.lbl_cmd.setText("")

    def _export_presets(self):
        path, _ = QFileDialog.getSaveFileName(
            self, T("dlg_preset_export_title"), "ffmpeg_presets.json",
            "JSON (*.json);;Tutti i file (*)")
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(self.presets, f, indent=2)
            except Exception as e:
                QMessageBox.warning(self, T("dlg_warn_title"), str(e))

    def _import_presets(self):
        path, _ = QFileDialog.getOpenFileName(
            self, T("dlg_preset_import_title"), "",
            "JSON (*.json);;Tutti i file (*)")
        if not path:
            return
        try:
            with open(path, "r") as f:
                imported = json.load(f)
            if not isinstance(imported, dict):
                raise ValueError("not a dict")
            for name, cmd in imported.items():
                save_ffmpeg_preset(str(name), str(cmd))
            QMessageBox.information(
                self, T("dlg_preset_save_title"), T("dlg_preset_import_ok"))
            self.reject()
        except Exception:
            QMessageBox.warning(self, T("dlg_warn_title"), T("dlg_preset_import_err"))

# ============================================================
#  THREAD SOTTOTITOLI
# ============================================================
