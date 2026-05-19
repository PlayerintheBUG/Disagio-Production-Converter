# 🎬 Disagio Production Converter

Un convertitore multimediale ad alte prestazioni, Sviluppato in Python con un'interfaccia grafica moderna in PyQt6, sfrutta la potenza di FFmpeg per garantire conversioni rapide, stabili e fedeli all'originale.

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


## 🚀 Download (.exe per Windows)
Puoi scaricare l'eseguibile per Windows già pronto all'uso, senza dover installare Python o FFmpeg, direttamente dalla sezione **[Releases](https://github.com/PlayerintheBUG/Disagio-Production-Converter/releases)** sulla destra di questa pagina.

### Nota per l'uso dell'eseguibile:
L'eseguibile integra al suo interno i binari di FFmpeg e FFprobe per funzionare in modalità standalone.

---

## 🛠️ Come eseguirlo dal codice sorgente
Se preferisci non usare l'eseguibile e lanciarlo tramite Python:

1. Clona il repository:
   ```bash
   git clone [https://github.com/PlayerintheBUG/Disagio-Production-Converter.git](https://github.com/PlayerintheBUG/Disagio-Production-Converter.git)

---
⚖️ Licenza e Note Legali

**Codice sorgente del progetto**  
Questo progetto è distribuito sotto licenza **GNU General Public License v3.0** (GPLv3).  
Il codice sorgente completo è disponibile su questo repository GitHub.

**FFmpeg e FFprobe**  
L'eseguibile Windows include al suo interno i binari di **FFmpeg** e **ffprobe** (build full) per funzionare in modalità completamente standalone.

- I binari provengono dalle build ufficiali **[gyan.dev](https://www.gyan.dev/ffmpeg/builds/)** (versione full GPLv3).
- FFmpeg è rilasciato sotto **GNU General Public License v3** a causa dell'inclusione di codec e librerie sotto licenza GPL (es. x264, x265, ecc.).
- **Nessuna modifica** è stata apportata ai binari originali di FFmpeg.

**Come ottenere il codice sorgente di FFmpeg**  
Puoi scaricare il codice sorgente corrispondente alla versione utilizzata qui:  
→ [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) (sezione "Source code")  

Oppure clonando direttamente il repository ufficiale:  
```bash
git clone https://git.ffmpeg.org/ffmpeg.git
