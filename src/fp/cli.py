#!/usr/bin/env python3
"""fp — Family Planner CLI for mox.db"""

import os
import re
import sqlite3
import sys
from datetime import datetime

DB_PATH = os.path.expanduser(os.environ.get("FP_DB", "~/projects/_openclaw/family-planning.db"))

USAGE = """\
fp — Family Planner CLI

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
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fmt_rows(rows, columns=None):
    if not rows:
        return "(no results)"
    if columns is None:
        columns = rows[0].keys() if hasattr(rows[0], "keys") else [f"col{i}" for i in range(len(rows[0]))]
    lines = []
    for row in rows:
        parts = []
        for col in columns:
            val = row[col] if hasattr(row, "keys") else row[columns.index(col)]
            if val is not None:
                parts.append(f"{col}: {val}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def fmt_rows_for_llm(rows, column_names): # Added column_names parameter
    if not rows:
        return "(no records)"
    
    # Column names are now passed explicitly
    columns = column_names
    if not columns:
        return "(no records)"

    # Format header
    header = "| " + " | ".join(columns) + " |\n"
    # Generate separator dynamically
    separator_parts = []
    for col in columns:
        # Minimum width of 3 for markdown table (e.g., ---)
        separator_parts.append("-" * max(3, len(col))) 
    separator = "|-" + "-|-".join(separator_parts) + "-|\n"

    # Format rows
    data_rows = []
    for row_tuple in rows: # Iterate over tuple elements
        formatted_values = []
        for val in row_tuple: # val is directly the value from the tuple
            val_str = str(val) if val is not None else ""
            # Escape markdown table breaking characters and newlines
            val_str = val_str.replace('|', '\\|').replace('\n', '\\n')
            formatted_values.append(val_str)
        data_rows.append("| " + " | ".join(formatted_values) + " |")
    
    return header + separator + "\n".join(data_rows)



def cmd_balances():
    db = get_db()
    rows = db.execute(
        "SELECT key, value, notes FROM finances WHERE category='banking' ORDER BY key"
    ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_net_worth():
    db = get_db()
    rows = db.execute(
        "SELECT key, value, notes, category, asset_type, country FROM finances ORDER BY key"
    ).fetchall()
    total_cad_equivalent = 0.0
    
    print("--- Detailed Net Worth Calculation ---")
    for r in rows:
        value_str = r["value"] or ""
        notes_str = r["notes"] or ""
        asset_cad = 0.0
        processed = False

        # Prioritize CAD equivalent from notes
        cad_equiv_match = re.search(r"CAD equivalent:\s*([\d,.]+)", notes_str)
        if not cad_equiv_match:
            cad_equiv_match = re.search(r"([\d,.]+)\s*CAD", notes_str, re.IGNORECASE)

        if cad_equiv_match:
            # Clean the extracted string for float conversion (remove commas, ensure only one dot)
            numeric_str = re.sub(r'[^\d.]', '', cad_equiv_match.group(1)).strip('.')
            try:
                asset_cad = float(numeric_str)
                print(f"  - {r['key']} ({r['value']}): {asset_cad:,.2f} CAD (from notes)")
                processed = True
            except ValueError:
                print(f"  - {r['key']} ({r['value']}): Could not convert '{numeric_str}' from notes to float, skipping.")

        if not processed:
            # If not processed by notes, try to parse directly if it looks like CAD in value_str
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
            # Fallback for raw numbers without explicit currency if no CAD equivalent
            numeric_match = re.search(r"[\d,.]+", value_str.replace(",", ""))
            if numeric_match:
                amount = float(numeric_match.group())
                # Attempt a rough conversion for SGD if it's the only info
                if "SGD" in value_str.upper() or "SGD" in notes_str.upper():
                    asset_cad = amount * 0.95 # Approximate SGD->CAD rate
                    print(f"  - {r['key']} ({r['value']}): {asset_cad:,.2f} CAD (approx SGD->CAD)")
                    processed = True
                elif "VND" in value_str.upper() or "VND" in notes_str.upper():
                    # If VND, and not processed by notes, and no direct CAD:
                    print(f"  - {r['key']} ({r['value']}): VND amount, no explicit CAD conversion found, skipping for now.")
                else:
                    print(f"  - {r['key']} ({r['value']}): No currency or explicit CAD equivalent found, skipping for now.")
            else:
                # This could catch values like "active", "unemployed" etc.
                print(f"  - {r['key']} ({r['value']}): Could not parse numeric value, skipping.")
        
        total_cad_equivalent += asset_cad
        
    print("------------------------------------")
    print(f"Total Net Worth (approx CAD): {total_cad_equivalent:,.2f}")
    db.close()


def cmd_tasks():
    db = get_db()
    rows = db.execute(
        "SELECT id, action, status, priority, due_date, category FROM tasks WHERE status != 'DONE' ORDER BY priority, due_date"
    ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_dates(category=None):
    db = get_db()
    if category:
        rows = db.execute(
            "SELECT label, date, category, notes FROM key_dates WHERE category=? ORDER BY date",
            (category,),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT label, date, category, notes FROM key_dates ORDER BY date"
        ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_people():
    db = get_db()
    rows = db.execute(
        "SELECT id, name, relation, dob, notes FROM people ORDER BY id"
    ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_docs(person=None):
    db = get_db()
    if person:
        rows = db.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM documents d JOIN people p ON d.person_id=p.id
               WHERE p.name LIKE ? ORDER BY p.name, d.doc_type""",
            (f"%{person}%",),
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM documents d JOIN people p ON d.person_id=p.id ORDER BY p.name, d.doc_type"""
        ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_facts(topic=None):
    db = get_db()
    if topic:
        rows = db.execute(
            "SELECT topic, key, value, source FROM facts WHERE topic LIKE ? ORDER BY topic, key",
            (f"%{topic}%",),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT topic, key, value FROM facts ORDER BY topic, key"
        ).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_search(term):
    db = get_db()
    pattern = f"%{term}%"
    tables = {
        "facts": "SELECT 'facts' as tbl, topic||'.'||key as item, value FROM facts WHERE topic LIKE ? OR key LIKE ? OR value LIKE ?",
        "tasks": "SELECT 'tasks' as tbl, action as item, notes as value FROM tasks WHERE action LIKE ? OR notes LIKE ? OR category LIKE ?",
        "key_dates": "SELECT 'key_dates' as tbl, label as item, notes as value FROM key_dates WHERE label LIKE ? OR notes LIKE ? OR category LIKE ?",
        "people": "SELECT 'people' as tbl, name as item, notes as value FROM people WHERE name LIKE ? OR notes LIKE ? OR relation LIKE ?",
        "finances": "SELECT 'finances' as tbl, category||'.'||key as item, value FROM finances WHERE key LIKE ? OR value LIKE ? OR notes LIKE ?",
    }
    results = []
    for tbl, sql in tables.items():
        rows = db.execute(sql, (pattern, pattern, pattern)).fetchall()
        results.extend(rows)
    if results:
        for r in results:
            print(f"[{r['tbl']}] {r['item']}: {r['value']}")
    else:
        print(f"No results for '{term}'")
    db.close()


def cmd_sql(query):
    db = get_db()
    rows = db.execute(query).fetchall()
    print(fmt_rows(rows))
    db.close()


def cmd_exec(sql):
    db = get_db()
    cursor = db.execute(sql)
    db.commit()
    print(f"OK — {cursor.rowcount} row(s) affected")
    db.close()


def cmd_add_fact(args):
    if len(args) < 3:
        print("Usage: fp add-fact <topic> <key> <value> [source]")
        return
    topic, key, value = args[0], args[1], args[2]
    source = args[3] if len(args) > 3 else None
    db = get_db()
    db.execute(
        "INSERT INTO facts (topic, key, value, source) VALUES (?, ?, ?, ?)",
        (topic, key, value, source),
    )
    db.commit()
    print(f"Added fact: {topic}.{key}")
    db.close()


def cmd_add_task(args):
    if len(args) < 1:
        print("Usage: fp add-task <action> [priority] [due_date] [category]")
        return
    action = args[0]
    priority = args[1] if len(args) > 1 else "P2"
    due_date = args[2] if len(args) > 2 else None
    category = args[3] if len(args) > 3 else None
    db = get_db()
    db.execute(
        "INSERT INTO tasks (action, priority, due_date, category) VALUES (?, ?, ?, ?)",
        (action, priority, due_date, category),
    )
    db.commit()
    print(f"Added task: {action}")
    db.close()


def cmd_complete_task(task_id):
    db = get_db()
    db.execute(
        "UPDATE tasks SET status='DONE', updated_at=datetime('now') WHERE id=?",
        (task_id,),
    )
    db.commit()
    print(f"Task {task_id} marked DONE")
    db.close()


def cmd_set(args):
    if len(args) < 4:
        print("Usage: fp set <table> <id> <column> <value>")
        return
    table, row_id, column, value = args[0], args[1], args[2], args[3]
    # Whitelist tables and validate column names
    allowed_tables = {"people", "documents", "key_dates", "finances", "tasks", "facts", "addresses"}
    if table not in allowed_tables:
        print(f"Table must be one of: {', '.join(sorted(allowed_tables))}")
        return
    if not re.match(r"^[a-z_]+$", column):
        print("Invalid column name")
        return
    db = get_db()
    db.execute(
        f"UPDATE {table} SET {column}=?, updated_at=datetime('now') WHERE id=?",
        (value, row_id),
    )
    db.commit()
    print(f"Updated {table}.{column} for id {row_id}")
    db.close()


def cmd_finances(asset_type=None, country=None):
    db = get_db()
    query = "SELECT category, asset_type, country, key, value, notes FROM finances WHERE 1=1"
    params = []
    if asset_type:
        query += " AND asset_type=?"
        params.append(asset_type)
    if country:
        query += " AND country=?"
        params.append(country)
    query += " ORDER BY country, asset_type, key"
    rows = db.execute(query, params).fetchall()
    print(fmt_rows(rows))
    db.close()

SENSITIVE_COLUMNS_MAP = {
    "documents": ["doc_number"]
}

def cmd_dump():
    output_content = ""

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table_name in tables:
        output_content += f"## {table_name}\n\n"
        
        cursor.execute(f"PRAGMA table_info({table_name});")
        column_info = cursor.fetchall()
        all_column_names = [col[1] for col in column_info]

        cursor.execute(f"SELECT * FROM {table_name};")
        rows_data = cursor.fetchall()

        processed_rows = []
        for row_tuple in rows_data:
            processed_row = []
            for i, col_name in enumerate(all_column_names):
                val = row_tuple[i]
                if table_name in SENSITIVE_COLUMNS_MAP and col_name in SENSITIVE_COLUMNS_MAP[table_name]:
                    processed_row.append("[REDACTED]" if val is not None else None)
                else:
                    processed_row.append(val)
            processed_rows.append(tuple(processed_row)) # Convert list back to tuple

        if processed_rows:
            output_content += fmt_rows_for_llm(processed_rows, all_column_names) + "\n\n"
        else:
            output_content += "(no records)\n\n"

    db.close()
    print(output_content) # Print to stdout # Print to stdout


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    cmd = args[0]
    rest = args[1:]

    commands = {
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
        "dump": lambda: cmd_dump(), # New command
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
