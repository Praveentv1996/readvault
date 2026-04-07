#!/usr/bin/env python3
"""
PostgreSQL Migration: Add 'type' column to existing 'book' table
Run this ONCE to add the missing column to your existing database
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "BOOK"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "port": os.environ.get("DB_PORT", "5432")
}

def get_type_from_source(source):
    """Calculate Type based on Source value"""
    if source in ["Kindle Unlimited", "Pushtaka Digital Media"]:
        return "E-Book"
    elif source == "Kuku FM":
        return "AudioBook"
    elif source == "YouTube":
        return "VideoBook"
    elif source == "Book":
        return "Book"
    return "Unknown"

def migrate():
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("SUCCESS: Connected!")

        # Check if 'type' column already exists
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='book' AND column_name='type'
        """)

        if cur.fetchone():
            print("WARNING: 'type' column already exists! No migration needed.")
            cur.close()
            conn.close()
            return

        print("\nMigration Steps:")
        print("1. Adding 'type' column to book table...")

        # Add the type column
        cur.execute("ALTER TABLE book ADD COLUMN type VARCHAR(50)")
        conn.commit()
        print("   SUCCESS: Column added")

        # Get all books and populate type based on source
        print("2. Populating 'type' column for all existing books...")
        cur.execute("SELECT id, source FROM book")
        books = cur.fetchall()

        updated_count = 0
        for book_id, source in books:
            book_type = get_type_from_source(source or "")
            cur.execute("UPDATE book SET type = %s WHERE id = %s", (book_type, book_id))
            updated_count += 1

        conn.commit()
        print(f"   SUCCESS: Updated {updated_count} books")

        # Verify
        cur.execute("SELECT COUNT(*) FROM book WHERE type IS NOT NULL")
        populated = cur.fetchone()[0]

        print(f"\nMIGRATION COMPLETE!")
        print(f"Total books with type: {populated}/{updated_count}")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL Migration: Add 'type' column")
    print("=" * 50)
    print()

    try:
        migrate()
    except Exception as e:
        print(f"\nMigration failed! Error: {e}")
        exit(1)
