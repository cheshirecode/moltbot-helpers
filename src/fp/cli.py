#!/usr/bin/env python3
"""fp — Family Planner CLI (PostgreSQL backend)"""

import os
import re
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection settings
DB_HOST = os.environ.get("FP_DB_HOST", os.environ.get("PT_DB_HOST", "localhost"))
DB_PORT = os.environ.get("FP_DB_PORT", os.environ.get("PT_DB_PORT", "5433"))
DB_NAME = os.environ.get("FP_DB_NAME", os.environ.get("PT_DB_NAME", "financial_analysis"))
DB_USER = os.environ.get("FP_DB_USER", os.environ.get("PT_DB_USER", "finance_user"))
DB_PASS = os.environ.get("FP_DB_PASS", os.environ.get("PT_DB_PASS", "secure_finance_password"))

USAGE = """\
fp — Family Planner CLI (PostgreSQL)

Usage: fp <command> [args]

Query commands:
  balances              Show all financial balances
  net-worth             Summarize net worth
  tasks                 Show open tasks
  dates [category]      Show key dates (optional category filter)
  people                List family members
  docs [person]         Show documents (optional person filter)
  facts [topic]         Show facts (optional topic filter)
  finances [asset_type] [country] Show financial entries (optional filters)
  search <term>         Search across all tables
  sql <query>           Run read-only SQL
  dump                  Dump all family planning data

Update commands:
  add-fact <topic> <key> <value> [source]
  add-task <action> [priority] [due_date] [category]
  complete-task <id>
  set <table> <id> <column> <value>
  exec <sql>            Run arbitrary SQL (INSERT/UPDATE/DELETE)
  
Admin commands:
  init                  Initialize database tables
"""


def get_db():
    """Connect to PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn


def fmt_rows(rows, columns=None):
    if not rows:
        return "(no results)"
    if columns is None and rows:
        columns = rows[0].keys() if hasattr(rows[0], "keys") else [f"col{i}" for i in range(len(rows[0]))]
    lines = []
    for row in rows:
        parts = []
        for col in columns:
            val = row[col] if hasattr(row, "keys") else row[list(columns).index(col)]
            if val is not None:
                parts.append(f"{col}: {val}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def fmt_rows_for_llm(rows, column_names):
    if not rows:
        return "(no records)"
    
    columns = column_names
    if not columns:
        return "(no records)"

    header = "| " + " | ".join(columns) + " |\n"
    separator_parts = ["-" * max(3, len(col)) for col in columns]
    separator = "|-" + "-|-".join(separator_parts) + "-|\n"

    data_rows = []
    for row in rows:
        formatted_values = []
        for col in columns:
            val = row[col] if hasattr(row, "keys") else row[list(columns).index(col)]
            val_str = str(val) if val is not None else ""
            val_str = val_str.replace('|', '\\|').replace('\n', '\\n')
            formatted_values.append(val_str)
        data_rows.append("| " + " | ".join(formatted_values) + " |")
    
    return header + separator + "\n".join(data_rows)


def cmd_init():
    """Initialize database tables."""
    conn = get_db()
    cur = conn.cursor()
    
    # People table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_people (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            relation TEXT,
            dob DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Documents table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_documents (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES fp_people(id),
            doc_type TEXT NOT NULL,
            doc_number TEXT,
            country TEXT,
            issued DATE,
            expires DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Key dates table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_key_dates (
            id SERIAL PRIMARY KEY,
            label TEXT NOT NULL,
            date DATE,
            category TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Finances table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_finances (
            id SERIAL PRIMARY KEY,
            category TEXT,
            asset_type TEXT,
            country TEXT,
            key TEXT NOT NULL,
            value TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tasks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_tasks (
            id SERIAL PRIMARY KEY,
            action TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            priority TEXT DEFAULT 'P2',
            due_date DATE,
            category TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Facts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_facts (
            id SERIAL PRIMARY KEY,
            topic TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Addresses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_addresses (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES fp_people(id),
            address_type TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("Database tables initialized successfully.")
    conn.close()


def cmd_balances():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT key, value, notes FROM fp_finances WHERE category='banking' ORDER BY key"
    )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_net_worth():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT key, value, notes, category, asset_type, country FROM fp_finances ORDER BY key"
    )
    rows = cur.fetchall()
    total_cad_equivalent = 0.0
    
    print("--- Detailed Net Worth Calculation ---")
    for r in rows:
        value_str = r["value"] or ""
        notes_str = r["notes"] or ""
        asset_cad = 0.0
        processed = False

        cad_equiv_match = re.search(r"CAD equivalent:\s*([\d,.]+)", notes_str)
        if not cad_equiv_match:
            cad_equiv_match = re.search(r"([\d,.]+)\s*CAD", notes_str, re.IGNORECASE)

        if cad_equiv_match:
            numeric_str = re.sub(r'[^\d.]', '', cad_equiv_match.group(1)).strip('.')
            try:
                asset_cad = float(numeric_str)
                print(f"  - {r['key']} ({r['value']}): {asset_cad:,.2f} CAD (from notes)")
                processed = True
            except ValueError:
                print(f"  - {r['key']} ({r['value']}): Could not convert '{numeric_str}' from notes to float, skipping.")

        if not processed:
            cad_match = re.search(r"CAD\s*([\d,.]+)", value_str)
            if not cad_match:
                cad_match = re.search(r"([\d,.]+)\s*CAD", value_str)
            
            if cad_match:
                numeric_str = re.sub(r'[^\d.]', '', cad_match.group(1)).strip('.')
                try:
                    asset_cad = float(numeric_str)
                    print(f"  - {r['key']} ({r['value']}): {asset_cad:,.2f} CAD (direct from value)")
                    processed = True
                except ValueError:
                    print(f"  - {r['key']} ({r['value']}): Could not convert '{numeric_str}' from value to float, skipping.")

        if not processed:
            numeric_match = re.search(r"[\d,.]+", value_str.replace(",", ""))
            if numeric_match:
                amount = float(numeric_match.group())
                if "SGD" in value_str.upper() or "SGD" in notes_str.upper():
                    asset_cad = amount * 0.95
                    print(f"  - {r['key']} ({r['value']}): {asset_cad:,.2f} CAD (approx SGD->CAD)")
                    processed = True
                elif "VND" in value_str.upper() or "VND" in notes_str.upper():
                    print(f"  - {r['key']} ({r['value']}): VND amount, no explicit CAD conversion found, skipping for now.")
                else:
                    print(f"  - {r['key']} ({r['value']}): No currency or explicit CAD equivalent found, skipping for now.")
            else:
                print(f"  - {r['key']} ({r['value']}): Could not parse numeric value, skipping.")
        
        total_cad_equivalent += asset_cad
        
    print("------------------------------------")
    print(f"Total Net Worth (approx CAD): {total_cad_equivalent:,.2f}")
    conn.close()


def cmd_tasks():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, action, status, priority, due_date, category FROM fp_tasks WHERE status != 'DONE' ORDER BY priority, due_date"
    )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_dates(category=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if category:
        cur.execute(
            "SELECT label, date, category, notes FROM fp_key_dates WHERE category=%s ORDER BY date",
            (category,),
        )
    else:
        cur.execute(
            "SELECT label, date, category, notes FROM fp_key_dates ORDER BY date"
        )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_people():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, name, relation, dob, notes FROM fp_people ORDER BY id"
    )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_docs(person=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if person:
        cur.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM fp_documents d JOIN fp_people p ON d.person_id=p.id
               WHERE p.name ILIKE %s ORDER BY p.name, d.doc_type""",
            (f"%{person}%",),
        )
    else:
        cur.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM fp_documents d JOIN fp_people p ON d.person_id=p.id ORDER BY p.name, d.doc_type"""
        )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_facts(topic=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if topic:
        cur.execute(
            "SELECT topic, key, value, source FROM fp_facts WHERE topic ILIKE %s ORDER BY topic, key",
            (f"%{topic}%",),
        )
    else:
        cur.execute(
            "SELECT topic, key, value FROM fp_facts ORDER BY topic, key"
        )
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_search(term):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    pattern = f"%{term}%"
    tables = {
        "facts": "SELECT 'facts' as tbl, topic||'.'||key as item, value FROM fp_facts WHERE topic ILIKE %s OR key ILIKE %s OR value ILIKE %s",
        "tasks": "SELECT 'tasks' as tbl, action as item, notes as value FROM fp_tasks WHERE action ILIKE %s OR notes ILIKE %s OR category ILIKE %s",
        "key_dates": "SELECT 'key_dates' as tbl, label as item, notes as value FROM fp_key_dates WHERE label ILIKE %s OR notes ILIKE %s OR category ILIKE %s",
        "people": "SELECT 'people' as tbl, name as item, notes as value FROM fp_people WHERE name ILIKE %s OR notes ILIKE %s OR relation ILIKE %s",
        "finances": "SELECT 'finances' as tbl, category||'.'||key as item, value FROM fp_finances WHERE key ILIKE %s OR value ILIKE %s OR notes ILIKE %s",
    }
    results = []
    for tbl, sql in tables.items():
        cur.execute(sql, (pattern, pattern, pattern))
        results.extend(cur.fetchall())
    if results:
        for r in results:
            print(f"[{r['tbl']}] {r['item']}: {r['value']}")
    else:
        print(f"No results for '{term}'")
    conn.close()


def cmd_sql(query):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query)
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


def cmd_exec(sql):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print(f"OK — {cur.rowcount} row(s) affected")
    conn.close()


def cmd_add_fact(args):
    if len(args) < 3:
        print("Usage: fp add-fact <topic> <key> <value> [source]")
        return
    topic, key, value = args[0], args[1], args[2]
    source = args[3] if len(args) > 3 else None
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO fp_facts (topic, key, value, source) VALUES (%s, %s, %s, %s)",
        (topic, key, value, source),
    )
    conn.commit()
    print(f"Added fact: {topic}.{key}")
    conn.close()


def cmd_add_task(args):
    if len(args) < 1:
        print("Usage: fp add-task <action> [priority] [due_date] [category]")
        return
    action = args[0]
    priority = args[1] if len(args) > 1 else "P2"
    due_date = args[2] if len(args) > 2 else None
    category = args[3] if len(args) > 3 else None
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO fp_tasks (action, priority, due_date, category) VALUES (%s, %s, %s, %s)",
        (action, priority, due_date, category),
    )
    conn.commit()
    print(f"Added task: {action}")
    conn.close()


def cmd_complete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE fp_tasks SET status='DONE', updated_at=CURRENT_TIMESTAMP WHERE id=%s",
        (task_id,),
    )
    conn.commit()
    print(f"Task {task_id} marked DONE")
    conn.close()


def cmd_set(args):
    if len(args) < 4:
        print("Usage: fp set <table> <id> <column> <value>")
        return
    table, row_id, column, value = args[0], args[1], args[2], args[3]
    allowed_tables = {"people": "fp_people", "documents": "fp_documents", "key_dates": "fp_key_dates", 
                      "finances": "fp_finances", "tasks": "fp_tasks", "facts": "fp_facts", "addresses": "fp_addresses"}
    if table not in allowed_tables:
        print(f"Table must be one of: {', '.join(sorted(allowed_tables.keys()))}")
        return
    if not re.match(r"^[a-z_]+$", column):
        print("Invalid column name")
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE {allowed_tables[table]} SET {column}=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s",
        (value, row_id),
    )
    conn.commit()
    print(f"Updated {table}.{column} for id {row_id}")
    conn.close()


def cmd_finances(asset_type=None, country=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = "SELECT category, asset_type, country, key, value, notes FROM fp_finances WHERE 1=1"
    params = []
    if asset_type:
        query += " AND asset_type=%s"
        params.append(asset_type)
    if country:
        query += " AND country=%s"
        params.append(country)
    query += " ORDER BY country, asset_type, key"
    cur.execute(query, params)
    rows = cur.fetchall()
    print(fmt_rows(rows))
    conn.close()


SENSITIVE_COLUMNS_MAP = {
    "fp_documents": ["doc_number"]
}


def cmd_dump():
    output_content = ""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'fp_%'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]

    for table_name in tables:
        output_content += f"## {table_name}\n\n"
        
        cur.execute(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = %s ORDER BY ordinal_position
        """, (table_name,))
        all_column_names = [col[0] for col in cur.fetchall()]

        cur.execute(f"SELECT * FROM {table_name}")
        rows_data = cur.fetchall()

        processed_rows = []
        for row_tuple in rows_data:
            processed_row = {}
            for i, col_name in enumerate(all_column_names):
                val = row_tuple[i]
                if table_name in SENSITIVE_COLUMNS_MAP and col_name in SENSITIVE_COLUMNS_MAP[table_name]:
                    processed_row[col_name] = "[REDACTED]" if val is not None else None
                else:
                    processed_row[col_name] = val
            processed_rows.append(processed_row)

        if processed_rows:
            output_content += fmt_rows_for_llm(processed_rows, all_column_names) + "\n\n"
        else:
            output_content += "(no records)\n\n"

    conn.close()
    print(output_content)


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    cmd = args[0]
    rest = args[1:]

    commands = {
        "init": lambda: cmd_init(),
        "balances": lambda: cmd_balances(),
        "net-worth": lambda: cmd_net_worth(),
        "tasks": lambda: cmd_tasks(),
        "dates": lambda: cmd_dates(rest[0] if rest else None),
        "people": lambda: cmd_people(),
        "docs": lambda: cmd_docs(rest[0] if rest else None),
        "facts": lambda: cmd_facts(rest[0] if rest else None),
        "finances": lambda: cmd_finances(rest[0] if rest else None, rest[1] if len(rest) > 1 else None),
        "search": lambda: cmd_search(rest[0]) if rest else print("Usage: fp search <term>"),
        "sql": lambda: cmd_sql(" ".join(rest)) if rest else print("Usage: fp sql <query>"),
        "exec": lambda: cmd_exec(" ".join(rest)) if rest else print("Usage: fp exec <sql>"),
        "add-fact": lambda: cmd_add_fact(rest),
        "add-task": lambda: cmd_add_task(rest),
        "complete-task": lambda: cmd_complete_task(rest[0]) if rest else print("Usage: fp complete-task <id>"),
        "set": lambda: cmd_set(rest),
        "dump": lambda: cmd_dump(),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
