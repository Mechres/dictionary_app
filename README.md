# Multilingual Dictionary Application

<img src="https://github.com/user-attachments/assets/3de0e0c5-44be-432a-a6a5-1bd243428a1c">

This project is a web-based multilingual dictionary application built with Flask. It allows users to search for words across different languages, add new words (for admins), and manage the dictionary database.

It looks ugly I know.

## Features

- Support for multiple language pairs
- User authentication (login/register)
- Word search with fuzzy matching
- Category-based filtering
- Admin panel for managing words and users
- Excel import functionality for bulk word addition
- Responsive design
- Bidirectional word association
  
## Project Structure

```
dictionary_app/
│
├── static/
│   ├── admin.js
│   ├── scripts.js
│   ├── scripts_old.js
│   ├── styles_old.css
│   └── styles.css
│
├── templates/
│   ├── admin.html
│   ├── import_excel.html
│   ├── index_old.html
│   └── index.html
│
├── app.py
├── dictionary.db
├── excel_to_db.py
└── README.md
```

```
***_Old.** files can be used they're just a different theme.
```


## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/multilingual-dictionary.git
   cd multilingual-dictionary
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python app.py
   ```

5. Run the application:
   ```
   flask run
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Usage
```
Admin Username: Admin
Admin password: admin
```

### Regular Users
- Search for words using the search bar on the homepage
- Filter results by category and language
- Register for an account or log in to access additional features

### Admin Users
- Access the admin panel to manage words and users
- Add new words to the dictionary in various languages
- Edit or delete existing words
- Import words from an Excel file
- Manage user accounts (promote to admin or delete)

## Adding New Languages

The application is designed to be language-agnostic. To add support for new languages:

1. Update the language options in the admin interface (`admin.html`)
2. Modify the `add_word` function in `app.py` to handle the new language
3. Update the search functionality in `app.py` to include the new language

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- Additional libraries: Flask-CORS, Flask-Bcrypt, Flask-JWT-Extended, fuzzywuzzy

## Screenshot

<img src="https://github.com/user-attachments/assets/64c8ca55-b1d7-43ca-a9ed-40fced97db40" width="100" height="100">
<img src="https://github.com/user-attachments/assets/bfe8a327-0914-464d-951e-68ca1886075f" width="100" height="100">
<img src="https://github.com/user-attachments/assets/5f8118ad-ed77-4f5b-8500-6505a6473f75" width="100" height="100">
<img src="https://github.com/user-attachments/assets/e4ebd249-2d27-4132-804f-916ebd9a8f92" width="100" height="100">
<img src="https://github.com/user-attachments/assets/96b174cb-5475-4800-85e5-8e9fe564b361" width="100" height="100">
<img src="https://github.com/user-attachments/assets/a98971a9-3c04-4a1b-8bdc-d7948bd4173c" width="100" height="100">

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
