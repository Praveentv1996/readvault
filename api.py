#!/usr/bin/env python3
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "database": "BOOK",
    "user": "postgres",
    "password": "Pravin#.2",
    "port": "5432"
}

FRONTEND = os.path.join(os.path.dirname(__file__), 'FRONT END')

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND, filename)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, title, author, source, type, status, featuring FROM book ORDER BY id")
        books = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    try:
        data = request.json
        if not data.get('title') or not data.get('author'):
            return jsonify({'error': 'Title and Author required'}), 400

        source = data.get('source', '').strip()
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        status = data.get('status', 'Finished').strip()
        featuring = data.get('featuring', '').strip()

        book_type = 'E-Book' if source in ['Kindle Unlimited', 'Pushtaka Digital Media'] else \
                   'AudioBook' if source == 'Kuku FM' else \
                   'VideoBook' if source == 'YouTube' else \
                   'Book' if source == 'Book' else 'Unknown'

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "INSERT INTO book (title, author, source, type, status, featuring) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (title, author, source, book_type, status, featuring)
        )
        row = dict(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(row), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.json
        if not data.get('title') or not data.get('author'):
            return jsonify({'error': 'Title and Author required'}), 400

        source = data.get('source', '').strip()
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        status = data.get('status', 'Finished').strip()
        featuring = data.get('featuring', '').strip()

        book_type = 'E-Book' if source in ['Kindle Unlimited', 'Pushtaka Digital Media'] else \
                   'AudioBook' if source == 'Kuku FM' else \
                   'VideoBook' if source == 'YouTube' else \
                   'Book' if source == 'Book' else 'Unknown'

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "UPDATE book SET title=%s, author=%s, source=%s, type=%s, status=%s, featuring=%s WHERE id=%s RETURNING *",
            (title, author, source, book_type, status, featuring, book_id)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        row = dict(row)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(row)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM book WHERE id=%s", (book_id,))
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'deleted': book_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting BookVault API on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
