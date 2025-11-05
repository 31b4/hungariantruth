# 📰 Hungarian Truth News

AI-powered unbiased news aggregator for Hungary.

## 🚀 Quick Start

### Run Locally
```bash
./run_local.sh
```

### Deploy to GitHub
1. Push to GitHub
2. Add GitHub Secret: `GEMINI_API_KEY` = `AIzaSyDW9LlCfH82IoX1QbDe7r2DmA2BNCPVnqI`
3. Settings → Pages → Source: **GitHub Actions**
4. Actions → Run workflow

Your site: `https://YOUR_USERNAME.github.io/hungariantruth/`

## 📁 Important Files

### Website
- `index.html` - Main page
- `archive.html` - Archive page
- `assets/css/style.css` - Styles
- `assets/js/app.js` - Main JavaScript
- `assets/js/archive.js` - Archive JavaScript

### Scraper (Python)
- `scraper/run_daily.py` - Main script (runs daily)
- `scraper/main.py` - News aggregator
- `scraper/rss_reader.py` - RSS parser
- `scraper/gemini_synthesis.py` - AI synthesis
- `scraper/config_sources.json` - News sources
- `scraper/sites/origo.py` - Custom scraper example

### Automation
- `.github/workflows/daily-news.yml` - Daily scraper (6 AM)
- `.github/workflows/pages.yml` - Website deployment

### Data
- `data/` - Daily news stored here (auto-generated)

## How It Works

1. **6 AM Daily**: GitHub Action runs `scraper/run_daily.py`
2. **Scrapes**: Gets news from 9 Hungarian sources (left/right/independent)
3. **AI Analysis**: Gemini compares all perspectives
4. **Synthesis**: Creates unbiased bilingual news
5. **Saves**: To `data/YYYY-MM-DD.json`
6. **Website**: Updates automatically with new news

## View Website Locally
```bash
python3 -m http.server 8000
# Open: http://localhost:8000
```

---

Made with ❤️ for truth in journalism

