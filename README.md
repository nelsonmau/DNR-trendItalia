# DNR Trend Italia

Analisi longitudinale dei dati italiani dal **Reuters Institute Digital News Report** (2021–2026).

## Contenuto

```
.
├── article_italia_dnr.md        # Bozza articolo Substack
├── extract_pdfs.py              # Script estrazione testo dai PDF
├── extracted/                   # Testo estratto dai report (Markdown)
│   ├── Digital_News_Report_2021.md
│   ├── Digital_News_Report_2022.md
│   ├── Digital_News_Report_2023.md
│   ├── Digital_News_Report_2024.md
│   ├── Digital_News_Report_2025.md
│   └── Digital_News_Report_2026.md
└── data/
    ├── build_datasets_and_charts.py   # Script generazione CSV e grafici
    ├── csv/                           # Dataset puliti
    │   ├── indicators_over_time.csv
    │   ├── platforms_for_news.csv
    │   ├── brand_trust.csv
    │   └── press_freedom.csv
    └── charts/                        # Grafici per l'articolo
        ├── 01_trust_print_pay.png
        ├── 02_sources_of_news.png
        ├── 03_social_platforms.png
        ├── 04_emerging_platforms.png
        ├── 05_press_freedom.png
        ├── 06_brand_trust_heatmap.png
        ├── 07_share_and_podcast.png
        └── 08_snapshot_2021_vs_2026.png
```

## Dati

Tutti i dati sono estratti esclusivamente dalle sezioni Italia dei Digital News Report. I PDF originali non sono inclusi nel repository (materiale copyrightato Reuters Institute / YouGov).

Per riprodurre l'estrazione:
```bash
python3 extract_pdfs.py
```

Per rigenerare CSV e grafici:
```bash
python3 data/build_datasets_and_charts.py
```

## Indicatori tracciati (2021–2026)

- Fiducia complessiva nelle notizie
- Reach settimanale per fonte (TV, online, social, stampa)
- Uso delle piattaforme social per le notizie (Facebook, Instagram, WhatsApp, YouTube, TikTok, Telegram, Twitter/X)
- Fiducia nei singoli brand giornalistici (2023–2026)
- Libertà di stampa RSF (2023–2026)
- Pagamento per notizie online
- Condivisione notizie via social
- News avoidance
- Podcast e AI chatbot per le notizie

## Fonte primaria

Reuters Institute for the Study of Journalism — Digital News Report 2021–2026.  
Sezione Italia a cura di Alessio Cornia, Dublin City University.
