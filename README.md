# Disagio Production Converter

Un convertitore video e audio avanzato ad alte prestazioni, basato su **FFmpeg** e sviluppato in **Python** con **PyQt6**. Questo strumento è stato ingegnerizzato su misura per ottimizzare i flussi di lavoro di post-produzione e compressione della **Disagio Production**.

## 🚀 Novità della Versione 1.1.0
* **Matrice Decisionale AUTO:** Integrazione di un algoritmo intelligente che analizza i metadati del file sorgente tramite `ffprobe` e calcola dinamicamente il valore di CQ (Constant Quality) ideale, bilanciando peso del file e fedeltà visiva.
* **Filtro di Downscale Avanzato:** Algoritmo di scaling basato su filtro **Lanczos** con gestione automatica del padding per mantenere l'aspect ratio originale senza distorsioni o stiramenti dell'immagine.
* **Ottimizzazione Core:** Correzione dei glitch di parsing dei log e riscrittura dei flussi di threading per una stabilità assoluta durante i processi di rendering più pesanti.

---

## 🔥 Caratteristiche Principali

* **Interfaccia Grafica Moderna (PyQt6):** UI pulita, reattiva e organizzata per gestire parametri complessi in pochi clic.
* **Architettura Multithreading (`QThread`):** Il motore di rendering di FFmpeg gira su thread isolati dal codice della UI. Questo garantisce che l'interfaccia rimanga fluida, non si blocchi mai ("Non risponde") e aggiorni la barra di avanzamento in tempo reale.
* **Analisi Dinamica del Flusso:** Lettura accurata di codec, framerate (CFR/VFR) e tracce audio/video per evitare fallimenti di codifica su file corrotti o privi di audio.
* **Accelerazione Hardware Integrata:** Supporto nativo ai principali encoder hardware per sfruttare al massimo la potenza di CPU e GPU moderne:
  * **NVIDIA NVENC** (per schede grafiche RTX/GTX)
  * **AMD AMF** / **Intel QSV** & codifica software nativa via CPU.

---

## 🛠️ Requisiti di Sistema e Dipendenze

Il software è ottimizzato per ambienti **Linux** (sviluppato e testato su Nobara Linux / KDE Plasma).

### Dipendenze di sistema:
* **Python 3.10+**
* **FFmpeg** e **FFprobe** installati nel sistema e accessibili dal PATH.

### Dipendenze Python:
```bash
pip install PyQt6
