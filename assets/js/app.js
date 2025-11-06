// =============================================
// Hungarian Truth News - Main JavaScript
// =============================================

// Language management
let currentLanguage = localStorage.getItem('language') || 'hu';

// Theme management
let currentTheme = localStorage.getItem('theme') || 'dark';

// =============================================
// Initialize on page load
// =============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initializeLanguage();
    initializeEventListeners();
    
    // Load content based on page
    if (document.querySelector('#news-container')) {
        loadTodayNews();
    }
});

// =============================================
// Theme Functions
// =============================================
function initializeTheme() {
    document.body.setAttribute('data-theme', currentTheme);
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
}

// =============================================
// Language Functions
// =============================================
function initializeLanguage() {
    updateLanguageButtons();
    updatePageLanguage();
}

function updateLanguageButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLanguage);
    });
}

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    updateLanguageButtons();
    updatePageLanguage();
    
    // Reload content if on main page
    if (document.querySelector('#news-container')) {
        displayNews(window.currentNewsData);
    }
}

function updatePageLanguage() {
    document.documentElement.lang = currentLanguage;
    
    // Update all translatable elements
    document.querySelectorAll('[data-hu][data-en]').forEach(element => {
        const text = element.getAttribute(`data-${currentLanguage}`);
        if (text) {
            if (element.tagName === 'INPUT') {
                element.placeholder = text;
            } else {
                element.textContent = text;
            }
        }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-placeholder-hu][data-placeholder-en]').forEach(element => {
        const text = element.getAttribute(`data-placeholder-${currentLanguage}`);
        if (text && element.tagName === 'INPUT') {
            element.placeholder = text;
        }
    });
}

// =============================================
// Event Listeners
// =============================================
function initializeEventListeners() {
    // Dark mode toggle
    const darkModeBtn = document.getElementById('dark-mode-toggle');
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', toggleTheme);
    }
    
    // Language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
    });
}

// =============================================
// News Loading Functions
// =============================================
async function loadTodayNews() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const newsContainer = document.getElementById('news-container');
    
    try {
        // Check URL parameters FIRST (for archive links) - this is the priority
        const urlParams = new URLSearchParams(window.location.search);
        const dateParam = urlParams.get('date');
        
        let data = null;
        let dateStr = null;
        
        // Priority 1: Date from URL parameter (archive clicks)
        if (dateParam) {
            dateStr = dateParam;
            data = await loadNewsData(dateParam);
            if (data) {
                // Successfully loaded the requested date
                window.currentNewsData = data;
                displayNews(data);
                loading.style.display = 'none';
                return;
            }
            // If date param exists but file not found, show error
            throw new Error(`News for ${dateParam} not found`);
        }
        
        // Priority 2: Today's news
        const today = new Date();
        dateStr = formatDate(today);
        data = await loadNewsData(dateStr);
        
        // Priority 3: Yesterday's news (fallback)
        if (!data) {
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            dateStr = formatDate(yesterday);
            data = await loadNewsData(dateStr);
        }
        
        if (data) {
            window.currentNewsData = data;
            displayNews(data);
            loading.style.display = 'none';
        } else {
            throw new Error('No news data available');
        }
        
    } catch (err) {
        console.error('Error loading news:', err);
        loading.style.display = 'none';
        error.style.display = 'block';
    }
}

async function loadNewsData(dateStr) {
    try {
        const response = await fetch(`data/${dateStr}.json`);
        if (!response.ok) return null;
        return await response.json();
    } catch (err) {
        console.error(`Failed to load ${dateStr}:`, err);
        return null;
    }
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDisplayDate(dateStr) {
    const date = new Date(dateStr);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    
    if (currentLanguage === 'hu') {
        return date.toLocaleDateString('hu-HU', options);
    } else {
        return date.toLocaleDateString('en-US', options);
    }
}

// =============================================
// News Display Functions
// =============================================
function displayNews(data) {
    const newsContainer = document.getElementById('news-container');
    const newsDate = document.getElementById('news-date');
    const methodologyContent = document.getElementById('methodology-content');
    
    if (!data || !data.stories) {
        console.error('Invalid news data');
        return;
    }
    
    // Display date
    if (newsDate) {
        newsDate.textContent = formatDisplayDate(data.date);
    }
    
    // Display stories
    newsContainer.innerHTML = '';
    data.stories.forEach((story, index) => {
        const storyElement = createStoryElement(story, index + 1);
        newsContainer.appendChild(storyElement);
    });
    
    // Display methodology
    if (methodologyContent) {
        const methodologyNote = currentLanguage === 'hu' 
            ? data.methodology_note_hu 
            : data.methodology_note_en;
        
        if (methodologyNote) {
            methodologyContent.innerHTML = `<p>${methodologyNote}</p>`;
        }
    }
}

function createStoryElement(story, number) {
    const article = document.createElement('article');
    article.className = 'news-story';
    
    const title = currentLanguage === 'hu' ? story.title_hu : story.title_en;
    const summary = currentLanguage === 'hu' ? story.summary_hu : story.summary_en;
    
    let html = `
        <div class="story-header">
            <div class="story-number">${currentLanguage === 'hu' ? 'Történet' : 'Story'} #${number}</div>
            <h2 class="story-title">${escapeHtml(title)}</h2>
        </div>
        
        <div class="story-summary">${escapeHtml(summary)}</div>
    `;
    
    // Add sources and key facts
    if (story.sources_analyzed || story.key_facts) {
        html += '<div class="story-meta">';
        
        if (story.sources_analyzed && story.sources_analyzed.length > 0) {
            html += `
                <div class="sources-list">
                    <div class="meta-title">${currentLanguage === 'hu' ? 'Elemzett források' : 'Sources Analyzed'}</div>
                    <div class="source-tags">
                        ${story.sources_analyzed.map(source => 
                            `<span class="source-tag">${escapeHtml(source)}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }
        
        if (story.key_facts && story.key_facts.length > 0) {
            html += `
                <div class="key-facts">
                    <div class="meta-title">${currentLanguage === 'hu' ? 'Kulcsfontosságú tények' : 'Key Facts'}</div>
                    <ul class="facts-list">
                        ${story.key_facts.map(fact => 
                            `<li>${escapeHtml(fact)}</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }
        
        html += '</div>';
    }
    
    // Add perspective comparison
    if (story.perspective_comparison) {
        html += `
            <div class="perspective-comparison">
                <div class="meta-title">${currentLanguage === 'hu' ? '🔍 Nézőpontok összehasonlítása' : '🔍 Perspective Comparison'}</div>
                <p>${escapeHtml(story.perspective_comparison)}</p>
            </div>
        `;
    }
    
    article.innerHTML = html;
    return article;
}

// =============================================
// Utility Functions
// =============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =============================================
// Export for use in other scripts
// =============================================
window.appUtils = {
    currentLanguage: () => currentLanguage,
    formatDate,
    formatDisplayDate,
    escapeHtml,
    loadNewsData
};

