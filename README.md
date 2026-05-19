# 🎬 Disagio Production Converter

Un convertitore multimediale ad alte prestazioni, ottimizzato per i flussi di lavoro di post-produzione della **Disagio Production**. Sviluppato in Python con un'interfaccia grafica moderna in PyQt6, sfrutta la potenza di FFmpeg per garantire conversioni rapide, stabili e fedeli all'originale.

---

## ✨ Caratteristiche Principali

### 🧠 Automazione Intelligente (v1.1.0)
* **Decisionale AUTO:** Analizza i metadati del file sorgente tramite `ffprobe` e calcola dinamicamente il valore di CQ (Constant Quality) ideale. Bilancia automaticamente il peso del file e la qualità visiva senza interventi manuali.
* **Downscale con Padding:** Ridimensiona i video utilizzando l'algoritmo **Lanczos**, calcolando il padding al millesimo per mantenere l'aspect ratio originale senza deformare l'immagine.

### 🛡️ Stabilità ed Efficienza
* **Interfaccia Anti-Freeze:** Sfrutta il multithreading nativo (`QThread`). Il motore di FFmpeg lavora in isolamento: la UI rimane fluida, risponde ai comandi e aggiorna la barra di avanzamento in tempo reale anche nei render più pesanti.
* **Analisi Robusta del Flusso:** Gestione avanzata dei metadati per evitare crash su file complessi, tracce audio mancanti o video a framerate variabile (VFR).

### 🚀 Accelerazione Hardware
Integrazione nativa con i principali encoder para sfruttare al massimo CPU e GPU moderne:
* **NVIDIA NVENC** (Architetture GeForce RTX/GTX)
* **AMD AMF** / **Intel QSV**
* Codifica software ottimizzata via CPU

---
🚀 Installazione e Utilizzo

Il Disagio Production Converter è progettato per essere versatile. Scegli la procedura adatta al tuo sistema operativo:
🐧 Per utenti Linux

Il software sfrutta le librerie di sistema per garantire le massime prestazioni.

Assicurati di avere ffmpeg e ffprobe installati:

  Esempio su Fedora:
    sudo dnf install ffmpeg ffmpeg-free-devel

   Clona il repository e installa le dipendenze Python:
    
    git clone https://github.com/PlayerintheBUG/Disagio-Production-Converter.git
    cd Disagio-Production-Converter
    pip install PyQt6

Avvia l'applicazione:

    python disagio_converter.py

🪟 Per utenti Windows 10/11

Non è necessaria alcuna configurazione. è impacchettato tutto in un unico file eseguibile.

    Vai nella sezione Releases di questo repository.

Scarica l'ultima versione disponibile (Disagio_Production_Converter.exe).

Avvia il file con un doppio clic.

Nota: L'eseguibile contiene già al suo interno ffmpeg e ffprobe, quindi è pronto all'uso immediato senza bisogno di installare Python o altri componenti aggiuntivi.

## 📜 Licenza

Questo progetto è software libero rilasciato sotto i termini della licenza **GNU GPL v3 (GNU General Public License v3.0)**. Sei libero di modificare, distribuire e condividere il software, a patto che ogni opera derivata mantenga la stessa licenza open source.
