document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const searchContainer = document.getElementById('search-container');
    const resultsContainer = document.getElementById('results-container');
    const queryInfo = document.getElementById('query-info');
    const resultsTable = document.getElementById('results-table');

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Move search bar to top
        searchContainer.classList.add('top');
        resultsContainer.style.display = 'block';

        // Show loading
        queryInfo.innerHTML = '<div class="loading">Searching...</div>';
        resultsTable.innerHTML = '';

        // Fetch results
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
                queryInfo.innerHTML = '<div class="error">Error occurred while searching. Please try again.</div>';
            });
    }

    function displayResults(data) {
        // Display query info
        queryInfo.innerHTML = `
            <h3>Search Results</h3>
            <p><strong>Query:</strong> ${data.query}</p>
            <p><strong>Applied Filters:</strong> ${JSON.stringify(data.applied_filters, null, 2)}</p>
            <p><strong>Total Results:</strong> ${data.total_results}</p>
            <p><strong>Returned Results:</strong> ${data.returned_results}</p>
            <p><strong>Timestamp:</strong> ${data.timestamp}</p>
            ${data.non_matched_columns.length > 0 ? `<p><strong>Non-matched Columns:</strong> ${data.non_matched_columns.join(', ')}</p>` : ''}
        `;

        // Display results table
        if (data.results && data.results.length > 0) {
            const columns = Object.keys(data.results[0]);
            let tableHTML = '<table><thead><tr>';
            columns.forEach(col => {
                tableHTML += `<th>${col}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';

            data.results.forEach(car => {
                tableHTML += '<tr>';
                columns.forEach(col => {
                    tableHTML += `<td>${car[col]}</td>`;
                });
                tableHTML += '</tr>';
            });

            tableHTML += '</tbody></table>';
            resultsTable.innerHTML = tableHTML;
        } else {
            resultsTable.innerHTML = '<p>No results found.</p>';
        }
    }

    // Event listeners
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});