# 🎬 Disagio Production Converter

Un convertitore multimediale ad alte prestazioni, Sviluppato in Python con un'interfaccia grafica moderna in PyQt6, sfrutta la potenza di FFmpeg per garantire conversioni rapide, stabili e fedeli all'originale.

---

✨ Caratteristiche Principali

🧠 Automazione e Gestione Intelligente
- **Decisionale AUTO:** Il convertitore analizza istantaneamente i metadati del file sorgente tramite ffprobe e calcola dinamicamente il valore di CQ (Constant Quality) ideale. Questo permette di bilanciare in automatico il peso finale del file e la fedeltà visiva, senza richiedere interventi manuali o competenze tecniche.
- **Downscale Avanzato con Padding:** Ridimensiona i video sfruttando l'altissima qualità del filtro Lanczos. Il software calcola al millesimo i margini geometrici (padding) per preservare l'aspect ratio originale, evitando qualsiasi tipo di distorsione o allungamento dell'immagine.

📸 Elaborazione e Conversione Immagini
- **Convertitore Grafico Multiformato:** Espande le funzionalità del software oltre il comparto video, introducendo la gestione nativa dei file grafici. Consente di convertire qualsiasi immagine sorgente nei formati JPG, PNG, WebP e BMP.
- **Profili di Compressione Dedicati:** Ottimizza lo spazio su disco o la qualità visiva grazie a algoritmi di compressione specifici per WebP e JPG, permettendo di scegliere tra il massimo risparmio di spazio o la conservazione millimetrica dei dettagli.
- **Interfaccia Dinamica:** La GUI si adatta automaticamente rilevando il tipo di file caricato, mostrando all'utente solo i filtri, i parametri e le opzioni pertinenti alla modalità Video o alla modalità Immagine.

🛡️ Stabilità ed Efficienza di Sistema
- **Interfaccia Grafica Anti-Freeze:** Sfrutta l'architettura in multithreading nativo (QThread). Il motore di rendering lavora in totale isolamento in background: l'interfaccia utente (PyQt6) rimane fluida, risponde istantaneamente ai comandi e aggiorna la barra di avanzamento in tempo reale anche durante le conversioni più pesanti.
- **Analisi Robusta dei Flussi:** Gestione avanzata dei flussi multimediali per prevenire crash ed errori critici su file danneggiati o complessi, tracce audio mancanti, flussi sottotitoli o video a framerate variabile (VFR).

🚀 Accelerazione Hardware Avanzata
Integrazione profonda con i principali encoder di sistema per sfruttare al massimo la potenza computazionale di CPU e GPU moderne, riducendo drasticamente i tempi di esportazione:
- **NVIDIA NVENC:** Sfruttamento dei core dedicati delle schede grafiche GeForce RTX / GTX.
- **AMD AMF & Intel QSV:** Supporto completo alle tecnologie di accelerazione hardware Radeon e Intel Graphics.
- **Codifica Software Ottimizzata:** Pipeline di elaborazione via CPU efficiente e ottimizzata per i sistemi che non dispongono di una GPU dedicata.

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


Note aggiuntive
FFmpeg viene eseguito come processo esterno (subprocess).
Nessuna modifica è stata apportata ai binari.

Per qualsiasi chiarimento sulle licenze, apri pure una Issue su questo repository.
