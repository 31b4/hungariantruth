// =============================================
// Archive Page JavaScript
// =============================================

let archiveData = [];
let filteredArchive = [];

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#archive-list')) {
        loadArchive();
        initializeSearch();
    }
});

// =============================================
// Archive Loading
// =============================================
async function loadArchive() {
    const loading = document.getElementById('loading');
    const archiveList = document.getElementById('archive-list');
    
    try {
        // Scan for available data files
        const dataFiles = await discoverDataFiles();
        
        if (dataFiles.length === 0) {
            archiveList.innerHTML = `
                <div class="no-archive">
                    <p>${currentLanguage === 'hu' 
                        ? 'Még nincs elérhető archívum.' 
                        : 'No archive available yet.'}</p>
                </div>
            `;
            loading.style.display = 'none';
            return;
        }
        
        // Load archive data in parallel (all at once is fine for small datasets)
        const archivePromises = dataFiles.map(async (dateStr) => {
            try {
                const data = await window.appUtils.loadNewsData(dateStr);
                if (data) {
                    return {
                        date: dateStr,
                        displayDate: window.appUtils.formatDisplayDate(dateStr),
                        storyCount: data.stories ? data.stories.length : 0,
                        data: data
                    };
                }
            } catch (err) {
                console.warn(`Failed to load ${dateStr}:`, err);
            }
            return null;
        });
        
        archiveData = (await Promise.all(archivePromises))
            .filter(item => item !== null)
            .sort((a, b) => new Date(b.date) - new Date(a.date));
        
        filteredArchive = [...archiveData];
        displayArchive();
        loading.style.display = 'none';
        
    } catch (err) {
        console.error('Error loading archive:', err);
        loading.style.display = 'none';
    }
}

// =============================================
// Discover Available Data Files
// =============================================
async function discoverDataFiles() {
    // First, try to load index.json (fastest method)
    try {
        const response = await fetch('data/index.json', { cache: 'no-cache' });
        if (response.ok) {
            const index = await response.json();
            if (index.available_dates && index.available_dates.length > 0) {
                return index.available_dates;
            }
        }
    } catch (err) {
        console.log('Index file not found, falling back to discovery');
    }
    
    // Fallback: Check files manually (slower but works if index doesn't exist)
    const files = [];
    const today = new Date();
    const daysToCheck = 30; // Reduced from 60 for faster loading
    
    // Create all date strings first
    const datesToCheck = [];
    for (let i = 0; i < daysToCheck; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        datesToCheck.push(window.appUtils.formatDate(date));
    }
    
    // Check files in parallel batches (10 at a time)
    const batchSize = 10;
    for (let i = 0; i < datesToCheck.length; i += batchSize) {
        const batch = datesToCheck.slice(i, i + batchSize);
        
        const batchPromises = batch.map(async (dateStr) => {
            try {
                const response = await fetch(`data/${dateStr}.json`, { 
                    method: 'HEAD',
                    cache: 'no-cache'
                });
                return response.ok ? dateStr : null;
            } catch (err) {
                return null;
            }
        });
        
        const batchResults = await Promise.all(batchPromises);
        files.push(...batchResults.filter(f => f !== null));
    }
    
    return files;
}

// =============================================
// Display Archive
// =============================================
function displayArchive() {
    const archiveList = document.getElementById('archive-list');
    
    if (filteredArchive.length === 0) {
        archiveList.innerHTML = `
            <div class="no-results">
                <p>${currentLanguage === 'hu' 
                    ? 'Nincs találat a keresésre.' 
                    : 'No results found.'}</p>
            </div>
        `;
        return;
    }
    
    archiveList.innerHTML = '';
    
    filteredArchive.forEach(item => {
        const archiveItem = createArchiveItem(item);
        archiveList.appendChild(archiveItem);
    });
}

function createArchiveItem(item) {
    const div = document.createElement('a');
    div.className = 'archive-item';
    div.href = `?date=${item.date}`;
    
    const storyCountText = currentLanguage === 'hu'
        ? `${item.storyCount} történet`
        : `${item.storyCount} ${item.storyCount === 1 ? 'story' : 'stories'}`;
    
    div.innerHTML = `
        <div class="archive-date">${window.appUtils.escapeHtml(item.displayDate)}</div>
        <div class="archive-story-count">${storyCountText}</div>
    `;
    
    // Override default link behavior to load inline
    div.addEventListener('click', (e) => {
        e.preventDefault();
        loadArchiveDate(item.date, item.data);
    });
    
    return div;
}

// =============================================
// Load Specific Archive Date
// =============================================
function loadArchiveDate(dateStr, data) {
    // Store the data and redirect to index page
    sessionStorage.setItem('archiveDate', dateStr);
    sessionStorage.setItem('archiveData', JSON.stringify(data));
    window.location.href = 'index.html?from=archive';
}

// Check if we're loading from archive on index page
if (window.location.search.includes('from=archive')) {
    const archiveDate = sessionStorage.getItem('archiveDate');
    const archiveData = sessionStorage.getItem('archiveData');
    
    if (archiveData) {
        try {
            window.currentNewsData = JSON.parse(archiveData);
            setTimeout(() => {
                if (window.currentNewsData) {
                    displayNews(window.currentNewsData);
                    document.getElementById('loading').style.display = 'none';
                }
            }, 100);
            
            // Clear session storage
            sessionStorage.removeItem('archiveDate');
            sessionStorage.removeItem('archiveData');
        } catch (err) {
            console.error('Error loading archive data:', err);
        }
    }
}

// =============================================
// Search Functionality
// =============================================
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            filterArchive(query);
        });
    }
}

function filterArchive(query) {
    if (!query) {
        filteredArchive = [...archiveData];
    } else {
        filteredArchive = archiveData.filter(item => {
            // Search in date
            if (item.displayDate.toLowerCase().includes(query)) {
                return true;
            }
            
            // Search in story titles and summaries
            if (item.data && item.data.stories) {
                return item.data.stories.some(story => {
                    const titleHu = (story.title_hu || '').toLowerCase();
                    const titleEn = (story.title_en || '').toLowerCase();
                    const summaryHu = (story.summary_hu || '').toLowerCase();
                    const summaryEn = (story.summary_en || '').toLowerCase();
                    
                    return titleHu.includes(query) || 
                           titleEn.includes(query) ||
                           summaryHu.includes(query) ||
                           summaryEn.includes(query);
                });
            }
            
            return false;
        });
    }
    
    displayArchive();
}

