// AJAX Pagination and filters
function loadPage(page, event = null) {
    const category = document.getElementById('categoryFilter').value;
    const tags = Array.from(document.getElementById('tagFilter').selectedOptions).map(option => option.value);
    const players = Array.from(document.getElementById('playerFilter').selectedOptions).map(option => option.value);
    const soldBy = document.getElementById('soldByFilter').value;
    const sort = document.getElementById('sortFilter').value;
    const order = document.querySelector('#sortFilter option:checked').dataset.order || 'asc';
    const searchQuery = document.getElementById('searchInput').value;

    fetch(`/?page=${page}&category=${category}&tags=${tags.join(',')}&players=${players.join(',')}&sold_by=${soldBy}&sort=${sort}&order=${order}&search=${searchQuery}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.product_list && data.pagination) {
            document.getElementById('productList').innerHTML = data.product_list;
            document.getElementById('paginationControlsTop').innerHTML = data.pagination;
            document.getElementById('paginationControlsBottom').innerHTML = data.pagination;
            document.getElementById('productCount').innerHTML = `Products found: <b>${data.total_count}</b>`;
        } else {
            console.error('Could not find product list or pagination controls in the response.');
        }
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
}

document.getElementById('categoryFilter').addEventListener('change', function() {
    loadPage(1);
});

document.getElementById('tagFilter').addEventListener('change', function() {
    loadPage(1);
});

document.getElementById('playerFilter').addEventListener('change', function() {
    loadPage(1);
});

document.getElementById('soldByFilter').addEventListener('change', function() {
    loadPage(1);
});

document.getElementById('sortFilter').addEventListener('change', function() {
    loadPage(1);
});

document.getElementById('searchInput').addEventListener('input', function() {
    loadPage(1);
});

// Handle clearing filters
document.getElementById('clearTagFilter').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('tagFilter').selectedIndex = -1; // Deselect all options
    loadPage(1);
});

document.getElementById('clearPlayerFilter').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('playerFilter').selectedIndex = -1; // Deselect all options
    loadPage(1);
});
