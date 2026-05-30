#!/usr/bin/env python3
"""
Disagio — translations.py
Sistema i18n: dizionario TRANSLATIONS, funzione T(), set_language().
"""

LANGUAGES = {
    "Italiano 🇮🇹":  "it",
    "English 🇬🇧":   "en",
    "Deutsch 🇩🇪":   "de",
    "Español 🇪🇸":   "es",
    "Doge 🐕":        "doge",
}

TRANSLATIONS = {
    # ── App title ──────────────────────────────────────────
    "app_title": {
        "it":   "DISAGIO PRODUCTION CONVERTER",
        "en":   "DISAGIO PRODUCTION CONVERTER",
        "de":   "DISAGIO PRODUCTION CONVERTER",
        "es":   "DISAGIO PRODUCTION CONVERTER",
        "doge": "DISAGIO PRODUCTION CONVERTER wow",
    },
    # ── Toolbar ────────────────────────────────────────────
    "lbl_theme": {
        "it": "Tema:", "en": "Theme:", "de": "Design:", "es": "Tema:",
        "doge": "such color:",
    },
    "btn_edit_theme": {
        "it": " Modifica Tema ", "en": " Edit Theme ", "de": " Design bearbeiten ",
        "es": " Editar Tema ", "doge": " wow theme edit ",
    },
    "btn_edit_theme_tip": {
        "it": "Modifica o crea un tema personalizzato",
        "en": "Edit or create a custom theme",
        "de": "Design bearbeiten oder erstellen",
        "es": "Editar o crear un tema personalizado",
        "doge": "much customize wow",
    },
    "btn_license": {
        "it": "⚖  GPL v3", "en": "⚖  GPL v3", "de": "⚖  GPL v3",
        "es": "⚖  GPL v3", "doge": "⚖  law paper",
    },
    "btn_license_tip": {
        "it": "Visualizza la licenza GNU GPL v3",
        "en": "View the GNU GPL v3 license",
        "de": "GNU GPL v3 Lizenz anzeigen",
        "es": "Ver la licencia GNU GPL v3",
        "doge": "such legal, very free",
    },


    # ── Step 1 ─────────────────────────────────────────────
    "step1_title": {
        "it": "STEP 1 — Sorgente",
        "en": "STEP 1 — Source",
        "de": "SCHRITT 1 — Quelle",
        "es": "PASO 1 — Fuente",
        "doge": "STEP 1 — such file",
    },
    "rb_single": {
        "it": "File singolo", "en": "Single file", "de": "Einzelne Datei",
        "es": "Archivo único", "doge": "one file, wow",
    },
    "rb_folder": {
        "it": "Cartella intera", "en": "Entire folder", "de": "Ganzer Ordner",
        "es": "Carpeta entera", "doge": "many file, very folder",
    },
    "lbl_no_file": {
        "it": "Nessun file selezionato",
        "en": "No file selected",
        "de": "Keine Datei ausgewählt",
        "es": "Ningún archivo seleccionado",
        "doge": "no file. such empty. wow",
    },
    "btn_browse": {
        "it": "Sfoglia…", "en": "Browse…", "de": "Durchsuchen…",
        "es": "Examinar…", "doge": "pls find…",
    },
    # ── Step 2 ─────────────────────────────────────────────
    "step2_title": {
        "it": "STEP 2 — Tipo output",
        "en": "STEP 2 — Output type",
        "de": "SCHRITT 2 — Ausgabetyp",
        "es": "PASO 2 — Tipo de salida",
        "doge": "STEP 2 — what output? wow",
    },
    "rb_video": {
        "it": "Video + Audio", "en": "Video + Audio", "de": "Video + Audio",
        "es": "Video + Audio", "doge": "Video + sound wow",
    },
    "rb_audio": {
        "it": "Solo Audio", "en": "Audio only", "de": "Nur Audio",
        "es": "Solo Audio", "doge": "only sound, very audio",
    },
    "rb_image": {
        "it": "Immagini", "en": "Images", "de": "Bilder",
        "es": "Imágenes", "doge": "much picture, wow",
    },
    # ── Step 3 video ───────────────────────────────────────
    "grp_video": {
        "it": "STEP 3 — Video", "en": "STEP 3 — Video",
        "de": "SCHRITT 3 — Video", "es": "PASO 3 — Video",
        "doge": "STEP 3 — such video",
    },
    "lbl_gpu": {
        "it": "Encoder GPU:", "en": "GPU Encoder:", "de": "GPU-Encoder:",
        "es": "Codificador GPU:", "doge": "fast chip:",
    },
    "chk_hwaccel": {
        "it": "Accelerazione hardware decodifica  (-hwaccel auto)",
        "en": "Hardware decode acceleration  (-hwaccel auto)",
        "de": "Hardware-Dekodierungsbeschleunigung  (-hwaccel auto)",
        "es": "Aceleración de decodificación por hardware  (-hwaccel auto)",
        "doge": "vroom hardware go fast (-hwaccel auto)",
    },
    "lbl_container": {
        "it": "Container:", "en": "Container:", "de": "Container:",
        "es": "Contenedor:", "doge": "box:",
    },
    "lbl_vcodec": {
        "it": "Codec video:", "en": "Video codec:", "de": "Video-Codec:",
        "es": "Codec de video:", "doge": "such encode:",
    },
    "lbl_vqual": {
        "it": "Qualità video:", "en": "Video quality:", "de": "Videoqualität:",
        "es": "Calidad de video:", "doge": "how good video?:",
    },
    "qual_high": {
        "it": "Alto", "en": "High", "de": "Hoch", "es": "Alto", "doge": "very wow",
    },
    "qual_mid": {
        "it": "Medio", "en": "Medium", "de": "Mittel", "es": "Medio", "doge": "much ok",
    },
    "qual_low": {
        "it": "Basso", "en": "Low", "de": "Niedrig", "es": "Bajo", "doge": "smol",
    },
    "qual_auto": {
        "it": "AUTO", "en": "AUTO", "de": "AUTO", "es": "AUTO", "doge": "DOGE",
    },
    "lbl_auto_warn": {
        "it": "⚠ Il sistema AUTO è una stima — può commettere errori su sorgenti atipici",
        "en": "⚠ AUTO mode is an estimate — may have errors on atypical sources",
        "de": "⚠ AUTO ist eine Schätzung — bei atypischen Quellen können Fehler auftreten",
        "es": "⚠ El modo AUTO es una estimación — puede tener errores en fuentes atípicas",
        "doge": "⚠ AUTO is guess. much estimate. maybe wrong. wow",
    },
    "lbl_resolution": {
        "it": "Risoluzione output:", "en": "Output resolution:", "de": "Ausgabeauflösung:",
        "es": "Resolución de salida:", "doge": "how many pixel?:",
    },
    "lbl_res_note": {
        "it": "<small style='color:#666688'>  Aspect ratio originale preservato  |  filtro: lanczos</small>",
        "en": "<small style='color:#666688'>  Original aspect ratio preserved  |  filter: lanczos</small>",
        "de": "<small style='color:#666688'>  Originales Seitenverhältnis beibehalten  |  Filter: lanczos</small>",
        "es": "<small style='color:#666688'>  Relación de aspecto original preservada  |  filtro: lanczos</small>",
        "doge": "<small style='color:#666688'>  keep shape wow  |  such lanczos filter</small>",
    },
    # ── Step 3 images ──────────────────────────────────────
    "grp_image": {
        "it": "STEP 3 — Immagini", "en": "STEP 3 — Images",
        "de": "SCHRITT 3 — Bilder", "es": "PASO 3 — Imágenes",
        "doge": "STEP 3 — much picture",
    },
    "lbl_imgfmt": {
        "it": "Formato di output:", "en": "Output format:", "de": "Ausgabeformat:",
        "es": "Formato de salida:", "doge": "what picture box?:",
    },
    "lbl_imgqual_header": {
        "it": "Qualità / Compressione:", "en": "Quality / Compression:",
        "de": "Qualität / Komprimierung:", "es": "Calidad / Compresión:",
        "doge": "how squish?:",
    },
    "lbl_img_low": {
        "it": "Bassa qualità\n(File piccolo)", "en": "Low quality\n(Small file)",
        "de": "Niedrige Qualität\n(Kleine Datei)", "es": "Baja calidad\n(Archivo pequeño)",
        "doge": "smol quality\n(tiny file)",
    },
    "lbl_img_high": {
        "it": "Alta qualità\n(File grande)", "en": "High quality\n(Large file)",
        "de": "Hohe Qualität\n(Große Datei)", "es": "Alta calidad\n(Archivo grande)",
        "doge": "wow quality\n(big file)",
    },
    "lbl_bmp_warn": {
        "it": "ℹ  Il formato BMP non supporta la compressione — lo slider non ha effetto.",
        "en": "ℹ  BMP format does not support compression — the slider has no effect.",
        "de": "ℹ  Das BMP-Format unterstützt keine Komprimierung — der Schieberegler hat keine Wirkung.",
        "es": "ℹ  El formato BMP no admite compresión — el control deslizante no tiene efecto.",
        "doge": "ℹ  BMP no squish. slider do nothing. wow.",
    },
    "lbl_raw_note": {
        "it": "📁  I file RAW trovati nella cartella verranno copiati intatti in una sottocartella separata  \"FOTO_RAW\"  accanto ai file convertiti.",
        "en": "📁  RAW files found in the folder will be copied intact to a separate subfolder  \"FOTO_RAW\"  next to the converted files.",
        "de": "📁  RAW-Dateien im Ordner werden unverändert in einen separaten Unterordner  \"FOTO_RAW\"  neben den konvertierten Dateien kopiert.",
        "es": "📁  Los archivos RAW encontrados en la carpeta se copiarán intactos en una subcarpeta separada  \"FOTO_RAW\"  junto a los archivos convertidos.",
        "doge": "📁  RAW file found. very copy. much intact. go to FOTO_RAW folder wow.",
    },
    # ── Step 4 audio ───────────────────────────────────────
    "grp_audio_v": {
        "it": "STEP 4 — Audio", "en": "STEP 4 — Audio",
        "de": "SCHRITT 4 — Audio", "es": "PASO 4 — Audio",
        "doge": "STEP 4 — such sound",
    },
    "grp_audio_a": {
        "it": "STEP 3 — Audio", "en": "STEP 3 — Audio",
        "de": "SCHRITT 3 — Audio", "es": "PASO 3 — Audio",
        "doge": "STEP 3 — such sound",
    },
    "lbl_acodec": {
        "it": "Codec audio:", "en": "Audio codec:", "de": "Audio-Codec:",
        "es": "Codec de audio:", "doge": "sound encode:",
    },
    "lbl_aqual": {
        "it": "Qualità audio:", "en": "Audio quality:", "de": "Audioqualität:",
        "es": "Calidad de audio:", "doge": "how good sound?:",
    },
    "lbl_samplerate": {
        "it": "Sample rate:", "en": "Sample rate:", "de": "Abtastrate:",
        "es": "Frecuencia de muestreo:", "doge": "many sample per sec:",
    },
    # ── Step 5 name ────────────────────────────────────────
    "grp_name_single_v": {
        "it": "STEP 5 — Nome file output", "en": "STEP 5 — Output file name",
        "de": "SCHRITT 5 — Ausgabedateiname", "es": "PASO 5 — Nombre del archivo de salida",
        "doge": "STEP 5 — name the file wow",
    },
    "grp_name_folder_v": {
        "it": "STEP 5 — Prefisso file output", "en": "STEP 5 — Output file prefix",
        "de": "SCHRITT 5 — Ausgabedatei-Präfix", "es": "PASO 5 — Prefijo del archivo de salida",
        "doge": "STEP 5 — prefix wow",
    },
    "grp_name_single_a": {
        "it": "STEP 4 — Nome file output", "en": "STEP 4 — Output file name",
        "de": "SCHRITT 4 — Ausgabedateiname", "es": "PASO 4 — Nombre del archivo de salida",
        "doge": "STEP 4 — name the file wow",
    },
    "grp_name_folder_a": {
        "it": "STEP 4 — Prefisso file output", "en": "STEP 4 — Output file prefix",
        "de": "SCHRITT 4 — Ausgabedatei-Präfix", "es": "PASO 4 — Prefijo del archivo de salida",
        "doge": "STEP 4 — prefix wow",
    },
    "lbl_name_single": {
        "it": "Nome (senza estensione):", "en": "Name (without extension):",
        "de": "Name (ohne Erweiterung):", "es": "Nombre (sin extensión):",
        "doge": "what name? (no .ext):",
    },
    "lbl_name_folder": {
        "it": "Prefisso:", "en": "Prefix:", "de": "Präfix:", "es": "Prefijo:",
        "doge": "such prefix:",
    },
    "txt_name_ph_single": {
        "it": "Lascia vuoto per mantenere il nome originale",
        "en": "Leave empty to keep the original name",
        "de": "Leer lassen, um den Originalnamen beizubehalten",
        "es": "Dejar vacío para mantener el nombre original",
        "doge": "leave empty, keep original name wow",
    },
    "txt_name_ph_folder": {
        "it": "Lascia vuoto per nessun prefisso",
        "en": "Leave empty for no prefix",
        "de": "Leer lassen für kein Präfix",
        "es": "Dejar vacío para sin prefijo",
        "doge": "empty = no prefix. much nothing.",
    },
    # ── FFmpeg command box ─────────────────────────────────
    "grp_cmd": {
        "it": "Comando ffmpeg (aggiornato live)", "en": "FFmpeg command (live preview)",
        "de": "FFmpeg-Befehl (Live-Vorschau)", "es": "Comando ffmpeg (vista previa en vivo)",
        "doge": "such command, very live wow",
    },
    "btn_manual": {
        "it": "✏  Abilita modifica manuale", "en": "✏  Enable manual edit",
        "de": "✏  Manuelle Bearbeitung aktivieren", "es": "✏  Habilitar edición manual",
        "doge": "✏  type it myself wow",
    },
    "btn_manual_active": {
        "it": "🔒  Torna a modalità automatica", "en": "🔒  Back to automatic mode",
        "de": "🔒  Zurück zum automatischen Modus", "es": "🔒  Volver al modo automático",
        "doge": "🔒  no touch. auto now. wow",
    },
    # ── Dialog Sottotitoli ────────────────────────────────────
    "btn_subtitles": {
        "it": "🎙  Sottotitoli…", "en": "🎙  Subtitles…",
        "de": "🎙  Untertitel…", "es": "🎙  Subtítulos…",
        "doge": "🎙  sub wow",
    },
    "dlg_sub_title": {
        "it": "Generazione sottotitoli automatica",
        "en": "Automatic subtitle generation",
        "de": "Automatische Untertitel-Generierung",
        "es": "Generación automática de subtítulos",
        "doge": "auto sub wow",
    },
    "grp_sub_engine": {
        "it": "Motore di riconoscimento vocale",
        "en": "Speech recognition engine",
        "de": "Spracherkennungs-Engine",
        "es": "Motor de reconocimiento de voz",
        "doge": "voice brain engine",
    },
    "lbl_sub_model": {
        "it": "Modello Whisper:", "en": "Whisper model:",
        "de": "Whisper-Modell:", "es": "Modelo Whisper:",
        "doge": "which whisper?:",
    },
    "lbl_sub_device": {
        "it": "Esegui su:", "en": "Run on:",
        "de": "Ausführen auf:", "es": "Ejecutar en:",
        "doge": "run where?:",
    },
    "lbl_sub_lang": {
        "it": "Lingua audio:", "en": "Audio language:",
        "de": "Audiosprache:", "es": "Idioma del audio:",
        "doge": "what language?:",
    },
    "grp_sub_output": {
        "it": "Modalità output", "en": "Output mode",
        "de": "Ausgabemodus", "es": "Modo de salida",
        "doge": "output mode wow",
    },
    "rb_sub_soft": {
        "it": "Morbidi — traccia separata nel container (attivabili/disattivabili dal player)",
        "en": "Soft — separate track in container (can be toggled in player)",
        "de": "Weich — separate Spur im Container (im Player ein/ausschaltbar)",
        "es": "Suaves — pista separada en el container (activables en el reproductor)",
        "doge": "soft sub. player toggle. wow.",
    },
    "rb_sub_hard": {
        "it": "Hard — bruciati nel video (sempre visibili, non disattivabili)",
        "en": "Hard — burned into video (always visible, cannot be disabled)",
        "de": "Hard — ins Video gebrannt (immer sichtbar, nicht deaktivierbar)",
        "es": "Hard — grabados en el video (siempre visibles, no desactivables)",
        "doge": "hard burn. no turn off. always there. wow.",
    },
    "rb_sub_srt_only": {
        "it": "Solo SRT — genera solo il file sottotitoli, non tocca il video",
        "en": "SRT only — generates only the subtitle file, does not modify the video",
        "de": "Nur SRT — erzeugt nur die Untertiteldatei, Video bleibt unverändert",
        "es": "Solo SRT — genera solo el archivo de subtítulos, no modifica el video",
        "doge": "just srt file. video untouched. wow.",
    },
    "lbl_sub_hard_warn": {
        "it": "⚠  I sottotitoli hard sono bruciati nei frame del video e richiedono una ricodifica completa.\nNon potranno essere rimossi o disattivati in alcun modo.",
        "en": "⚠  Hard subtitles are burned into the video frames and require full re-encoding.\nThey cannot be removed or disabled in any way.",
        "de": "⚠  Harte Untertitel werden in die Videoframes gebrannt und erfordern eine vollständige Neukodierung.\nSie können auf keine Weise entfernt oder deaktiviert werden.",
        "es": "⚠  Los subtítulos hard se graban en los fotogramas y requieren recodificación completa.\nNo se pueden eliminar ni desactivar de ninguna manera.",
        "doge": "⚠  burned forever. no remove. much permanent. wow.",
    },
    "grp_sub_style": {
        "it": "Stile testo (solo Hard)", "en": "Text style (Hard only)",
        "de": "Textstil (nur Hard)", "es": "Estilo de texto (solo Hard)",
        "doge": "style only hard wow",
    },
    "lbl_sub_fontsize": {
        "it": "Dimensione font:", "en": "Font size:",
        "de": "Schriftgröße:", "es": "Tamaño de fuente:",
        "doge": "how big text?:",
    },
    "lbl_sub_color": {
        "it": "Colore testo:", "en": "Text color:",
        "de": "Textfarbe:", "es": "Color de texto:",
        "doge": "what color?:",
    },
    "lbl_sub_position": {
        "it": "Posizione:", "en": "Position:",
        "de": "Position:", "es": "Posición:",
        "doge": "where subs?:",
    },
    "sub_not_installed_title": {
        "it": "faster-whisper non trovato",
        "en": "faster-whisper not found",
        "de": "faster-whisper nicht gefunden",
        "es": "faster-whisper no encontrado",
        "doge": "whisper missing wow",
    },
    "sub_not_installed_body": {
        "it": "La libreria faster-whisper non è installata.\n\nPer installarla esegui nel terminale:\n\n    pip install faster-whisper\n\nSe hai una GPU NVIDIA assicurati di avere CUDA 12 installato per la modalità GPU.",
        "en": "The faster-whisper library is not installed.\n\nTo install it, run in the terminal:\n\n    pip install faster-whisper\n\nIf you have an NVIDIA GPU, make sure CUDA 12 is installed for GPU mode.",
        "de": "Die faster-whisper-Bibliothek ist nicht installiert.\n\nZur Installation im Terminal ausführen:\n\n    pip install faster-whisper\n\nBei einer NVIDIA GPU sicherstellen, dass CUDA 12 für den GPU-Modus installiert ist.",
        "es": "La librería faster-whisper no está instalada.\n\nPara instalarla ejecuta en la terminal:\n\n    pip install faster-whisper\n\nSi tienes una GPU NVIDIA asegúrate de tener CUDA 12 instalado para el modo GPU.",
        "doge": "no faster-whisper. pip install it. much easy. wow.",
    },
    "btn_sub_confirm": {
        "it": "✔  Attiva sottotitoli", "en": "✔  Enable subtitles",
        "de": "✔  Untertitel aktivieren", "es": "✔  Activar subtítulos",
        "doge": "✔  subs on wow",
    },
    "btn_sub_disable": {
        "it": "✖  Disattiva sottotitoli", "en": "✖  Disable subtitles",
        "de": "✖  Untertitel deaktivieren", "es": "✖  Desactivar subtítulos",
        "doge": "✖  subs off wow",
    },
    "btn_sub_cancel": {
        "it": "Annulla", "en": "Cancel", "de": "Abbrechen", "es": "Cancelar",
        "doge": "nope",
    },
    "lbl_sub_active": {
        "it": "🎙 sottotitoli attivi", "en": "🎙 subtitles active",
        "de": "🎙 Untertitel aktiv", "es": "🎙 subtítulos activos",
        "doge": "🎙 subs on wow",
    },
    # ── Dialog AUTO avanzato ──────────────────────────────────
    "dlg_auto_title": {
        "it": "Impostazioni modalità AUTO",
        "en": "AUTO mode settings",
        "de": "AUTO-Modus Einstellungen",
        "es": "Configuración modo AUTO",
        "doge": "AUTO settings wow",
    },
    "grp_auto_analysis": {
        "it": "Analisi qualità",
        "en": "Quality analysis",
        "de": "Qualitätsanalyse",
        "es": "Análisis de calidad",
        "doge": "how good? analysis",
    },
    "chk_auto_bpp_probe": {
        "it": "Analisi BPP reale (legge i frame effettivi con ffprobe)",
        "en": "Real BPP analysis (reads actual frames with ffprobe)",
        "de": "Echte BPP-Analyse (liest tatsächliche Frames mit ffprobe)",
        "es": "Análisis BPP real (lee frames reales con ffprobe)",
        "doge": "real frame scan wow",
    },
    "lbl_auto_bpp_probe_info": {
        "it": "ℹ  Più preciso del bitrate dichiarato nel container.\nSu file grandi o cartelle può richiedere qualche minuto in più.",
        "en": "ℹ  More accurate than the bitrate declared in the container.\nOn large files or folders it may take a few extra minutes.",
        "de": "ℹ  Genauer als die im Container angegebene Bitrate.\nBei großen Dateien oder Ordnern kann es einige Minuten länger dauern.",
        "es": "ℹ  Más preciso que el bitrate declarado en el container.\nEn archivos grandes o carpetas puede tardar algunos minutos más.",
        "doge": "ℹ  more precise. much slow on big folder. wow.",
    },
    "grp_auto_cap": {
        "it": "Cap dimensione output",
        "en": "Output size cap",
        "de": "Ausgabegröße begrenzen",
        "es": "Límite de tamaño de salida",
        "doge": "size limit wow",
    },
    "rb_cap_none": {
        "it": "Nessun cap (qualità ottimale)",
        "en": "No cap (optimal quality)",
        "de": "Kein Limit (optimale Qualität)",
        "es": "Sin límite (calidad óptima)",
        "doge": "no cap. such quality. wow",
    },
    "rb_cap_mb": {
        "it": "Dimensione massima assoluta (solo file singolo)",
        "en": "Maximum absolute size (single file only)",
        "de": "Maximale absolute Größe (nur Einzeldatei)",
        "es": "Tamaño máximo absoluto (solo archivo único)",
        "doge": "max size MB. single file wow",
    },
    "rb_cap_pct": {
        "it": "Riduci del % rispetto all'originale (file singolo e cartella)",
        "en": "Reduce by % compared to original (single file and folder)",
        "de": "Um % gegenüber dem Original reduzieren (Einzel- und Ordner)",
        "es": "Reducir en % respecto al original (archivo único y carpeta)",
        "doge": "shrink by %. much smaller. wow",
    },
    "lbl_cap_mb_value": {
        "it": "Dimensione massima:", "en": "Maximum size:",
        "de": "Maximale Größe:", "es": "Tamaño máximo:",
        "doge": "max how big?:",
    },
    "lbl_cap_pct_value": {
        "it": "Riduzione %:", "en": "Reduction %:",
        "de": "Reduktion %:", "es": "Reducción %:",
        "doge": "shrink how much?:",
    },
    "lbl_cap_warn": {
        "it": "⚠  Il cap usa bitrate target (VBR). Il peso finale può variare del ±10% rispetto al valore impostato.\nContenuti semplici (screencast, animazioni) tendono a essere più piccoli del target.",
        "en": "⚠  The cap uses target bitrate (VBR). Final size may vary ±10% from the set value.\nSimple content (screencasts, animations) tends to be smaller than the target.",
        "de": "⚠  Das Limit verwendet Ziel-Bitrate (VBR). Die endgültige Größe kann ±10% abweichen.\nEinfache Inhalte (Screencasts, Animationen) sind oft kleiner als das Ziel.",
        "es": "⚠  El límite usa bitrate objetivo (VBR). El tamaño final puede variar ±10%.\nContenido simple (screencasts, animaciones) tiende a ser más pequeño que el objetivo.",
        "doge": "⚠  cap = VBR target. maybe ±10% off. simple video = smaller. wow.",
    },
    "btn_auto_ok": {
        "it": "✔  Conferma impostazioni AUTO",
        "en": "✔  Confirm AUTO settings",
        "de": "✔  AUTO-Einstellungen bestätigen",
        "es": "✔  Confirmar configuración AUTO",
        "doge": "✔  confirm wow",
    },
    "btn_auto_cancel": {
        "it": "Annulla", "en": "Cancel", "de": "Abbrechen", "es": "Cancelar",
        "doge": "nope",
    },
    "btn_auto_settings": {
        "it": "⚙  Impostazioni AUTO…", "en": "⚙  AUTO settings…",
        "de": "⚙  AUTO-Einstellungen…", "es": "⚙  Configuración AUTO…",
        "doge": "⚙  AUTO settings wow",
    },
    "btn_save_preset": {
        "it": "💾  Salva preset", "en": "💾  Save preset",
        "de": "💾  Preset speichern", "es": "💾  Guardar preset",
        "doge": "💾  save command wow",
    },
    "btn_load_preset": {
        "it": "📂  Carica preset", "en": "📂  Load preset",
        "de": "📂  Preset laden", "es": "📂  Cargar preset",
        "doge": "📂  load command wow",
    },
    "dlg_preset_save_title": {
        "it": "Salva preset ffmpeg", "en": "Save ffmpeg preset",
        "de": "FFmpeg-Preset speichern", "es": "Guardar preset ffmpeg",
        "doge": "save preset wow",
    },
    "dlg_preset_save_label": {
        "it": "Nome del preset:", "en": "Preset name:",
        "de": "Preset-Name:", "es": "Nombre del preset:",
        "doge": "what name? wow:",
    },
    "dlg_preset_save_placeholder": {
        "it": "Es: H264 Instagram, ProRes Edit...", "en": "E.g: H264 Instagram, ProRes Edit...",
        "de": "Z.B: H264 Instagram, ProRes Edit...", "es": "Ej: H264 Instagram, ProRes Edit...",
        "doge": "such name. very describe. wow",
    },
    "dlg_preset_load_title": {
        "it": "Carica preset ffmpeg", "en": "Load ffmpeg preset",
        "de": "FFmpeg-Preset laden", "es": "Cargar preset ffmpeg",
        "doge": "load preset wow",
    },
    "dlg_preset_no_presets": {
        "it": "Nessun preset salvato.", "en": "No saved presets.",
        "de": "Keine gespeicherten Presets.", "es": "No hay presets guardados.",
        "doge": "no preset. much empty. wow.",
    },
    "dlg_preset_cmd_label": {
        "it": "Comando:", "en": "Command:",
        "de": "Befehl:", "es": "Comando:",
        "doge": "such command:",
    },
    "dlg_preset_delete": {
        "it": "🗑  Elimina", "en": "🗑  Delete",
        "de": "🗑  Löschen", "es": "🗑  Eliminar",
        "doge": "🗑  bye bye",
    },
    "dlg_preset_use": {
        "it": "✔  Usa questo preset", "en": "✔  Use this preset",
        "de": "✔  Dieses Preset verwenden", "es": "✔  Usar este preset",
        "doge": "✔  use it wow",
    },
    "dlg_preset_warn_empty": {
        "it": "Inserisci un nome per il preset.", "en": "Please enter a preset name.",
        "de": "Bitte einen Preset-Namen eingeben.", "es": "Por favor ingresa un nombre para el preset.",
        "doge": "pls type name. much empty. wow.",
    },
    "dlg_preset_warn_no_cmd": {
        "it": "Il comando è vuoto. Abilita prima la modalità manuale e scrivi un comando.",
        "en": "The command is empty. Enable manual mode first and type a command.",
        "de": "Der Befehl ist leer. Aktiviere zuerst den manuellen Modus und gib einen Befehl ein.",
        "es": "El comando está vacío. Habilita el modo manual primero y escribe un comando.",
        "doge": "command empty. type something first. wow.",
    },
    "dlg_preset_export_title": {
        "it": "Esporta preset in JSON", "en": "Export presets to JSON",
        "de": "Presets als JSON exportieren", "es": "Exportar presets a JSON",
        "doge": "export preset wow",
    },
    "dlg_preset_import_title": {
        "it": "Importa preset da JSON", "en": "Import presets from JSON",
        "de": "Presets aus JSON importieren", "es": "Importar presets desde JSON",
        "doge": "import preset wow",
    },
    "dlg_preset_import_ok": {
        "it": "Preset importati con successo!", "en": "Presets imported successfully!",
        "de": "Presets erfolgreich importiert!", "es": "¡Presets importados con éxito!",
        "doge": "import done! such success! wow!",
    },
    "dlg_preset_import_err": {
        "it": "Errore durante l'importazione. Il file non è valido.",
        "en": "Import error. The file is not valid.",
        "de": "Importfehler. Die Datei ist ungültig.",
        "es": "Error de importación. El archivo no es válido.",
        "doge": "oops. bad file. much error. wow.",
    },
    "btn_preset_export": {
        "it": "⬆  Esporta JSON", "en": "⬆  Export JSON",
        "de": "⬆  JSON exportieren", "es": "⬆  Exportar JSON",
        "doge": "⬆  export wow",
    },
    "btn_preset_import": {
        "it": "⬇  Importa JSON", "en": "⬇  Import JSON",
        "de": "⬇  JSON importieren", "es": "⬇  Importar JSON",
        "doge": "⬇  import wow",
    },
    "lbl_hint": {
        "it": "Usa {INPUT} e {OUTPUT} come segnaposto",
        "en": "Use {INPUT} and {OUTPUT} as placeholders",
        "de": "Verwende {INPUT} und {OUTPUT} als Platzhalter",
        "es": "Usa {INPUT} y {OUTPUT} como marcadores de posición",
        "doge": "put {INPUT} and {OUTPUT} here. much magic.",
    },
    # ── Convert button ─────────────────────────────────────
    "btn_go": {
        "it": "▶  CONVERTI", "en": "▶  CONVERT", "de": "▶  KONVERTIEREN",
        "es": "▶  CONVERTIR", "doge": "▶  DO THE THING wow",
    },
    "btn_stop": {
        "it": "■  INTERROMPI", "en": "■  STOP", "de": "■  ABBRECHEN",
        "es": "■  DETENER", "doge": "■  STOP IT wow",
    },
    # ── Terminal ───────────────────────────────────────────
    "lbl_terminal": {
        "it": "Log Terminale:", "en": "Terminal Log:", "de": "Terminal-Protokoll:",
        "es": "Registro de Terminal:", "doge": "such log, very output:",
    },
    "chk_verbose": {
        "it": "Mostra Log Completo", "en": "Show Full Log", "de": "Vollständiges Protokoll anzeigen",
        "es": "Mostrar registro completo", "doge": "show all the things",
    },
    "terminal_ph": {
        "it": "L'output di ffmpeg apparirà qui…",
        "en": "FFmpeg output will appear here…",
        "de": "FFmpeg-Ausgabe erscheint hier…",
        "es": "La salida de ffmpeg aparecerá aquí…",
        "doge": "wow output come here. much wait.",
    },
    # ── Bottom bar ─────────────────────────────────────────
    "lic_bar": {
        "it": "  DISAGIO PRODUCTION CONVERTER  —  Open source, licenza GNU GPL v3  —  github.com/PlayerintheBUG/Disagio-Production-Converter",
        "en": "  DISAGIO PRODUCTION CONVERTER  —  Open source, GNU GPL v3 license  —  github.com/PlayerintheBUG/Disagio-Production-Converter",
        "de": "  DISAGIO PRODUCTION CONVERTER  —  Open Source, GNU GPL v3 Lizenz  —  github.com/PlayerintheBUG/Disagio-Production-Converter",
        "es": "  DISAGIO PRODUCTION CONVERTER  —  Código abierto, licencia GNU GPL v3  —  github.com/PlayerintheBUG/Disagio-Production-Converter",
        "doge": "  DISAGIO PRODUCTION CONVERTER  —  very open source wow  —  github.com/PlayerintheBUG/Disagio-Production-Converter",
    },
    # ── Auto mode ──────────────────────────────────────────
    "auto_cmd_preview": {
        "it": "ffmpeg [parametri calcolati automaticamente per ogni file — vedi terminale durante la conversione]",
        "en": "ffmpeg [parameters calculated automatically for each file — see terminal during conversion]",
        "de": "ffmpeg [Parameter werden für jede Datei automatisch berechnet — Terminal während der Konvertierung beachten]",
        "es": "ffmpeg [parámetros calculados automáticamente para cada archivo — ver terminal durante la conversión]",
        "doge": "ffmpeg [much auto. such calculate. see terminal wow]",
    },
    # ── Dialogs ────────────────────────────────────────────
    "dlg_warn_title": {
        "it": "Attenzione", "en": "Warning", "de": "Achtung", "es": "Atención",
        "doge": "wow careful",
    },
    "dlg_warn_no_file": {
        "it": "Seleziona prima un file o una cartella.",
        "en": "Please select a file or folder first.",
        "de": "Bitte zuerst eine Datei oder einen Ordner auswählen.",
        "es": "Por favor selecciona primero un archivo o carpeta.",
        "doge": "pls pick file first. such empty. wow.",
    },
    "dlg_auto_folder_title": {
        "it": "Modalità AUTO — cartella",
        "en": "AUTO mode — folder",
        "de": "AUTO-Modus — Ordner",
        "es": "Modo AUTO — carpeta",
        "doge": "AUTO mode — many file wow",
    },
    "dlg_auto_folder_body": {
        "it": "In modalità AUTO ogni file viene analizzato con ffprobe prima della conversione.\nSu cartelle grandi questo può richiedere qualche minuto in più.\n\nProcedere?",
        "en": "In AUTO mode, each file is analyzed with ffprobe before conversion.\nFor large folders this may take a few extra minutes.\n\nProceed?",
        "de": "Im AUTO-Modus wird jede Datei vor der Konvertierung mit ffprobe analysiert.\nBei großen Ordnern kann dies einige Minuten länger dauern.\n\nFortfahren?",
        "es": "En modo AUTO, cada archivo se analiza con ffprobe antes de la conversión.\nEn carpetas grandes esto puede tardar algunos minutos extra.\n\nProceder?",
        "doge": "AUTO mode: ffprobe sniff every file first. big folder = much wait.\n\ndo it? wow",
    },
    "dlg_no_files_title": {
        "it": "Nessun file", "en": "No files", "de": "Keine Dateien", "es": "Ningún archivo",
        "doge": "such empty",
    },
    "dlg_no_files_body": {
        "it": "Nessun file da convertire trovato.",
        "en": "No files to convert were found.",
        "de": "Keine zu konvertierenden Dateien gefunden.",
        "es": "No se encontraron archivos para convertir.",
        "doge": "no file found. much sadness. wow.",
    },
    "dlg_confirm_title": {
        "it": "Conferma", "en": "Confirm", "de": "Bestätigen", "es": "Confirmar",
        "doge": "u sure? wow",
    },
    "dlg_done_title": {
        "it": "Conversione completata", "en": "Conversion completed",
        "de": "Konvertierung abgeschlossen", "es": "Conversión completada",
        "doge": "all done! such convert! wow!",
    },
    "dlg_done_body_ok": {
        "it": "✅  File convertiti:", "en": "✅  Files converted:", "de": "✅  Konvertierte Dateien:",
        "es": "✅  Archivos convertidos:", "doge": "✅  wow files done:",
    },
    "dlg_done_body_err": {
        "it": "⚠️  File convertiti:", "en": "⚠️  Files converted:", "de": "⚠️  Konvertierte Dateien:",
        "es": "⚠️  Archivos convertidos:", "doge": "⚠️  many done:",
    },
    "dlg_done_errors": {
        "it": "\n   Errori:", "en": "\n   Errors:", "de": "\n   Fehler:", "es": "\n   Errores:",
        "doge": "\n   oops:",
    },
    # ── confirm dialog fields ──────────────────────────────
    "conf_files": {
        "it": "File da convertire:", "en": "Files to convert:", "de": "Zu konvertierende Dateien:",
        "es": "Archivos a convertir:", "doge": "files to wow:",
    },
    "conf_img_conv": {
        "it": "Immagini da convertire:", "en": "Images to convert:", "de": "Zu konvertierende Bilder:",
        "es": "Imágenes a convertir:", "doge": "pics to change:",
    },
    "conf_raw": {
        "it": "File RAW da copiare in FOTO_RAW:", "en": "RAW files to copy to FOTO_RAW:",
        "de": "RAW-Dateien in FOTO_RAW kopieren:", "es": "Archivos RAW a copiar en FOTO_RAW:",
        "doge": "RAW to copy, such safe:",
    },
    "conf_fmt": {
        "it": "Formato output:", "en": "Output format:", "de": "Ausgabeformat:",
        "es": "Formato de salida:", "doge": "output box:",
    },
    "conf_qual": {
        "it": "Qualità:", "en": "Quality:", "de": "Qualität:", "es": "Calidad:",
        "doge": "how good?:",
    },
    "conf_gpu": {
        "it": "Encoder GPU:", "en": "GPU Encoder:", "de": "GPU-Encoder:",
        "es": "Codificador GPU:", "doge": "fast chip:",
    },
    "conf_hw": {
        "it": "HW decoding:", "en": "HW decoding:", "de": "HW-Dekodierung:", "es": "Decodificación HW:",
        "doge": "hardware fast?:",
    },
    "conf_hw_yes": {
        "it": "Sì", "en": "Yes", "de": "Ja", "es": "Sí", "doge": "wow yes",
    },
    "conf_hw_no": {
        "it": "No", "en": "No", "de": "Nein", "es": "No", "doge": "such no",
    },
    "conf_vcodec": {
        "it": "Codec video:", "en": "Video codec:", "de": "Video-Codec:", "es": "Codec de video:",
        "doge": "encode magic:",
    },
    "conf_container": {
        "it": "Container:", "en": "Container:", "de": "Container:", "es": "Contenedor:",
        "doge": "file box:",
    },
    "conf_res": {
        "it": "Risoluzione:", "en": "Resolution:", "de": "Auflösung:", "es": "Resolución:",
        "doge": "many pixel?:",
    },
    "conf_acodec": {
        "it": "Codec audio:", "en": "Audio codec:", "de": "Audio-Codec:", "es": "Codec de audio:",
        "doge": "sound code:",
    },
    "conf_samplerate": {
        "it": "Sample rate:", "en": "Sample rate:", "de": "Abtastrate:",
        "es": "Frecuencia de muestreo:", "doge": "sound samples:",
    },
    "conf_prefix": {
        "it": "Prefisso:", "en": "Prefix:", "de": "Präfix:", "es": "Prefijo:",
        "doge": "name before name:",
    },
    # ── log messages ───────────────────────────────────────
    "log_interrupted": {
        "it": "\n⚠  Conversione interrotta dall'utente.",
        "en": "\n⚠  Conversion interrupted by user.",
        "de": "\n⚠  Konvertierung vom Benutzer unterbrochen.",
        "es": "\n⚠  Conversión interrumpida por el usuario.",
        "doge": "\n⚠  user say STOP. such interrupt. wow.",
    },
    "log_completed": {
        "it": "  COMPLETATO — OK:", "en": "  COMPLETED — OK:", "de": "  ABGESCHLOSSEN — OK:",
        "es": "  COMPLETADO — OK:", "doge": "  WOW DONE — OK:",
    },
    "log_errors": {
        "it": "   ERRORI:", "en": "   ERRORS:", "de": "   FEHLER:", "es": "   ERRORES:",
        "doge": "   oops:",
    },
    # ── theme editor dialog ────────────────────────────────
    "dlg_theme_title": {
        "it": "Editor Tema Personalizzato", "en": "Custom Theme Editor",
        "de": "Benutzerdefinierter Design-Editor", "es": "Editor de Tema Personalizado",
        "doge": "wow color editor",
    },
    "dlg_theme_name_lbl": {
        "it": "Nome Tema:", "en": "Theme name:", "de": "Design-Name:", "es": "Nombre del tema:",
        "doge": "name the color:",
    },
    "dlg_theme_name_ph": {
        "it": "Es. Mio Tema...", "en": "E.g. My Theme...", "de": "Z.B. Mein Design...",
        "es": "Ej. Mi Tema...", "doge": "E.g. such theme...",
    },
    "dlg_theme_info": {
        "it": "Clicca sui colori per modificarli:", "en": "Click colors to edit them:",
        "de": "Klicke auf Farben zum Bearbeiten:", "es": "Haz clic en los colores para editarlos:",
        "doge": "click color to wow change:",
    },
    "dlg_theme_save": {
        "it": "Salva Tema", "en": "Save Theme", "de": "Design speichern", "es": "Guardar Tema",
        "doge": "keep colors wow",
    },
    "dlg_theme_cancel": {
        "it": "Annulla", "en": "Cancel", "de": "Abbrechen", "es": "Cancelar",
        "doge": "nope",
    },
    "dlg_theme_delete": {
        "it": "Elimina Tema", "en": "Delete Theme", "de": "Design löschen", "es": "Eliminar Tema",
        "doge": "bye color",
    },
    "dlg_theme_default_name": {
        "it": "Tema Custom", "en": "Custom Theme", "de": "Benutzerdefiniertes Design",
        "es": "Tema Personalizado", "doge": "wow custom",
    },
    "dlg_color_pick": {
        "it": "Scegli Colore", "en": "Pick Color", "de": "Farbe wählen", "es": "Elegir Color",
        "doge": "pick wow color",
    },
    # ── license dialog ─────────────────────────────────────
    "dlg_lic_title": {
        "it": "Licenza — GNU GPL v3", "en": "License — GNU GPL v3",
        "de": "Lizenz — GNU GPL v3", "es": "Licencia — GNU GPL v3",
        "doge": "legal stuff — GNU GPL v3 wow",
    },
    # ── ffmpeg not found ───────────────────────────────────
    "ffmpeg_not_found_title": {
        "it": "FFmpeg non trovato", "en": "FFmpeg not found",
        "de": "FFmpeg nicht gefunden", "es": "FFmpeg no encontrado",
        "doge": "where ffmpeg? such missing wow",
    },
    "ffmpeg_not_found_body": {
        "it": "Impossibile trovare ffmpeg.\n\nCercato in:\n  • Bundle exe (PyInstaller)\n  • Cartella dell'eseguibile\n  • PATH di sistema\n\nSu Linux installa con:  sudo dnf install ffmpeg\nSu Windows scarica da:  https://ffmpeg.org/download.html\ne metti ffmpeg.exe nella stessa cartella di questo programma.",
        "en": "Cannot find ffmpeg.\n\nSearched in:\n  • PyInstaller bundle\n  • Executable folder\n  • System PATH\n\nOn Linux install with:  sudo dnf install ffmpeg\nOn Windows download from:  https://ffmpeg.org/download.html\nand put ffmpeg.exe in the same folder as this program.",
        "de": "FFmpeg konnte nicht gefunden werden.\n\nGesucht in:\n  • PyInstaller-Bundle\n  • Ausführbarer Ordner\n  • System-PATH\n\nUnter Linux installieren mit:  sudo dnf install ffmpeg\nUnter Windows herunterladen von:  https://ffmpeg.org/download.html\nund ffmpeg.exe in denselben Ordner wie dieses Programm legen.",
        "es": "No se puede encontrar ffmpeg.\n\nBuscado en:\n  • Bundle PyInstaller\n  • Carpeta del ejecutable\n  • PATH del sistema\n\nEn Linux instalar con:  sudo dnf install ffmpeg\nEn Windows descargar de:  https://ffmpeg.org/download.html\ny poner ffmpeg.exe en la misma carpeta que este programa.",
        "doge": "ffmpeg not here. much missing wow.\n\nlooked in:\n  • exe bundle\n  • exe folder\n  • system PATH\n\nLinux: sudo dnf install ffmpeg\nWindows: get from https://ffmpeg.org/download.html\nput ffmpeg.exe next to this program. pls.",
    },
    # ── sample rates / resolutions (translated labels) ─────
    "keep_original": {
        "it": "Mantieni originale", "en": "Keep original", "de": "Original beibehalten",
        "es": "Mantener original", "doge": "keep as is wow",
    },
}

# Active language code
_LANG = "it"

def T(key: str) -> str:
    """Return translated string for the current language."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(_LANG, entry.get("it", key))

def set_language(lang_code: str):
    global _LANG
    _LANG = lang_code


# ── Localised display for RESOLUTIONS and SAMPLE_RATES ───────────────────────
