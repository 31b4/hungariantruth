# 📰 Magyar Igazság Hírek | Hungarian Truth News

**Objektív, pártatlan hírek Magyarország számára**  
*Objective, unbiased news for Hungary*

---

## 🎯 Projekt Célja | Project Goal

Ez a projekt célja egy AI-alapú híraggregátor létrehozása, amely:
- Naponta reggel 6 órakor automatikusan összegyűjti a magyar hírportálok híreit
- Elemzi a jobboldali, baloldali és független forrásokat
- Google Gemini AI segítségével semleges, tényalapú szintézist készít
- Kétnyelvű (magyar/angol) statikus weboldalon jeleníti meg
- Teljes mértékben ingyenes és nyílt forráskódú

This project aims to create an AI-powered news aggregator that:
- Automatically collects news from Hungarian portals daily at 6 AM
- Analyzes right-wing, left-wing, and independent sources
- Creates neutral, fact-based synthesis using Google Gemini AI
- Displays on a bilingual (Hungarian/English) static website
- Completely free and open source

---

## 🏗️ Architektúra | Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions                         │
│              (Runs daily at 6 AM CET)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Python News Scraper                         │
│  • RSS Feeds (Telex, HVG, Index, etc.)                  │
│  • Custom Scrapers (Origo, etc.)                         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Google Gemini AI                            │
│  • Analyzes all perspectives                            │
│  • Generates neutral synthesis                          │
│  • Bilingual output (HU/EN)                             │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              JSON Storage (data/)                        │
│  • One file per day (YYYY-MM-DD.json)                   │
│  • Historical archive                                   │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Pages                                │
│  • Static HTML/CSS/JS website                           │
│  • Bilingual interface                                  │
│  • Search & archive features                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Gyors Indítás | Quick Start

### 1. Repository Klónozása | Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/hungariantruth.git
cd hungariantruth
```

### 2. Gemini API Kulcs Beszerzése | Get Gemini API Key

1. Menj a [Google AI Studio](https://makersuite.google.com/app/apikey) oldalra
2. Jelentkezz be Google fiókkal
3. Kattints a "Create API Key" gombra
4. Másold ki a kulcsot

### 3. GitHub Secrets Beállítása | Configure GitHub Secrets

1. Menj a GitHub repository Settings oldalára
2. Navigálj a **Security** > **Secrets and variables** > **Actions** menüponthoz
3. Kattints a **New repository secret** gombra
4. Név: `GEMINI_API_KEY`
5. Érték: Illeszd be a Gemini API kulcsot
6. Kattints a **Add secret** gombra

### 4. GitHub Pages Engedélyezése | Enable GitHub Pages

1. Menj a repository **Settings** oldalára
2. Navigálj a **Pages** menüponthoz
3. Source: **GitHub Actions**
4. Mentsd el

### 5. Tesztelés | Testing

Manuálisan indítsd el a workflow-t:
1. Menj a **Actions** fülre
2. Válaszd ki a **Daily News Synthesis** workflow-t
3. Kattints a **Run workflow** gombra

---

## 📁 Projekt Struktúra | Project Structure

```
hungariantruth/
├── .github/
│   └── workflows/
│       ├── daily-news.yml      # Daily scraping workflow
│       └── pages.yml            # GitHub Pages deployment
├── data/
│   └── YYYY-MM-DD.json          # Daily news data files
├── scraper/
│   ├── sites/
│   │   ├── __init__.py
│   │   └── origo.py             # Custom site scrapers
│   ├── __init__.py
│   ├── config_sources.json      # News sources configuration
│   ├── gemini_synthesis.py      # Gemini AI integration
│   ├── main.py                  # Main scraper orchestrator
│   ├── requirements.txt         # Python dependencies
│   ├── rss_reader.py            # RSS feed parser
│   └── run_daily.py             # Daily execution script
├── assets/
│   ├── css/
│   │   └── style.css            # Website styles
│   └── js/
│       ├── app.js               # Main JavaScript
│       └── archive.js           # Archive page logic
├── index.html                   # Main page
├── archive.html                 # Archive page
├── magyar_hirportalok.csv       # List of Hungarian news sources
├── .gitignore
└── README.md
```

---

## 🔧 Konfiguráció | Configuration

### Hírek Forrásai | News Sources

A `scraper/config_sources.json` fájl tartalmazza az összes hírf forrást:

```json
{
  "sources": {
    "right_wing": [...],   // Jobboldali források
    "left_wing": [...],    // Baloldali források
    "independent": [...]   // Független források
  }
}
```

**Új forrás hozzáadása | Adding a new source:**

```json
{
  "name": "Forrás Neve",
  "url": "example.hu",
  "type": "rss",                    // vagy "custom"
  "rss_url": "https://example.hu/rss"
}
```

### Ütemezés Módosítása | Modify Schedule

A `.github/workflows/daily-news.yml` fájlban:

```yaml
schedule:
  - cron: '0 5 * * *'  # 6 AM CET (5 AM UTC)
```

Cron szintaxis:
- `0 5 * * *` - Minden nap 5:00 UTC-kor (6:00 CET)
- `0 4,14 * * *` - Naponta kétszer: 5:00 és 15:00 CET-kor

---

## 🛠️ Helyi Fejlesztés | Local Development

### Python Környezet Beállítása | Setup Python Environment

```bash
cd scraper
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# vagy
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Scraper Tesztelése | Test Scraper

```bash
export GEMINI_API_KEY="your-api-key-here"
python run_daily.py
```

### Weboldal Helyi Futtatása | Run Website Locally

```bash
# Egyszerű HTTP szerver
python3 -m http.server 8000

# Vagy használj bármilyen más local server-t
# npx serve
# php -S localhost:8000
```

Nyisd meg: `http://localhost:8000`

---

## 📊 Adatformátum | Data Format

Minden napi JSON fájl (`data/YYYY-MM-DD.json`) struktúrája:

```json
{
  "date": "2025-11-05",
  "stories": [
    {
      "title_hu": "Magyar cím",
      "title_en": "English title",
      "summary_hu": "Magyar összefoglaló...",
      "summary_en": "English summary...",
      "sources_analyzed": ["Origo", "Telex", "HVG"],
      "perspective_comparison": "Nézőpontok összehasonlítása...",
      "key_facts": ["Tény 1", "Tény 2", "Tény 3"]
    }
  ],
  "methodology_note_hu": "Módszertan leírása magyarul",
  "methodology_note_en": "Methodology description in English",
  "metadata": {
    "sources_scraped": 9,
    "generation_time": "2025-11-05T06:00:00",
    "ai_model": "gemini-pro"
  }
}
```

---

## 🎨 Weboldal Funkciók | Website Features

### ✨ Főbb jellemzők | Main Features

- **🌓 Dark Mode**: Sötét/világos téma váltás
- **🌍 Bilingual**: Magyar/angol nyelvváltás
- **📱 Responsive**: Mobil-barát design
- **🔍 Search**: Keresés az archívumban
- **📅 Archive**: Korábbi napok hírein böngészés
- **⚡ Fast**: Statikus oldal, gyors betöltés

### 🎯 Használat | Usage

1. **Mai hírek megtekintése**: `index.html`
2. **Archívum böngészése**: `archive.html`
3. **Keresés**: Írd be a keresendő szót az archívum oldalon
4. **Nyelv váltás**: Kattints a HU/EN gombra
5. **Téma váltás**: Kattints a ☀️/🌙 ikonra

---

## 🔐 Biztonság | Security

### API Kulcsok Kezelése | API Key Management

- ❌ **SOHA** ne commitold az API kulcsot a repository-ba
- ✅ Használj GitHub Secrets-et
- ✅ Az API kulcs csak GitHub Actions-ben fut
- ✅ Weboldal teljesen publikus, nincs API kulcs szükség

### Adatvédelem | Privacy

- Nincs felhasználói követés
- Nincs cookie használat
- Nincs analytics
- Nyílt forráskódú és transzparens

---

## 🤝 Közreműködés | Contributing

Szívesen látunk hozzájárulásokat!

1. Fork-old a repository-t
2. Készíts egy feature branch-et (`git checkout -b feature/NewFeature`)
3. Commit-old a változásokat (`git commit -m 'Add NewFeature'`)
4. Push-old a branch-et (`git push origin feature/NewFeature`)
5. Nyiss egy Pull Request-et

### Fejlesztési ötletek | Development Ideas

- [ ] Több egyedi scraper hozzáadása
- [ ] Sentiment analysis integráció
- [ ] Trend vizualizáció
- [ ] Email értesítések
- [ ] PWA support
- [ ] RSS feed generálás

---

## 📝 Licensz | License

MIT License - lásd a `LICENSE` fájlt.

---

## 🙏 Köszönetnyilvánítás | Acknowledgments

- **Google Gemini**: AI szintézis
- **GitHub**: Hosting és automation
- **Összes magyar hírportál**: Forrás szolgáltatás

---

## 📧 Kapcsolat | Contact

Ha kérdésed van, nyiss egy Issue-t a GitHub-on.

---

## ⚠️ Disclaimer | Jogi nyilatkozat

Ez a projekt kísérleti jellegű és oktatási célokat szolgál. A hírek összefoglalása AI által generált, és lehet, hogy nem 100%-ban pontos. Mindig ellenőrizd az eredeti forrásokat.

This project is experimental and for educational purposes. News summaries are AI-generated and may not be 100% accurate. Always verify with original sources.

---

**🌟 Ha tetszik a projekt, adj neki egy csillagot! | If you like this project, give it a star!**

