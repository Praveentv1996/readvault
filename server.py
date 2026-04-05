import asyncio
import json
import psycopg2
import psycopg2.extras
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

DB_CONFIG = {
    "host": "localhost",
    "database": "BOOK",
    "user": "postgres",
    "password": "Pravin#.2",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

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
        try:
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(arguments["sql"])
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [types.TextContent(type="text", text=json.dumps([dict(r) for r in rows], indent=2, default=str))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "execute":
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(arguments["sql"])
            conn.commit()
            rowcount = cur.rowcount
            cur.close()
            conn.close()
            return [types.TextContent(type="text", text=f"Success. Rows affected: {rowcount}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "list_tables":
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return [types.TextContent(type="text", text=json.dumps(tables, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "describe_table":
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (arguments["table_name"],))
            columns = cur.fetchall()
            cur.close()
            conn.close()
            result = [{"column": c[0], "type": c[1], "nullable": c[2], "default": c[3]} for c in columns]
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
