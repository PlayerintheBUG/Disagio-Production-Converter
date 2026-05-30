#!/usr/bin/env python3
"""
Disagio — styles.py
Temi grafici (dizionari colori) e generazione QSS stylesheet.
"""

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

