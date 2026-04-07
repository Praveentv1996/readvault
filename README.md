# ReadVault 📚

A full-stack personal reading tracker with AI-powered insights and dual database synchronization.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![MongoDB](https://img.shields.io/badge/MongoDB-7-4EA94B?logo=mongodb)
![Docker](https://img.shields.io/badge/Docker-Latest-2496ED?logo=docker)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript)
![AI](https://img.shields.io/badge/AI-Qwen_3.6-FF6B00)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Overview

ReadVault is a personal library management system that tracks books across multiple sources (Kindle, Kuku FM, Physical Books, YouTube, etc.). It features:

- **Intelligent Book Management** with auto-categorization
- **AI-Powered Chat Assistant** for insights about your reading habits
- **Dual Database Sync** (PostgreSQL + MongoDB)
- **Real-time Filtering & Search** with multiple dimensions
- **Theme Customization** (6 themes)
- **Type Auto-Categorization** (E-Book, AudioBook, VideoBook, Book)

**Current Library:** 218+ books tracked

---

## ✨ Key Features

### 📖 Book Management
- ✅ Add/Edit/Delete books with full metadata
- ✅ Track 5 content sources: Kuku FM, Kindle, Pustaka, YouTube, Physical Books
- ✅ Auto-calculate content type from source (E-Book, AudioBook, VideoBook, Book)
- ✅ Mark books as "Finished" or "Reading"
- ✅ Tag featured characters for each book
- ✅ Real-time table display with 20+ books per page

### 🤖 AI Assistant
- ✅ Natural language queries about your collection
- ✅ Powered by Qwen 3.6 via OpenRouter API
- ✅ Full book context in conversations
- ✅ Markdown-formatted responses with tables
- ✅ Reading pattern analysis & recommendations

**Example Queries:**
- *"Show all books by Tamil authors"*
- *"Which are my favorite sources?"*
- *"Books currently reading with Vivek"*
- *"Suggest next thriller to read"*
- *"Reading statistics by type"*

### 🎨 UI/UX Features
- ✅ 6 color themes (Orange, Green, Yellow, Blue, Purple, Red)
- ✅ Persistent theme in localStorage
- ✅ Advanced filtering (Author, Source, Status, Featuring)
- ✅ Column sorting (click headers)
- ✅ Pagination (10, 20, 50, 100 rows/page)
- ✅ Global search across title, author, characters
- ✅ Responsive design

### 🗄️ Database Features
- ✅ PostgreSQL for primary data
- ✅ MongoDB for author-based collections
- ✅ Real-time sync on every change
- ✅ Migration scripts for schema updates
- ✅ Automatic type field population

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker & Docker Compose installed
- .env file with API keys (see below)

**Run:**
```bash
git clone https://github.com/Praveentv1996/readvault.git
cd readvault
cp .env.example .env
# Edit .env with your credentials
docker-compose up --build
```

Open **http://localhost:5000**

**Stop:**
```bash
docker-compose down
```

### Option 2: Local Setup

**Prerequisites:**
- Python 3.11+
- PostgreSQL 15+
- MongoDB 7+ (optional, for mirror sync)
- Node.js (optional, for MongoDB migrations)

**Install:**
```bash
git clone https://github.com/Praveentv1996/readvault.git
cd readvault

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Start PostgreSQL and MongoDB (if installed)
# Then run:
python api.py
```

Open **http://localhost:5000**

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# PostgreSQL Configuration
DB_HOST=localhost
DB_NAME=BOOK
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# MongoDB Configuration (optional)
MONGO_URI=mongodb://localhost:27017

# AI API Configuration
OPENROUTER_API_KEY=your_openrouter_key  # Get from https://openrouter.ai
```

### Docker Environment

If using Docker, these are auto-configured in `docker-compose.yml`:

```yaml
app:
  environment:
    - DB_HOST=postgres          # Docker service name
    - MONGO_URI=mongodb://mongodb:27017
```

---

## 📊 Database Schema

### PostgreSQL - Book Table

```sql
CREATE TABLE book (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    author      VARCHAR(255) NOT NULL,
    source      VARCHAR(100),              -- Kuku FM, Kindle Unlimited, Pushtaka Digital Media, YouTube, Book
    type        VARCHAR(50),                -- E-Book, AudioBook, VideoBook, Book (auto-calculated)
    status      VARCHAR(50) DEFAULT 'Finished',  -- Finished, Reading
    featuring   VARCHAR(255)                -- Featured characters (optional)
);
```

### MongoDB - Author Collections

Each author has a collection with documents:

```json
{
  "_id": ObjectId("..."),
  "id": 1,                    // PostgreSQL reference
  "title": "Book Title",
  "author": "Author Name",
  "source": "Kuku FM",
  "type": "AudioBook",        // Auto-calculated
  "status": "Reading",
  "featuring": "Character Names"
}
```

### Type Auto-Calculation

```
Source                    → Type
Kuku FM                   → AudioBook
Kindle Unlimited          → E-Book
Pushtaka Digital Media    → E-Book
YouTube                   → VideoBook
Book (Physical)           → Book
```

---

## 🔌 API Endpoints

All endpoints require no authentication. Data is sent/received as JSON.

### Books

#### Get All Books
```http
GET /api/books
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Ponniyin Selvan",
    "author": "Kalki",
    "source": "Kindle Unlimited",
    "type": "E-Book",
    "status": "Finished",
    "featuring": "Arulmozhivarman, Vanathi"
  },
  ...
]
```

#### Add Book
```http
POST /api/books
Content-Type: application/json

{
  "title": "Book Title",
  "author": "Author Name",
  "source": "Kuku FM",
  "status": "Reading",
  "featuring": "Character Names"
}
```

**Returns:** Created book object with auto-calculated type

#### Update Book
```http
PUT /api/books/{id}
Content-Type: application/json

{
  "title": "Updated Title",
  "author": "Author Name",
  "source": "YouTube",
  "status": "Finished",
  "featuring": ""
}
```

**Note:** Type is automatically recalculated based on source

#### Delete Book
```http
DELETE /api/books/{id}
```

**Returns:** `{"deleted": id}`

### AI Chat

#### Send Message
```http
POST /api/ai/chat
Content-Type: application/json

{
  "message": "Show all books by Sujatha",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Response:**
```json
{
  "response": "Here are all books by Sujatha:\n\n| Title | Source | Status |\n|-------|--------|--------|..."
}
```

---

## 📦 Project Structure

```
readvault/
├── api.py                           # Flask backend (REST API + AI chat)
├── migrate_add_type_column.py       # PostgreSQL migration script
├── server.py                        # PostgreSQL MCP server (Claude)
├── app.pyw                          # Windows desktop launcher
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Multi-container orchestration
├── init.sql                         # PostgreSQL schema initialization
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .dockerignore                    # Docker build optimization
│
├── FRONT END/                       # Web UI
│   ├── index.html                   # HTML structure
│   ├── script.js                    # Vanilla JavaScript (no frameworks)
│   └── style.css                    # Responsive design
│
├── MONGO_DB_migrate_add_type.js     # Add type field to MongoDB
├── MONGO_DB_migrate_remove_pg_id.js # Remove redundant pg_id from MongoDB
├── MONGO_DB_SCHEMA.md               # MongoDB schema documentation
├── MONGO_DB_MIGRATION_SUMMARY.md    # MongoDB migration guide
│
├── DOCKER_BUILD_GUIDE.md            # Docker build & push instructions
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## 🔄 Data Sync

ReadVault maintains a dual database architecture:

```
User Action (Add/Edit/Delete)
        ↓
    Flask API
    ↙       ↘
PostgreSQL  MongoDB
(Primary)   (Mirror by Author)
    ↓           ↓
   Stored    Author Collections
```

**Sync Details:**
- PostgreSQL: Source of truth, all operations here first
- MongoDB: Auto-synced using `id` field as reference
- Type: Auto-calculated on every save
- Real-time: Changes immediately visible in UI

---

## 📈 Migrations

### v1.1.0 Update (YouTube + Type Column)

**New Features:**
- ✅ YouTube as 5th content source
- ✅ Type column with auto-calculation
- ✅ Enhanced MongoDB schema
- ✅ 218+ books migrated successfully

**Upgrading from v1.0.0:**

```bash
# 1. Pull latest code
git pull origin master

# 2. Rebuild Docker
docker-compose down
docker-compose up --build

# 3. Auto-migration runs on startup
# (PostgreSQL: migrate_add_type_column.py)
# (MongoDB: manual if needed)

# 4. Verify: Open http://localhost:5000
# Should see Type column and YouTube source
```

**Manual PostgreSQL Migration:**
```bash
python migrate_add_type_column.py
```

**Manual MongoDB Migration:**
```bash
node MONGO_DB_migrate_add_type.js
node MONGO_DB_migrate_remove_pg_id.js
```

See [MONGO_DB_MIGRATION_SUMMARY.md](./MONGO_DB_MIGRATION_SUMMARY.md) for details.

---

## 🐳 Docker

### Available Image Versions

| Tag | Features | Status |
|-----|----------|--------|
| `v1.0.0` | Initial release | Deprecated |
| `v1.1.0` | YouTube + Type column | Current |
| `latest` | Always newest | Recommended |

### Build & Push to Docker Hub

See [DOCKER_BUILD_GUIDE.md](./DOCKER_BUILD_GUIDE.md) for detailed instructions.

**Quick Build:**
```bash
docker build -t praveentv1996/readvault:v1.1.0 .
docker push praveentv1996/readvault:v1.1.0
```

**Pull & Run:**
```bash
docker pull praveentv1996/readvault:latest
docker-compose up
```

---

## 🛠️ Development

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Flask | 2.x |
| Language | Python | 3.11+ |
| Primary DB | PostgreSQL | 15+ |
| Mirror DB | MongoDB | 7+ |
| Frontend | Vanilla JS | ES6 |
| Styling | CSS3 | No framework |
| AI | Qwen 3.6 | OpenRouter API |
| Containerization | Docker | Latest |

### Adding Features

1. **Backend:** Edit `api.py` (Flask routes)
2. **Database:** Update `init.sql` and create migration script
3. **Frontend:** Edit `FRONT END/script.js` (logic) and `style.css` (styling)
4. **Test:** `docker-compose up --build`
5. **Push:** Commit and `git push`

### Database Migrations

When adding columns or changing schema:

```bash
# PostgreSQL
python migrate_add_type_column.py  # As template

# MongoDB
node MONGO_DB_migrate_add_type.js  # As template
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 instead of 5000
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Check MongoDB is running
docker-compose logs mongodb

# Verify .env has correct credentials
cat .env
```

### Migration Fails

```bash
# Check logs
docker-compose logs app

# Manual fix (if migration didn't run):
python migrate_add_type_column.py
```

### Docker Image Not Updated

```bash
# Force rebuild from source
docker-compose down
docker image rm readvault:latest
docker-compose up --build
```

### Books Not Loading

```bash
# Verify database has data
docker-compose exec postgres psql -U postgres -d BOOK -c "SELECT COUNT(*) FROM book;"

# Check API is running
curl http://localhost:5000/api/books

# Check browser console for errors (F12)
```

---

## 📝 License

MIT License - See LICENSE file

---

## 👤 Author

**Praveen TV**
- GitHub: [@Praveentv1996](https://github.com/Praveentv1996)
- Repository: [readvault](https://github.com/Praveentv1996/readvault)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/Praveentv1996/readvault/issues)
- Check [DOCKER_BUILD_GUIDE.md](./DOCKER_BUILD_GUIDE.md) for Docker help
- Check [MONGO_DB_SCHEMA.md](./MONGO_DB_SCHEMA.md) for database questions

---

## 📚 Additional Resources

- [Docker Build Guide](./DOCKER_BUILD_GUIDE.md) - Build and push Docker images
- [MongoDB Schema](./MONGO_DB_SCHEMA.md) - MongoDB structure and migrations
- [Migration Summary](./MONGO_DB_MIGRATION_SUMMARY.md) - v1.1.0 migration details
- [.env.example](./.env.example) - Environment configuration template

---

**Happy Reading! 📖**

*Track your books, discover patterns, and let AI guide your next read.*
