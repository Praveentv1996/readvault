# BookVault

> A personal desktop app to catalogue and track every book, audiobook, e-book, and video-book you read — backed by a local PostgreSQL database and surfaced through a clean, fast UI.

---

## About

BookVault was built as a private reading tracker to replace messy spreadsheets.
The goal was simple: one place to log every book, filter by source or status, and glance at stats without opening a browser or paying for a subscription service.

It runs entirely on **localhost** — no cloud, no accounts, no data leaving your machine.
The backend is a minimal Flask API talking to a local PostgreSQL database.
The UI is plain HTML/CSS/JS loaded inside a native desktop window via pywebview, so it looks and feels like a real app without shipping an Electron bundle.

A companion **MCP server** (`server.py`) exposes the database to Claude Code, so you can ask plain-English questions like *"how many audiobooks did I finish this year?"* and get live answers without writing SQL.

---

## Features

- Add, edit, and delete books via a modal form
- Multi-field filter bar — Author · Source · Status · Featuring
- Global search across title, author, and featuring fields
- Sortable columns (single-click to sort, click again to reverse)
- Live stats dashboard — total books, unique authors, finished count, source breakdown chart
- Auto-detects book type from source (AudioBook / E-Book / VideoBook / Book)
- Paginated table with 10 / 20 / 50 / 100 rows-per-page
- White and Grey themes, persisted via `localStorage`
- F5 / refresh button to reload data without restarting the app
- About panel with full app info accessible from the sidebar
- MCP server for AI-assisted queries from Claude Code

---

## Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Backend API   | Python · Flask · Flask-CORS         |
| Database      | PostgreSQL · psycopg2               |
| Frontend      | Vanilla HTML / CSS / JavaScript     |
| Desktop Shell | pywebview (native OS window)        |
| AI Integration| PostgreSQL MCP Server (Claude Code) |

---

## Sources & Auto-Types

| Source                  | Auto Type  |
|-------------------------|------------|
| Kuku FM                 | AudioBook  |
| Kindle Unlimited        | E-Book     |
| Pushtaka Digital Media  | E-Book     |
| YouTube                 | VideoBook  |
| Book                    | Book       |

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

```sql
CREATE TABLE IF NOT EXISTS book (
    id        SERIAL PRIMARY KEY,
    title     VARCHAR(255) NOT NULL,
    author    VARCHAR(255) NOT NULL,
    source    VARCHAR(100),
    type      VARCHAR(50),
    status    VARCHAR(50)  DEFAULT 'Finished',
    featuring VARCHAR(255)
);
```

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

> `pywebview` is required to launch the desktop window:
> ```bash
> pip install pywebview
> ```

### 2. Set up PostgreSQL

- Create a database named `BOOK`
- Run `init.sql` to create the table:

```bash
psql -U postgres -d BOOK -f init.sql
```

- Update credentials in `api.py` if needed:

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
# then open http://localhost:5000
```

---

## API Endpoints

| Method | Endpoint          | Description      |
|--------|-------------------|------------------|
| GET    | `/api/books`      | List all books   |
| POST   | `/api/books`      | Add a book       |
| PUT    | `/api/books/<id>` | Update a book    |
| DELETE | `/api/books/<id>` | Delete a book    |
| GET    | `/api/health`     | Health check     |

---

## MCP Server (Claude Code Integration)

`server.py` implements a **Model Context Protocol** server that exposes four tools:

| Tool             | Description                              |
|------------------|------------------------------------------|
| `query`          | Run any SELECT statement                 |
| `execute`        | Run INSERT / UPDATE / DELETE / DDL       |
| `list_tables`    | List all tables in the database          |
| `describe_table` | Show column names, types and constraints |

Configure it in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "postgres-mcp": {
      "command": "python",
      "args": ["C:/path/to/BookVault/server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_NAME": "BOOK",
        "DB_USER": "postgres",
        "DB_PASSWORD": "your_password",
        "DB_PORT": "5432"
      }
    }
  }
}
```

---

## Project Structure

```
BookVault/
├── api.py            # Flask REST API
├── app.pyw           # Desktop launcher (pywebview)
├── server.py         # PostgreSQL MCP server for Claude Code
├── init.sql          # Database schema
├── requirements.txt  # Python dependencies
├── bookshelf.ico     # App icon
└── FRONT END/
    ├── index.html    # App shell + modals (Add/Edit, Theme, About)
    ├── style.css     # CSS variables, layout, components
    └── script.js     # State management, CRUD, filters, pagination
```

---

## Developer

Built by **Praveen TV** — Chennai, India
