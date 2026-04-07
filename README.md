# ReadVault

A full-stack personal reading tracker with an AI-powered chat assistant.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![MongoDB](https://img.shields.io/badge/MongoDB-Mirror_Store-4EA94B)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![AI](https://img.shields.io/badge/AI-Qwen_3.6_via_OpenRouter-orange)

---

## Features

- **Book Management** — Add, edit, delete books with title, author, source, status, and featuring characters
- **AI Chat Assistant** — Ask natural language questions about your collection powered by Qwen 3.6
- **Dual Database** — PostgreSQL as primary store, MongoDB mirrored by author
- **Smart Filtering** — Filter by author, source, status, featuring with real-time search
- **Sortable Table** — Sort by any column with pagination
- **Theme Switcher** — 6 color themes (Orange, Green, Yellow, Blue, Purple, Red) persisted in localStorage
- **Markdown Rendering** — AI responses render tables, bold, and lists properly

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Primary DB | PostgreSQL |
| Mirror DB | MongoDB |
| AI | Qwen 3.6 via OpenRouter API |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Containerization | Docker, Docker Compose |

---

## AI Assistant Examples

Ask the AI assistant anything about your collection:

- *"How many books have I read by Rajeshkumar?"*
- *"Show all Kuku FM books in a table"*
- *"Which books am I currently reading?"*
- *"Which author do I read the most?"*
- *"Suggest what to read next"*

---

## Run with Docker

```bash
# 1. Clone the repo
git clone https://github.com/Praveentv1996/readvault.git
cd readvault

# 2. Copy env file and fill in your values
cp .env.example .env
# Edit .env with your PostgreSQL, MongoDB, and OpenRouter credentials

# 3. Start all services (forces rebuild from latest code)
docker-compose up --build

# 4. Stop services
docker-compose down
```

Open **http://localhost:5000** in your browser.

### Build & Push Docker Image to Docker Hub

```bash
# 1. Login to Docker Hub
docker login

# 2. Build image with version tag (v1.1.0 = YouTube + Type feature)
docker build -t praveentv1996/readvault:v1.1.0 .
docker build -t praveentv1996/readvault:latest .

# 3. Push to Docker Hub
docker push praveentv1996/readvault:v1.1.0
docker push praveentv1996/readvault:latest

# 4. Now anyone can pull: docker pull praveentv1996/readvault:latest
```

### Docker Image Versions

| Tag | Features | Date |
|-----|----------|------|
| `v1.0.0` | Initial release | 2 days ago |
| `v1.1.0` | YouTube source + Type column | Today |
| `latest` | Always the newest version | Today |

---

## Run Locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env
cp .env.example .env
# Edit .env with your PostgreSQL and OpenRouter credentials

# Run
python api.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL host (default: localhost) |
| `DB_NAME` | Database name (default: BOOK) |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_PORT` | PostgreSQL port (default: 5432) |
| `MONGO_URI` | MongoDB connection URI |
| `OPENROUTER_API_KEY` | OpenRouter API key (get one at openrouter.ai) |

---

## Project Structure

```
readvault/
├── api.py              # Flask backend — REST API + AI chat endpoint
├── server.py           # PostgreSQL MCP server for Claude Desktop
├── app.pyw             # Desktop app launcher (pywebview)
├── Dockerfile
├── docker-compose.yml
├── init.sql            # PostgreSQL schema
├── requirements.txt
├── .env.example
└── FRONT END/
    ├── index.html
    ├── script.js
    └── style.css
```

---

## Migrations & Updates

### v1.1.0 Update (YouTube + Type Column)

If you're upgrading from v1.0.0 to v1.1.0:

#### 1. Pull Latest Code
```bash
git pull origin master
```

#### 2. Rebuild Docker Image
```bash
docker-compose down
docker-compose up --build    # Forces rebuild with new code
```

#### 3. PostgreSQL Migration (Auto-runs)
The migration runs automatically when the container starts if needed.

#### 4. MongoDB Migrations (Optional, if using MongoDB)
```bash
# Inside the container or on your machine:
node MONGO_DB_migrate_add_type.js
node MONGO_DB_migrate_remove_pg_id.js
```

#### What Changed
- ✅ Added **YouTube** as 5th content source
- ✅ Added **Type** column (E-Book, AudioBook, VideoBook, Book)
- ✅ Auto-calculated Type based on Source
- ✅ 218+ existing books migrated with Type populated
- ✅ MongoDB schema refactored (removed redundant pg_id)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/books` | Fetch all books |
| POST | `/api/books` | Add a new book |
| PUT | `/api/books/<id>` | Update a book |
| DELETE | `/api/books/<id>` | Delete a book |
| POST | `/api/ai/chat` | AI chat with book context |
