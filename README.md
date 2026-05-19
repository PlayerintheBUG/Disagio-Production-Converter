# 🎬 Disagio Production Converte

Un convertitore multimediale leggero. basato su **PyQt6** e **FFmpeg**.

## 🚀 Caratteristiche Principali

* **Accelerazione Hardware Dedicata:** Preset nativi ottimizzati per encoder **NVIDIA (NVENC)**, **AMD (AMF)**, e **Intel (QSV)**.
* **Formati di Montaggio Professionali:** Supporto diretto a codec intermedi intra-frame come **ProRes** e **DNxHR** per un editing fluido e senza scatti su DaVinci Resolve o Premiere.
* **Audio ad Alta Fedeltà:** Gestione profili audio avanzati tra cui **FLAC** (con compressione variabile) e **PCM 32-bit float / 24-bit** per archiviare master e registrazioni senza alcuna perdita di qualità.
* **FFmpeg Live Preview:** Monitoraggio in tempo reale della stringa di comando esatta generata dall'interfaccia grafica, con supporto alla modalità di **modifica manuale** per i flussi di lavoro più complessi.
* **Elaborazione in Batch Sicura:** Converte file singoli o intere cartelle mantenendo l'albero delle directory in una cartella dedicata (`CONVERTITI_DISAGIO`), con un algoritmo di auto-rinomina per evitare la sovrascrittura accidentale dei file RAW originali.
## ⚖️ Licenza e Note Legali

Copyright (C) 2026 PlayerintheBUG

Questo programma è software libero: puoi ridistribuirlo e/o modificarlo secondo i termini della Licenza Pubblica Generica GNU (GPL) versione 3, come pubblicata dalla Free Software Foundation.

Questo programma è distribuito nella speranza che sia utile, ma **SENZA ALCUNA GARANZIA**; senza nemmeno la garanzia implicita di **COMMERCIABILITÀ** o **IDONEITÀ PER UNO SCOPO PARTICOLARE**. Vedi la licenza GNU GPL v3 per maggiori dettagli

Assicurati che `ffmpeg` e `ffprobe` siano installati nel sistema e accessibili dal percorso globale:
```bash
sudo dnf install ffmpeg ffmpeg-free-devel

# Clona il progetto
git clone [https://github.com/PlayerintheBUG/Disagio-Production-Converter.git](https://github.com/PlayerintheBUG/Disagio-Production-Converter.git)
cd Disagio-Production-Converter

# Installa PyQt6 per il tuo utente
pip install PyQt6 --user

# Lancia il convertitore
python3 Disagio_Production_Converter.py



