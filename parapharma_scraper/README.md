# Parapharma Scraper

Ce projet permet de scraper les données du site https://parapharma.ma

## Structure du projet

```
parapharma_scraper/
│
├── scrapers/
│   └── parapharma.py     # Scraper pour https://parapharma.ma
│
├── data/
│   └── logs/            # Logs des scrapes
│
├── config/
│   └── sites.json       # Configuration multi-sites
│
├── utils/
│   └── mongo.py         # Connexion MongoDB
│
├── main.py              # Lancement du scraping
├── requirements.txt     # Dépendances Python
└── README.md           # Ce fichier
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py
```

## Configuration

Modifiez le fichier `config/sites.json` pour configurer les sites à scraper.
