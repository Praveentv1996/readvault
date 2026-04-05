from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

FRONTEND = os.path.join(os.path.dirname(__file__), 'FRONT END')

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND, filename)

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "BOOK"),
    "user":     os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "port":     os.environ.get("DB_PORT", "5432")
}

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MONGO_URI          = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# MongoDB setup
_mongo_client = None

def get_mongo_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
    return _mongo_client["BOOKS"]

def get_mongo_collection(author):
    collection_name = author.strip().replace(" ", "_")
    return get_mongo_db()[collection_name]


@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, title, author, source, status, featuring FROM book ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)


@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO book (title, author, source, status, featuring) VALUES (%s, %s, %s, %s, %s) RETURNING *",
        (data['title'], data['author'], data.get('source',''), data.get('status','Finished'), data.get('featuring',''))
    )
    row = dict(cur.fetchone())
    conn.commit(); cur.close(); conn.close()

    # Mirror to MongoDB
    col = get_mongo_collection(row['author'])
    col.update_one({"pg_id": row['id']}, {"$set": {**row, "pg_id": row['id']}}, upsert=True)

    return jsonify(row), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "UPDATE book SET title=%s, author=%s, source=%s, status=%s, featuring=%s WHERE id=%s RETURNING *",
        (data['title'], data['author'], data.get('source',''), data.get('status','Finished'), data.get('featuring',''), book_id)
    )
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    row = dict(row)

    # Mirror to MongoDB
    col = get_mongo_collection(row['author'])
    col.update_one({"pg_id": book_id}, {"$set": {**row, "pg_id": book_id}}, upsert=True)

    return jsonify(row)


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT author FROM book WHERE id=%s", (book_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({'error': 'Not found'}), 404
    author = row['author']
    cur.execute("DELETE FROM book WHERE id=%s", (book_id,))
    conn.commit(); cur.close(); conn.close()

    # Mirror to MongoDB
    col = get_mongo_collection(author)
    col.delete_one({"pg_id": book_id})

    return jsonify({'deleted': book_id})


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    user_message = (data.get('message') or '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Fetch all books from PostgreSQL for context
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT title, author, source, status, featuring FROM book ORDER BY author, title")
    books = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()

    system_prompt = f"""You are a personal reading assistant for Praveen's Tamil book collection.
He reads Tamil novels — mostly detective fiction, thrillers, and romance.

His complete book collection ({len(books)} books) from the database:
{json.dumps(books, ensure_ascii=False, indent=2)}

Sources he uses: Kuku FM (audio), Kindle Unlimited (ebook), Pushtaka Digital Media (ebook), Book (physical).
Statuses: Finished = completed reading, Reading = currently reading.

Answer questions about his collection, provide insights, recommend what to read next, find books by author/source/status, and analyze reading patterns.
Keep responses concise and helpful. Use the actual book titles and author names from the data above.
When showing lists of books, use markdown tables with columns like Title, Author, Source, Status.
Always use markdown formatting — tables, bold, bullet points. Never use raw HTML."""

    messages = [{"role": h['role'], "content": h['content']} for h in history[-10:]]
    messages.append({"role": "user", "content": user_message})

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
        response = client.chat.completions.create(
            model="qwen/qwen3.6-plus:free",
            max_tokens=1024,
            messages=[{"role": "system", "content": system_prompt}] + messages
        )
        return jsonify({'response': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
