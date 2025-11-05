# 🚀 Quick Start Guide

Get Hungarian Truth News running in 5 minutes!

## ⚡ Super Fast Setup

### 1️⃣ Get Gemini API Key (2 minutes)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### 2️⃣ Configure GitHub Repository (2 minutes)

```bash
# Clone and push to your GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hungariantruth.git
git push -u origin main
```

### 3️⃣ Add Secret to GitHub (1 minute)

1. Go to your repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GEMINI_API_KEY`
4. Value: Paste your Gemini API key
5. Click "Add secret"

### 4️⃣ Enable GitHub Pages (1 minute)

1. Go to Settings → Pages
2. Source: **GitHub Actions**
3. Save

### 5️⃣ Run First Scrape

1. Go to Actions tab
2. Click "Daily News Synthesis"
3. Click "Run workflow" → "Run workflow"
4. Wait ~2 minutes

### 6️⃣ View Your Site

Visit: `https://YOUR_USERNAME.github.io/hungariantruth/`

🎉 **Done!** Your news site is live!

---

## 🛠️ Local Development

### Test Scraper Locally

```bash
# Setup
cd scraper
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY="your-key-here"

# Run scraper
python run_daily.py

# Test individual components
python test_scraper.py
```

### Run Website Locally

```bash
# Simple HTTP server
python3 -m http.server 8000

# Open browser
open http://localhost:8000
```

---

## 📝 Daily Operations

### Manual Trigger
- Go to Actions → Daily News Synthesis → Run workflow

### Check Status
- Actions tab shows all runs
- Green ✅ = Success
- Red ❌ = Failed (check logs)

### View Data
- Generated files in `data/` folder
- Format: `YYYY-MM-DD.json`

---

## 🔧 Common Tasks

### Add New News Source (RSS)

Edit `scraper/config_sources.json`:

```json
{
  "name": "New Source",
  "url": "newssite.hu",
  "type": "rss",
  "rss_url": "https://newssite.hu/rss"
}
```

### Add Custom Scraper

1. Create `scraper/sites/newssite.py`
2. Copy structure from `origo.py`
3. Update HTML selectors for the site
4. Add to `config_sources.json` with `"type": "custom"`

### Change Schedule

Edit `.github/workflows/daily-news.yml`:

```yaml
schedule:
  - cron: '0 4 * * *'  # 5 AM CET
```

### Customize Website

- **Colors**: Edit `assets/css/style.css` (`:root` variables)
- **Text**: Edit `index.html` and `archive.html`
- **Logic**: Edit `assets/js/app.js`

---

## 🐛 Troubleshooting

### "No articles collected"
- Check if news sites are accessible
- Verify RSS URLs are correct
- Check scraper logs in Actions

### "Gemini API error"
- Verify API key is correct
- Check API quota limits
- Wait a few minutes and retry

### "GitHub Pages not updating"
- Check Actions tab for errors
- Ensure Pages is enabled
- Try manual workflow trigger

### Website shows old news
- Hard refresh: Ctrl+F5 (Cmd+Shift+R on Mac)
- Check if new data file exists in `data/`
- Clear browser cache

---

## 💡 Tips & Tricks

### Test Before Committing
```bash
# Always test locally first
cd scraper
python test_scraper.py
```

### Monitor API Usage
- Gemini has free tier limits
- Check: https://makersuite.google.com/

### Backup Data
```bash
# Data files are in git, automatically backed up
git log -- data/
```

### Custom Domain
1. Buy domain
2. Add CNAME file to repo root
3. Configure in GitHub Pages settings

---

## 📊 Understanding the Data Flow

```
6:00 AM CET
    ↓
GitHub Actions triggers
    ↓
Python scraper runs
    ↓
Collects from 9 sources (RSS + custom)
    ↓
Sends to Gemini AI
    ↓
Generates neutral synthesis
    ↓
Saves to data/YYYY-MM-DD.json
    ↓
Commits to repository
    ↓
GitHub Pages rebuilds
    ↓
Website updated with new news
```

---

## 🎯 What's Next?

- ⭐ Star the repo if you like it
- 🐛 Report bugs via Issues
- 💡 Suggest features
- 🤝 Contribute improvements
- 📢 Share with others

---

## 📚 More Resources

- [Full README](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [License](LICENSE)

---

**Need help?** Open an issue on GitHub!

