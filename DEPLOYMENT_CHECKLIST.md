# 🚀 Deployment Checklist

Use this checklist to deploy Hungarian Truth News to production.

---

## ✅ Pre-Deployment Checklist

### Local Testing
- [ ] Python scraper runs without errors locally
- [ ] `test_scraper.py` passes all tests
- [ ] Website displays correctly in browser
- [ ] Dark mode works
- [ ] Language switching works
- [ ] Archive page loads
- [ ] No console errors in browser

### Code Review
- [ ] All files committed to git
- [ ] No sensitive data in code
- [ ] .gitignore configured properly
- [ ] README is complete and accurate
- [ ] Code is well-commented

---

## 🌐 GitHub Setup

### Repository Creation
- [ ] Created GitHub repository
- [ ] Repository is public (for GitHub Pages)
- [ ] Repository name is appropriate
- [ ] Description added
- [ ] Topics/tags added for discoverability

### Initial Push
```bash
# Run these commands:
- [ ] git init
- [ ] git add .
- [ ] git commit -m "Initial commit"
- [ ] git branch -M main
- [ ] git remote add origin https://github.com/YOUR_USERNAME/hungariantruth.git
- [ ] git push -u origin main
```

### Verify on GitHub
- [ ] All files visible on GitHub
- [ ] README displays correctly
- [ ] No sensitive files committed
- [ ] .github/workflows directory exists

---

## 🔑 API Configuration

### Gemini API Key
- [ ] Obtained from https://makersuite.google.com/app/apikey
- [ ] Tested locally with the key
- [ ] Key is active and working

### GitHub Secrets
- [ ] Navigate to: Settings → Secrets and variables → Actions
- [ ] Click "New repository secret"
- [ ] Name: `GEMINI_API_KEY`
- [ ] Value: Pasted correctly
- [ ] Secret saved successfully
- [ ] Secret name matches workflow exactly (case-sensitive!)

---

## 📄 GitHub Pages Setup

### Enable Pages
- [ ] Go to Settings → Pages
- [ ] Source: **GitHub Actions** (not branch!)
- [ ] Click Save
- [ ] Wait for confirmation message

### Custom Domain (Optional)
- [ ] Domain purchased
- [ ] DNS configured with CNAME
- [ ] CNAME file added to repo root
- [ ] SSL certificate active
- [ ] Domain verified in GitHub

---

## 🤖 GitHub Actions

### First Manual Run
- [ ] Go to Actions tab
- [ ] See workflows listed (should see 2: daily-news, pages)
- [ ] Click "Daily News Synthesis"
- [ ] Click "Run workflow" button
- [ ] Select "main" branch
- [ ] Click green "Run workflow" button
- [ ] Workflow starts running

### Monitor First Run
- [ ] Workflow shows as running (yellow dot)
- [ ] Click on the running workflow
- [ ] Watch logs in real-time
- [ ] No errors in logs
- [ ] Workflow completes successfully (green checkmark)
- [ ] New data file appears in `data/` folder
- [ ] New commit appears in repository

### Verify Output
- [ ] `data/YYYY-MM-DD.json` file created
- [ ] JSON file is valid (not empty)
- [ ] Contains stories array
- [ ] Contains metadata
- [ ] File size is reasonable (not 0 bytes)

---

## 🌍 Website Verification

### Access Site
- [ ] Visit: https://YOUR_USERNAME.github.io/hungariantruth/
- [ ] Page loads successfully
- [ ] No 404 errors
- [ ] No console errors

### Test All Features
- [ ] Today's news displays
- [ ] News stories show correctly
- [ ] Sources are listed
- [ ] Dark mode toggle works
- [ ] Language switch works (HU ↔ EN)
- [ ] Archive link works
- [ ] Archive page shows news
- [ ] Search works in archive
- [ ] Mobile view is responsive

### Cross-Browser Testing
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if on Mac)
- [ ] Mobile browser

---

## 📅 Automation Verification

### Schedule Check
- [ ] Cron schedule is correct: `0 5 * * *` = 6 AM CET
- [ ] Timezone is appropriate
- [ ] Workflow has correct permissions

### Wait for Automatic Run
- [ ] Wait until next day at 6 AM
- [ ] Check Actions tab
- [ ] Workflow ran automatically
- [ ] New data file created
- [ ] Website updated

---

## 🐛 Troubleshooting Steps

If something fails, check:

### Scraper Failures
- [ ] Check workflow logs in Actions
- [ ] Verify API key is set correctly
- [ ] Check if news sites are accessible
- [ ] Verify RSS URLs are still valid
- [ ] Check API rate limits

### Website Not Updating
- [ ] Check Pages deployment workflow
- [ ] Verify Pages is enabled
- [ ] Hard refresh browser (Ctrl+F5)
- [ ] Check browser console for errors
- [ ] Verify JSON files are valid

### API Issues
- [ ] Check Gemini API dashboard
- [ ] Verify API key is active
- [ ] Check rate limits
- [ ] Review API usage

---

## 📊 Post-Deployment Monitoring

### First Week
- [ ] Day 1: Verify automatic run
- [ ] Day 2: Check data accumulation
- [ ] Day 3: Test archive functionality
- [ ] Day 7: Review logs for patterns

### Ongoing
- [ ] Weekly: Check workflow success rate
- [ ] Monthly: Review API usage
- [ ] Monthly: Verify all sources still work
- [ ] Quarterly: Update sources if needed

---

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Workflow runs daily without errors
- ✅ New data file created each day
- ✅ Website updates automatically
- ✅ All features work correctly
- ✅ No console errors
- ✅ Mobile responsive
- ✅ Both languages work
- ✅ Archive grows daily

---

## 📝 Post-Launch Tasks

### Documentation
- [ ] Update README with live URL
- [ ] Add screenshots
- [ ] Create demo video (optional)
- [ ] Write blog post (optional)

### Community
- [ ] Add topics/tags to repo
- [ ] Share on social media
- [ ] Submit to awesome lists
- [ ] Engage with users

### Maintenance
- [ ] Set up GitHub notifications
- [ ] Monitor Issues
- [ ] Review Pull Requests
- [ ] Keep dependencies updated

---

## 🆘 Emergency Contacts

If you need help:
1. **Check Logs**: Actions → Latest run → View logs
2. **Search Issues**: Check if others had similar problems
3. **Create Issue**: Describe problem with logs
4. **Community**: Share in relevant forums

---

## 🎉 Launch Announcement Template

Ready to announce? Use this template:

```
🚀 Excited to launch Hungarian Truth News!

An AI-powered news aggregator that:
✅ Scrapes 9+ Hungarian news sources daily
✅ Uses AI to create unbiased synthesis
✅ Compares left, right, and independent perspectives
✅ Fully automated via GitHub Actions
✅ Free and open source

Check it out: https://YOUR_USERNAME.github.io/hungariantruth/
Source code: https://github.com/YOUR_USERNAME/hungariantruth

#News #AI #OpenSource #Hungary #Journalism
```

---

## ✅ Final Checklist

Before announcing:
- [ ] Everything works perfectly
- [ ] At least 3-5 days of data
- [ ] Documentation is complete
- [ ] No known bugs
- [ ] Screenshots/demo ready
- [ ] Announcement written
- [ ] Ready for feedback

---

**🎊 Congratulations on your deployment!**

Remember: It's okay if not everything is perfect. You can iterate and improve over time!

