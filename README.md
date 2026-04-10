# BookVault

A personal desktop application to track your book collection. Built with Python (Flask) and PostgreSQL, runs as a native desktop window via pywebview.

---

## Features

- Add, edit, and delete books from your collection
- Filter by Author, Source, Status, or Featuring characters
- Sort any column in the table
- Search across title, author, and featuring fields
- Stats dashboard — total books, authors, finished count, source breakdown
- Auto-detects book type (AudioBook, E-Book, VideoBook, Book) based on source
- Two light themes — White and Grey
- Refresh button (or F5) to reload without restarting the app

---

## Tech Stack

| Layer    | Technology          |
|----------|---------------------|
| Backend  | Python, Flask       |
| Database | PostgreSQL          |
| Frontend | HTML, CSS, JS       |
| Desktop  | pywebview           |

---

## Database Schema

**Table: `book`**

| Column     | Type          | Constraints            |
|------------|---------------|------------------------|
| id         | SERIAL        | PRIMARY KEY            |
| title      | VARCHAR(255)  | NOT NULL               |
| author     | VARCHAR(255)  | NOT NULL               |
| source     | VARCHAR(100)  |                        |
| type       | VARCHAR(50)   |                        |
| status     | VARCHAR(50)   | DEFAULT `'Finished'`   |
| featuring  | VARCHAR(255)  |                        |

---

## Sources & Types

| Source                | Auto Type  |
|-----------------------|------------|
| Kuku FM               | AudioBook  |
| Kindle Unlimited      | E-Book     |
| Pushtaka Digital Media| E-Book     |
| YouTube               | VideoBook  |
| Book                  | Book       |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL

- Create a database named `BOOK`
- Run `init.sql` to create the table:

```bash
psql -U postgres -d BOOK -f init.sql
```

- Update the DB credentials in `api.py` if needed:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "BOOK",
    "user": "postgres",
    "password": "your_password",
    "port": "5432"
}
```

### 3. Run the app

**Desktop window (recommended):**
```bash
pythonw app.pyw
```

**Browser only:**
```bash
python api.py
```
Then open `http://localhost:5000`

---

## API Endpoints

| Method | Endpoint            | Description       |
|--------|---------------------|-------------------|
| GET    | `/api/books`        | Get all books     |
| POST   | `/api/books`        | Add a book        |
| PUT    | `/api/books/<id>`   | Update a book     |
| DELETE | `/api/books/<id>`   | Delete a book     |
| GET    | `/api/health`       | Health check      |

---

## Project Structure

```
BookVault/
├── api.py            # Flask backend
├── app.pyw           # Desktop app launcher (pywebview)
├── init.sql          # Database schema
├── requirements.txt  # Python dependencies
├── bookshelf.ico     # App icon
├── server.py         # MCP server (for Claude Code integration)
└── FRONT END/
    ├── index.html
    ├── style.css
    └── script.js
```
