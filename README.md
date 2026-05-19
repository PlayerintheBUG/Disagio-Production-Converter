# 🎬 Disagio Production Converter

Un convertitore multimediale ad alte prestazioni, ottimizzato per i flussi di lavoro di post-produzione della **Disagio Production**. Sviluppato in Python con un'interfaccia grafica moderna in PyQt6, sfrutta la potenza di FFmpeg per garantire conversioni rapide, stabili e fedeli all'originale.

---

## ✨ Caratteristiche Principali

### 🧠 Automazione Intelligente (v1.1.0)
* **Matrice Decisionale AUTO:** Analizza i metadati del file sorgente tramite `ffprobe` e calcola dinamicamente il valore di CQ (Constant Quality) ideale. Bilancia automaticamente il peso del file e la qualità visiva senza interventi manuali.
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

## 📜 Licenza

Questo progetto è software libero rilasciato sotto i termini della licenza **GNU GPL v3 (GNU General Public License v3.0)**. Sei libero di modificare, distribuire e condividere il software, a patto che ogni opera derivata mantenga la stessa licenza open source.

---

## 🛠️ Installazione e Utilizzo

> 💻 **Ambiente di Sviluppo:** Questo software è stato sviluppato e testato nativamente su **Nobara 43** con ambiente desktop **KDE Plasma**.

### 1. Requisiti di sistema
Assicurati che `ffmpeg` e `ffprobe` siano installati nel sistema. Su Nobara puoi verificarlo o installarli da terminale con:
```
sudo dnf install ffmpeg ffmpeg-free-devel
```
### 2. Clonazione e Configurazione
Esegui questi comandi nel terminale per scaricare il progetto e installare la libreria grafica necessaria.
```bash
git clone [github.com/PlayerintheBUG/Disagio-Production-Converter.git](https://github.com/PlayerintheBUG/Disagio-Production-Converter.git)
cd Disagio-Production-Converter
pip install PyQt6
