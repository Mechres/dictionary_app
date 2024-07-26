document.addEventListener('DOMContentLoaded', () => {
    const searchWord = document.getElementById('search-word');
    const searchCategory = document.getElementById('search-category');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    const loginButton = document.getElementById('login-button');
    const registerButton = document.getElementById('register-button');
    const logoutButton = document.getElementById('logout-button');
    const addWordButton = document.getElementById('add-word-button');
    const addWordContainer = document.getElementById('add-word-container');

    let currentPage = 1;
    let totalPages = 1;

    const search = async (page = 1) => {
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: searchWord.value,
                    category: searchCategory.value,
                    page: page
                })
            });
            const data = await response.json();
            if (data.error) {
                showMessage(data.error, 'error');
            } else {
                displayResults(data.results);
                updatePagination(page, data.total_pages);
            }
        } catch (error) {
            console.error('Error searching:', error);
            showMessage('An error occurred while searching. Please try again.', 'error');
        }
    };

    const displayResults = (results) => {
        resultsContainer.innerHTML = results.map(result => `
            <div class="result-item">
                <strong>${result.word}</strong> (${result.language}): ${result.meaning} - ${result.category}
            </div>
        `).join('');
    };

    const updatePagination = (page, total) => {
        currentPage = page;
        totalPages = total;
        pageInfo.textContent = `Page ${page} of ${total}`;
        prevPageButton.disabled = page === 1;
        nextPageButton.disabled = page === total;
    };

    const showMessage = (message, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    };

    searchButton.addEventListener('click', () => search());
    prevPageButton.addEventListener('click', () => search(currentPage - 1));
    nextPageButton.addEventListener('click', () => search(currentPage + 1));

loginButton.addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });
        const data = await response.json();
        if (data.login) {
            loginButton.style.display = 'none';
            registerButton.style.display = 'none';
            logoutButton.style.display = 'inline-block';
            if (data.is_admin) {
                document.getElementById('admin-button').style.display = 'inline-block';
            }
            showMessage('Logged in successfully', 'success');
        } else {
            showMessage('Invalid username or password', 'error');
        }
    } catch (error) {
        console.error('Error logging in:', error);
        showMessage('An error occurred while logging in. Please try again.', 'error');
    }
});
    document.getElementById('admin-button').addEventListener('click', () => {
        window.location.href = '/admin';
    });
    registerButton.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password
                })
            });
            const data = await response.json();
            showMessage(data.message, data.error ? 'error' : 'success');
        } catch (error) {
            console.error('Error registering:', error);
            showMessage('An error occurred while registering. Please try again.', 'error');
        }
    });

    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/logout', { method: 'POST' });
            const data = await response.json();
            if (data.logout) {
                addWordContainer.style.display = 'none';
                loginButton.style.display = 'inline-block';
                registerButton.style.display = 'inline-block';
                logoutButton.style.display = 'none';
                showMessage('Logged out successfully', 'success');
            }
        } catch (error) {
            console.error('Error logging out:', error);
            showMessage('An error occurred while logging out. Please try again.', 'error');
        }
    });

    addWordButton.addEventListener('click', async () => {
        const word = document.getElementById('new-word').value;
        const language = document.getElementById('new-word-language').value;
        const meaning = document.getElementById('new-word-meaning').value;
        const category = document.getElementById('new-word-category').value;
        try {
            const response = await fetch('/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: word,
                    language: language,
                    meaning: meaning,
                    category: category
                })
            });
            const data = await response.json();
            if (data.error) {
                showMessage(data.error, 'error');
            } else {
                showMessage(data.message, 'success');
                // Clear form fields after successful addition
                document.getElementById('new-word').value = '';
                document.getElementById('new-word-language').value = '';
                document.getElementById('new-word-meaning').value = '';
                document.getElementById('new-word-category').value = '';
                // Refresh the search results
                search();
            }
        } catch (error) {
            console.error('Error adding word:', error);
            showMessage('An error occurred while adding the word. Please try again.', 'error');
        }
        
    });

});