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
        // Get list of dates from index.json (fastest method)
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
        
        // Create archive items immediately (don't wait for story counts)
        archiveData = dataFiles.map(dateStr => ({
            date: dateStr,
            displayDate: window.appUtils.formatDisplayDate(dateStr),
            storyCount: null, // Will load lazily
            data: null
        })).sort((a, b) => new Date(b.date) - new Date(a.date));
        
        filteredArchive = [...archiveData];
        displayArchive();
        loading.style.display = 'none';
        
        // Load story counts in background (non-blocking)
        loadStoryCountsInBackground();
        
    } catch (err) {
        console.error('Error loading archive:', err);
        loading.style.display = 'none';
    }
}

// Load story counts in background without blocking display
async function loadStoryCountsInBackground() {
    const promises = archiveData.map(async (item) => {
        try {
            const response = await fetch(`data/${item.date}.json`, { cache: 'no-cache' });
            if (response.ok) {
                const data = await response.json();
                item.storyCount = data.stories ? data.stories.length : 0;
                // Update the display for this item
                updateArchiveItemCount(item);
            }
        } catch (err) {
            item.storyCount = 0;
        }
    });
    
    await Promise.all(promises);
}

function updateArchiveItemCount(item) {
    const archiveList = document.getElementById('archive-list');
    if (!archiveList) return;
    
    // Find and update the specific item
    const items = archiveList.querySelectorAll('.archive-item');
    items.forEach((element, index) => {
        if (archiveData[index] === item) {
            const countElement = element.querySelector('.archive-story-count');
            if (countElement && item.storyCount !== null) {
                const storyCountText = currentLanguage === 'hu'
                    ? `${item.storyCount} történet`
                    : `${item.storyCount} ${item.storyCount === 1 ? 'story' : 'stories'}`;
                countElement.textContent = storyCountText;
            }
        }
    });
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
    div.href = `index.html?date=${item.date}`;
    
    const storyCountText = item.storyCount !== null
        ? (currentLanguage === 'hu'
            ? `${item.storyCount} történet`
            : `${item.storyCount} ${item.storyCount === 1 ? 'story' : 'stories'}`)
        : (currentLanguage === 'hu' ? 'Betöltés...' : 'Loading...');
    
    div.innerHTML = `
        <div class="archive-date">${window.appUtils.escapeHtml(item.displayDate)}</div>
        <div class="archive-story-count">${storyCountText}</div>
    `;
    
    return div;
}


// =============================================
// Search Functionality
// =============================================
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            // Debounce search to avoid too many requests
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterArchive(query);
            }, 300);
        });
    }
}

async function filterArchive(query) {
    if (!query) {
        filteredArchive = [...archiveData];
        displayArchive();
        return;
    }
    
    // Filter by date first (fast)
    filteredArchive = archiveData.filter(item => {
        return item.displayDate.toLowerCase().includes(query) ||
               item.date.includes(query);
    });
    
    // If we have results, load data for those items to search in content
    if (filteredArchive.length > 0 && filteredArchive.length <= 10) {
        // Load data for filtered items to search in content
        const searchPromises = filteredArchive.map(async (item) => {
            if (!item.data) {
                try {
                    const data = await window.appUtils.loadNewsData(item.date);
                    item.data = data;
                } catch (err) {
                    // Ignore errors
                }
            }
            return item;
        });
        
        await Promise.all(searchPromises);
        
        // Now filter by content
        filteredArchive = filteredArchive.filter(item => {
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

