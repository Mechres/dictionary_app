document.addEventListener('DOMContentLoaded', () => {
    const addWordForm = document.getElementById('add-word-form');

    addWordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const word = document.getElementById('new-word').value;
        const language = document.getElementById('new-word-language').value;
        const meaning = document.getElementById('new-word-meaning').value;
        const category = document.getElementById('new-word-category').value;

        try {
            const response = await fetch('/admin/add_word', {
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
                showNotification(data.error, 'error');
            } else {
                showNotification('Word added successfully', 'success');
                addWordForm.reset();
                refreshWordList();
            }
        } catch (error) {
            console.error('Error adding word:', error);
            showNotification('An error occurred while adding the word. Please try again.', 'error');
        }
    });
});

async function editWord(id) {
    const row = event.target.closest('tr');
    const word = row.cells[1].innerText;
    const language = row.cells[2].innerText;
    const meaning = row.cells[3].innerText;
    const category = row.cells[4].innerText;

    const newWord = prompt('Enter new word:', word);
    const newLanguage = prompt('Enter new language:', language);
    const newMeaning = prompt('Enter new meaning:', meaning);
    const newCategory = prompt('Enter new category:', category);

    if (newWord && newLanguage && newMeaning && newCategory) {
        try {
            const response = await fetch('/admin/edit_word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    word: newWord,
                    language: newLanguage,
                    meaning: newMeaning,
                    category: newCategory
                })
            });
            const data = await response.json();
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                showNotification('Word updated successfully', 'success');
                refreshWordList();
            }
        } catch (error) {
            console.error('Error updating word:', error);
            showNotification('An error occurred while updating the word. Please try again.', 'error');
        }
    }
}
    function showTab(tabName) {
      // Hide all sections
      document.getElementById('users-section').style.display = 'none';
      document.getElementById('words-section').style.display = 'none';
      document.getElementById('add-word-section').style.display = 'none';

      // Deactivate all tabs
      document.getElementById('users-tab').classList.remove('is-active');
      document.getElementById('words-tab').classList.remove('is-active');
      document.getElementById('add-word-tab').classList.remove('is-active');

      // Show selected section and activate tab
      document.getElementById(tabName + '-section').style.display = 'block';
      document.getElementById(tabName + '-tab').classList.add('is-active');
    }
async function deleteWord(id) {
    if (confirm('Are you sure you want to delete this word?')) {
        try {
            const response = await fetch('/admin/delete_word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id })
            });
            const data = await response.json();
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                showNotification('Word deleted successfully', 'success');
                refreshWordList();
            }
        } catch (error) {
            console.error('Error deleting word:', error);
            showNotification('An error occurred while deleting the word. Please try again.', 'error');
        }
    }
}

async function toggleAdmin(id) {
    if (confirm('Are you sure you want to toggle admin status for this user?')) {
        try {
            const response = await fetch('/admin/manage_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id, action: 'toggle_admin' })
            });
            const data = await response.json();
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                showNotification('User admin status toggled successfully', 'success');
                refreshUserList();
            }
        } catch (error) {
            console.error('Error toggling admin status:', error);
            showNotification('An error occurred while toggling admin status. Please try again.', 'error');
        }
    }
}

async function deleteUser(id) {
    if (confirm('Are you sure you want to delete this user?')) {
        try {
            const response = await fetch('/admin/manage_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id, action: 'delete' })
            });
            const data = await response.json();
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                showNotification('User deleted successfully', 'success');
                refreshUserList();
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            showNotification('An error occurred while deleting the user. Please try again.', 'error');
        }
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

async function refreshWordList() {
    //
}

async function refreshUserList() {
    //
}