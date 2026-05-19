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
⚖️ Note Legali e Conformità Licenze (GPLv3)
In conformità con la GNU General Public License v3, si dichiara quanto segue:

Licenza del software
“Disagio Production Converter” è distribuito interamente sotto GNU GPLv3.
Il codice sorgente completo è disponibile su questo repository GitHub.
FFmpeg e ffprobe
Questo eseguibile include i binari ffmpeg.exe e ffprobe.exe (versione 8.1.1 full_build).
I binari sono originali e non modificati.
Sono stati scaricati dalle build ufficiali di gyan.dev.
FFmpeg è rilasciato sotto GNU GPLv3 per via dei codec GPL inclusi (x264, x265, ecc.).

Corresponding Source di FFmpeg
Il codice sorgente completo corrispondente alla versione 8.1.1 può essere trovato qui:
Commit esatto usato da gyan.dev:
→ https://github.com/FFmpeg/FFmpeg/commit/239f2c733d
Pagina generale di download sorgenti: https://ffmpeg.org/download.html

Note aggiuntive
FFmpeg viene eseguito come processo esterno (subprocess).
Nessuna modifica è stata apportata ai binari.

Per qualsiasi chiarimento sulle licenze, apri pure una Issue su questo repository.
