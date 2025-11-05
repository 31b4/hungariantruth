# Contributing to Hungarian Truth News

Thank you for considering contributing to Hungarian Truth News! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Add new news source scrapers
- 🎨 Improve the website design
- 🌍 Improve translations

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/hungariantruth.git
   cd hungariantruth
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Test your changes**
6. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of your changes"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

## 📋 Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add error handling

### JavaScript
- Use modern ES6+ syntax
- Add comments for complex logic
- Keep functions pure when possible
- Use meaningful variable names

### HTML/CSS
- Use semantic HTML
- Keep CSS organized and commented
- Ensure responsive design
- Test on multiple browsers

## 🧪 Testing

Before submitting a PR:

1. **Test the scraper locally**
   ```bash
   cd scraper
   export GEMINI_API_KEY="your-key"
   python run_daily.py
   ```

2. **Test the website locally**
   ```bash
   python3 -m http.server 8000
   # Visit http://localhost:8000
   ```

3. **Check for errors in browser console**

## 🔧 Adding a New News Source

To add a new Hungarian news source:

1. **Determine if it has an RSS feed**
   - If yes: Add to `scraper/config_sources.json`
   - If no: Create a custom scraper

2. **For RSS feeds:**
   ```json
   {
     "name": "Source Name",
     "url": "example.hu",
     "type": "rss",
     "rss_url": "https://example.hu/rss"
   }
   ```

3. **For custom scrapers:**
   - Create `scraper/sites/sourcename.py`
   - Implement scraper class following the pattern in `origo.py`
   - Add to `config_sources.json` with `"type": "custom"`

4. **Test thoroughly**
   - Ensure it returns standardized format
   - Handle errors gracefully
   - Respect robots.txt

## 📝 Commit Message Guidelines

Use clear and meaningful commit messages:

- `Add: new feature or file`
- `Fix: bug fix`
- `Update: changes to existing feature`
- `Refactor: code restructuring`
- `Docs: documentation changes`
- `Style: formatting changes`

Example: `Add: custom scraper for 24.hu`

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Screenshots**: If applicable
6. **Environment**: Browser, OS, Python version

## 💡 Suggesting Features

When suggesting features:

1. **Use case**: Explain why this feature is needed
2. **Proposed solution**: Describe how it could work
3. **Alternatives**: Other approaches considered
4. **Examples**: Links to similar implementations

## ✅ Pull Request Checklist

Before submitting:

- [ ] Code follows the project's style guidelines
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed
- [ ] Tested locally and works
- [ ] No unnecessary files included
- [ ] Commit messages are clear
- [ ] PR description explains the changes

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

## 📧 Questions?

If you have questions:
- Open an issue with the `question` label
- Check existing issues first

## 🙏 Thank You!

Every contribution helps make this project better. Thank you for your time and effort!

