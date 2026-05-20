🎬 Disagio Production Converter
Un convertitore multimediale ad alte prestazioni. Sviluppato in Python con un'interfaccia grafica moderna in PyQt6, sfrutta la potenza di FFmpeg per garantire conversioni rapide, stabili e fedeli all'originale.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Caratteristiche Principali

🧠 Automazione e Gestione Intelligente
* **Decisionale AUTO:** Il convertitore analizza istantaneamente i metadati del file sorgente tramite `ffprobe` e calcola dinamicamente il valore di CQ (Constant Quality) ideale. Questo permette di bilanciare in automatico il peso finale del file e la fedeltà visiva, senza richiedere interventi manuali o competenze tecniche.
* **Downscale Avanzato con Padding:** Ridimensiona i video sfruttando l'altissima qualità del filtro Lanczos. Il software calcola al millesimo i margini geometrici (padding) per preservare l'aspect ratio originale, evitando qualsiasi tipo di distorsione o allungamento dell'immagine.

🎨 Personalizzazione e Interfaccia Avanzata
* **Gestione Temi Dinamica:** Il software introduce il supporto completo alla personalizzazione estetica dell'interfaccia grafica tramite due modalità distinte:
    * **Temi Predefiniti:** Profili di colore preimpostati e ottimizzati per l'uso quotidiano (Light/Dark mode e varianti cromatiche).
    * **Temi Personalizzati (Customizer):** Un editor avanzato che permette all'utente di modificare manualmente ogni singolo colore dell'interfaccia, dei pulsanti, dei testi e dei menu, creando la propria combinazione personalizzata.

📸 Elaborazione e Conversione Immagini
* **Convertitore Grafico Multiformato:** Espande le funzionalità del software oltre il comparto video, introducendo la gestione nativa dei file grafici. Consente di convertire qualsiasi immagine sorgente nei formati JPG, PNG, WebP e BMP.
* **Profili di Compressione Dedicati:** Ottimizza lo spazio su disco o la qualità visiva grazie a algoritmi di compressione specifici per WebP e JPG, permettendo di scegliere tra il massimo risparmio di spazio o la conservazione millimetrica dei dettagli.

🛡️ Stabilità ed Efficienza di Sistema
* **Interfaccia Grafica Anti-Freeze:** Sfrutta l'architettura in multithreading nativo (`QThread`). Il motore di rendering lavora in totale isolamento in background: l'interfaccia utente (PyQt6) rimane fluida, risponde istantaneamente ai comandi e aggiorna la barra di avanzamento in tempo reale anche durante le conversioni più pesanti.
* **Analisi Robusta dei Flussi:** Gestione avanzata dei flussi multimediali per prevenire crash ed errori critici su file danneggiati o complessi, tracce audio mancanti, flussi sottotitoli o video a framerate variabile (VFR).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Accelerazione Hardware Avanzata
Integrazione profonda con i principali encoder di sistema per sfruttare al massimo la potenza computazionale di CPU e GPU moderne, riducendo drasticamente i tempi di esportazione:

* **NVIDIA NVENC:** Sfruttamento dei core dedicati delle schede grafiche GeForce RTX / GTX.
* **AMD AMF & Intel QSV:** Supporto completo alle tecnologie di accelerazione hardware Radeon e Intel Graphics.
* **Codifica Software Ottimizzata:** Pipeline di elaborazione via CPU efficiente e ottimizzata per i sistemi che non dispongono di una GPU dedicata.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Installazione e Utilizzo
Il Disagio Production Converter è progettato per essere versatile e cross-platform. Scegli la procedura adatta al tuo sistema operativo:

🐧 Per utenti Linux
Il software sfrutta le librerie di sistema per garantire le massime prestazioni.
Assicurati di avere `ffmpeg` e `ffprobe` installati (Esempio su Fedora):
```
sudo dnf install ffmpeg ffmpeg-free-devel
```
Scaricare dalla sezione Release il file Disagio_Production_Converter.py

🪟 Per utenti Windows (.exe)
Puoi scaricare l'eseguibile per Windows già pronto all'uso, senza dover installare Python o FFmpeg, direttamente dalla sezione Releases sulla destra di questa pagina.

Nota per l'uso dell'eseguibile: L'eseguibile integra al suo interno i binari di FFmpeg e FFprobe per funzionare in totale modalità standalone (One-File).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ Note Legali e Conformità Licenze (GPLv3)
In conformità con la GNU General Public License v3, si dichiara quanto segue:

  Licenza del software: "Disagio Production Converter" è distribuito interamente sotto licenza GNU GPLv3. Il codice sorgente completo è disponibile in questo repository GitHub.

  FFmpeg e ffprobe: La distribuzione compilata per Windows include i binari nativi ffmpeg.exe e ffprobe.exe (Version: 8.1.1 Full Build, scaricati non modificati da https://www.gyan.dev/ffmpeg/      builds/). FFmpeg è rilasciato sotto licenza GNU GPLv3 per via dei codec open-source commerciali inclusi (come x264, x265, ecc.), risultando al 100% compatibile con la licenza di questo progetto.

  Note aggiuntive: FFmpeg viene eseguito dall'applicazione come processo esterno isolato (subprocess). Nessuna modifica strutturale o software è stata apportata ai binari originali.

  Per qualsiasi chiarimento sulle licenze o richieste di supporto, apri pure una Issue su questo repository.
