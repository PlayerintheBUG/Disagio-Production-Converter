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

🔬 Modulo di Ingrandimento (Upscaling con Filtri)
Questa funzione NON utilizza l'intelligenza artificiale o reti neurali: non inventa dettagli dal nulla e non richiede il download di modelli pesanti. Si tratta invece di una **pipeline di filtri nativa FFmpeg super veloce**, studiata per ingrandire i video in modo nitido e pulito in un unico passaggio, lavorando su tre fasi consecutive:

1. Pulizia dal Rumore (`hqdn3d`): Rimuove le sgranature e i difetti di compressione *prima* dell'ingrandimento, evitando che il software aumenti anche i difetti visivi del vecchio file
2. Ingrandimento Ottimizzato (Filtro Lanczos): Modifica le dimensioni geometriche del video (a `2x`, `3x` o `4x`) mantenendo le proporzioni originali intatte ed evitando distorsioni
3. Nitidezza dei Bordi (`unsharp`): Applica un filtro di contrasto mirato sui contorni subito dopo l'ingrandimento, migliorando la definizione percepita dei dettagli

Caratteristiche e Gestione dei Formati:
* **Formati Standard (MP4 / MKV):** Permette di esportare in AV1, H.264 o H.265 sfruttando sia la CPU che l'accelerazione della scheda video (NVIDIA, AMD, Intel) per la massima velocità La qualità si imposta facilmente su 5 livelli (da minima a massima)
* **Formati Professionali (MOV):** Ideale per chi fa montaggio video. Supporta la codifica diretta in Apple ProRes o Avid DNxHR (lavorando via CPU), configurando in automatico i profili di qualità ufficiali
* **Audio Inalterato:** Qualunque sia il formato scelto, la traccia audio originale non viene mai ricodificata, ma viene copiata direttamente a specchio per mantenere la massima fedeltà (`-c:a copy`)
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
Scaricare dalla sezione Releases il file Disagio_Production_Converter.py

🪟 Per utenti Windows (.exe)
Puoi scaricare l'eseguibile per Windows già pronto all'uso, senza dover installare Python o FFmpeg, direttamente dalla sezione Releases sulla destra di questa pagina.

Nota per l'uso dell'eseguibile: L'eseguibile integra al suo interno i binari di FFmpeg e FFprobe per funzionare in totale modalità standalone (One-File).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ Note Legali e Conformità Licenze (GPLv3)
In conformità con la GNU General Public License v3, si dichiara quanto segue:

  Licenza del software: "Disagio Production Converter" è distribuito interamente sotto licenza GNU GPLv3. Il codice sorgente completo è disponibile in questo repository GitHub.

  FFmpeg e ffprobe: La distribuzione compilata per Windows include i binari nativi ffmpeg.exe e ffprobe.exe (Full Build, scaricati non modificati da https://www.gyan.dev/ffmpeg/      builds/). FFmpeg è rilasciato sotto licenza GNU GPLv3 per via dei codec open-source commerciali inclusi (come x264, x265, ecc.), risultando al 100% compatibile con la licenza di questo progetto.

  Note aggiuntive: FFmpeg viene eseguito dall'applicazione come processo esterno isolato (subprocess). Nessuna modifica strutturale o software è stata apportata ai binari originali.

  Per qualsiasi chiarimento sulle licenze o richieste di supporto, apri pure una Issue su questo repository.
