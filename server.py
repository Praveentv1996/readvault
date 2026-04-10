import asyncio
import json
import os
import psycopg2
import psycopg2.extras
import psycopg2.pool
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "BOOK"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "port": os.environ.get("DB_PORT", "5432")
}

# Connection pool
_pg_pool = None

def get_pool():
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
    return _pg_pool

def get_connection():
    return get_pool().getconn()

def release_connection(conn):
    if conn:
        get_pool().putconn(conn)

app = Server("postgres-mcp")

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="query",
            description="Run a SELECT query on the PostgreSQL database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL SELECT query to execute"}
                },
                "required": ["sql"]
            }
        ),
        types.Tool(
            name="execute",
            description="Execute INSERT, UPDATE, DELETE, or DDL statements",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL statement to execute"}
                },
                "required": ["sql"]
            }
        ),
        types.Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="describe_table",
            description="Describe the schema of a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table to describe"}
                },
                "required": ["table_name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query":
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(arguments["sql"])
            rows = cur.fetchall()
            cur.close()
            return [types.TextContent(type="text", text=json.dumps([dict(r) for r in rows], indent=2, default=str))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        finally:
            if conn:
                release_connection(conn)

    elif name == "execute":
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(arguments["sql"])
            conn.commit()
            rowcount = cur.rowcount
            cur.close()
            return [types.TextContent(type="text", text=f"Success. Rows affected: {rowcount}")]
        except Exception as e:
            if conn:
                conn.rollback()
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        finally:
            if conn:
                release_connection(conn)

    elif name == "list_tables":
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            return [types.TextContent(type="text", text=json.dumps(tables, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        finally:
            if conn:
                release_connection(conn)

    elif name == "describe_table":
        conn = None
        try:
            table_name = arguments.get("table_name", "").strip()
            if not table_name:
                return [types.TextContent(type="text", text="Error: table_name is required")]
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cur.fetchall()
            cur.close()
            result = [{"column": c[0], "type": c[1], "nullable": c[2], "default": c[3]} for c in columns]
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        finally:
            if conn:
                release_connection(conn)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
