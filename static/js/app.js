document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const resultsGrid = document.getElementById('resultsGrid');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (!query) return;

        // Reset UI
        resultsGrid.innerHTML = '';
        loading.style.display = 'block';
        errorMessage.style.display = 'none';

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Failed to fetch search results.');

            const data = await response.json();
            renderResults(data.results);
        } catch (err) {
            console.error(err);
            errorMessage.textContent = 'An error occurred while fetching data. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    });

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>"']/g, function(m) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }[m];
        });
    }

    function renderResults(results) {
        if (!results || results.length === 0) {
            resultsGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #8b949e;">No records found for this query.</div>';
            return;
        }

        resultsGrid.innerHTML = results.map(result => {
            const tagClass = getTagClass(result.source);
            const safeTitle = escapeHTML(result.title || 'Unknown Title');
            const safeDescription = truncate(escapeHTML(result.description || 'No description available.'), 150);
            const safeUrl = encodeURI(result.url || '#');
            const safeImage = result.image ? encodeURI(result.image) : null;

            return `
                <article class="card">
                    <div class="card-img-container">
                        ${safeImage ? `<img src="${safeImage}" alt="${safeTitle}" onerror="this.parentElement.innerHTML='<div style=\'color: #30363d; font-size: 3rem;\'>?</div>'">` : `<div style="color: #30363d; font-size: 3rem;">?</div>`}
                    </div>
                    <div class="card-content">
                        <span class="card-tag ${tagClass}">${escapeHTML(result.source)}</span>
                        <h3 class="card-title">${safeTitle}</h3>
                        <p class="card-description">${safeDescription}</p>
                    </div>
                    <div class="card-footer">
                        <a href="${safeUrl}" target="_blank" class="btn-view">VIEW DETAILS</a>
                    </div>
                </article>
            `;
        }).join('');
    }

    function getTagClass(source) {
        switch (source.toLowerCase()) {
            case 'fbi': return 'tag-fbi';
            case 'interpol': return 'tag-interpol';
            case 'web search': return 'tag-web';
            default: return '';
        }
    }

    function truncate(str, n) {
        return (str.length > n) ? str.substr(0, n - 1) + '&hellip;' : str;
    }
});
