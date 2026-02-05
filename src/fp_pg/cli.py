#!/usr/bin/env python3
"""fp_pg — PostgreSQL Family Planner CLI"""

import os
import sys
import re
from datetime import datetime
import psycopg2

# PostgreSQL connection using environment variables
def get_db():
    conn = psycopg2.connect(
        host=os.environ.get("PT_DB_HOST", "localhost"),
        port=int(os.environ.get("PT_DB_PORT", 5433)),
        database=os.environ.get("PT_DB_NAME", "financial_analysis"),
        user=os.environ.get("PT_DB_USER", "finance_user"),
        password=os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
    )
    conn.cursor().execute("SET SESSION application_name = 'fp_pg';")
    return conn

USAGE = """\
fp_pg — PostgreSQL Family Planner CLI

Usage: fp_pg <command> [args]

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
"""

def fmt_rows(rows, columns=None):
    if not rows:
        return "(no results)"
    if columns is None:
        # For psycopg2, get column names from cursor description if available
        columns = [desc[0] for desc in rows.cursor.description] if hasattr(rows, 'cursor') else []
        if not columns and len(rows) > 0:
            # Fallback: assume we have a row with keys or use indices
            if hasattr(rows[0], '_mapping'):  # Row with column access
                columns = list(rows[0]._mapping.keys())
            else:
                columns = [f"col{i}" for i in range(len(rows[0]))]
    
    lines = []
    for row in rows:
        parts = []
        for i, col in enumerate(columns):
            # Handle both dict-like and tuple-like rows
            try:
                val = row[col] if hasattr(row, '__getitem__') and not isinstance(row, (str, bytes)) else row[i]
            except (TypeError, IndexError):
                val = row[i] if i < len(row) else None
            
            if val is not None:
                parts.append(f"{col}: {val}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def fmt_rows_for_llm(rows, column_names):
    if not rows:
        return "(no records)"
    
    # Column names are passed explicitly
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
    for row_tuple in rows:
        formatted_values = []
        for val in row_tuple:
            val_str = str(val) if val is not None else ""
            # Escape markdown table breaking characters and newlines
            val_str = val_str.replace('|', '\\|').replace('\n', '\\n')
            formatted_values.append(val_str)
        data_rows.append("| " + " | ".join(formatted_values) + " |")
    
    return header + separator + "\n".join(data_rows)


def cmd_balances():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT key, value, notes FROM family_finances WHERE category='banking' ORDER BY key"
    )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_net_worth():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT key, value, notes, category, asset_type, country FROM family_finances ORDER BY key"
    )
    rows = cursor.fetchall()
    total_cad_equivalent = 0.0
    
    print("--- Detailed Net Worth Calculation ---")
    for r in rows:
        key, value, notes, category, asset_type, country = r
        value_str = value or ""
        notes_str = notes or ""
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
                print(f"  - {key} ({value}): {asset_cad:,.2f} CAD (from notes)")
                processed = True
            except ValueError:
                print(f"  - {key} ({value}): Could not convert '{numeric_str}' from notes to float, skipping.")

        if not processed:
            # If not processed by notes, try to parse directly if it looks like CAD in value_str
            cad_match = re.search(r"CAD\s*([\d,.]+)", value_str)
            if not cad_match:
                cad_match = re.search(r"([\d,.]+)\s*CAD", value_str)
            
            if cad_match:
                numeric_str = re.sub(r'[^\d.]', '', cad_match.group(1)).strip('.')
                try:
                    asset_cad = float(numeric_str)
                    print(f"  - {key} ({value}): {asset_cad:,.2f} CAD (direct from value)")
                    processed = True
                except ValueError:
                    print(f"  - {key} ({value}): Could not convert '{numeric_str}' from value to float, skipping.")

        if not processed:
            # Fallback for raw numbers without explicit currency if no CAD equivalent
            numeric_match = re.search(r"[\d,.]+", value_str.replace(",", ""))
            if numeric_match:
                amount = float(numeric_match.group())
                # Attempt a rough conversion for SGD if it's the only info
                if "SGD" in value_str.upper() or "SGD" in notes_str.upper():
                    asset_cad = amount * 0.95 # Approximate SGD->CAD rate
                    print(f"  - {key} ({value}): {asset_cad:,.2f} CAD (approx SGD->CAD)")
                    processed = True
                elif "VND" in value_str.upper() or "VND" in notes_str.upper():
                    # If VND, and not processed by notes, and no direct CAD:
                    print(f"  - {key} ({value}): VND amount, no explicit CAD conversion found, skipping for now.")
                else:
                    print(f"  - {key} ({value}): No currency or explicit CAD equivalent found, skipping for now.")
            else:
                # This could catch values like "active", "unemployed" etc.
                print(f"  - {key} ({value}): Could not parse numeric value, skipping.")
        
        total_cad_equivalent += asset_cad
        
    print("------------------------------------")
    print(f"Total Net Worth (approx CAD): {total_cad_equivalent:,.2f}")
    db.close()


def cmd_tasks():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, action, status, priority, due_date, category FROM family_tasks WHERE status != 'DONE' ORDER BY priority, due_date"
    )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_dates(category=None):
    db = get_db()
    cursor = db.cursor()
    if category:
        cursor.execute(
            "SELECT label, date, category, notes FROM family_key_dates WHERE category=%s ORDER BY date",
            (category,)
        )
    else:
        cursor.execute(
            "SELECT label, date, category, notes FROM family_key_dates ORDER BY date"
        )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_people():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, relation, dob, notes FROM family_people ORDER BY id"
    )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_docs(person=None):
    db = get_db()
    cursor = db.cursor()
    if person:
        cursor.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM family_documents d JOIN family_people p ON d.person_id=p.id
               WHERE p.name LIKE %s ORDER BY p.name, d.doc_type""",
            (f"%{person}%",)
        )
    else:
        cursor.execute(
            """SELECT d.doc_type, d.doc_number, d.country, d.issued, d.expires, d.notes, p.name
               FROM family_documents d JOIN family_people p ON d.person_id=p.id ORDER BY p.name, d.doc_type"""
        )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_facts(topic=None):
    db = get_db()
    cursor = db.cursor()
    if topic:
        cursor.execute(
            "SELECT topic, key, value, source FROM family_facts WHERE topic LIKE %s ORDER BY topic, key",
            (f"%{topic}%",)
        )
    else:
        cursor.execute(
            "SELECT topic, key, value, source FROM family_facts ORDER BY topic, key"
        )
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_search(term):
    db = get_db()
    cursor = db.cursor()
    pattern = f"%{term}%"
    tables = {
        "facts": "SELECT 'facts' as tbl, topic||'.'||key as item, value FROM family_facts WHERE topic LIKE %s OR key LIKE %s OR value LIKE %s",
        "tasks": "SELECT 'tasks' as tbl, action as item, notes as value FROM family_tasks WHERE action LIKE %s OR notes LIKE %s OR category LIKE %s",
        "key_dates": "SELECT 'key_dates' as tbl, label as item, notes as value FROM family_key_dates WHERE label LIKE %s OR notes LIKE %s OR category LIKE %s",
        "people": "SELECT 'people' as tbl, name as item, notes as value FROM family_people WHERE name LIKE %s OR notes LIKE %s OR relation LIKE %s",
        "finances": "SELECT 'finances' as tbl, category||'.'||key as item, value FROM family_finances WHERE key LIKE %s OR value LIKE %s OR notes LIKE %s",
    }
    results = []
    for tbl, sql in tables.items():
        cursor.execute(sql, (pattern, pattern, pattern))
        rows = cursor.fetchall()
        results.extend(rows)
    if results:
        for r in results:
            print(f"[{r[0]}] {r[1]}: {r[2]}")  # tbl, item, value
    else:
        print(f"No results for '{term}'")
    db.close()


def cmd_sql(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_exec(sql):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    print(f"OK — {cursor.rowcount} row(s) affected")
    db.close()


def cmd_add_fact(args):
    if len(args) < 3:
        print("Usage: fp_pg add-fact <topic> <key> <value> [source]")
        return
    topic, key, value = args[0], args[1], args[2]
    source = args[3] if len(args) > 3 else None
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO family_facts (topic, key, value, source) VALUES (%s, %s, %s, %s)",
        (topic, key, value, source),
    )
    db.commit()
    print(f"Added fact: {topic}.{key}")
    db.close()


def cmd_add_task(args):
    if len(args) < 1:
        print("Usage: fp_pg add-task <action> [priority] [due_date] [category]")
        return
    action = args[0]
    priority = args[1] if len(args) > 1 else "P2"
    due_date = args[2] if len(args) > 2 else None
    category = args[3] if len(args) > 3 else None
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO family_tasks (action, priority, due_date, category) VALUES (%s, %s, %s, %s)",
        (action, priority, due_date, category),
    )
    db.commit()
    print(f"Added task: {action}")
    db.close()


def cmd_complete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE family_tasks SET status='DONE', updated_at=NOW() WHERE id=%s",
        (task_id,)
    )
    db.commit()
    print(f"Task {task_id} marked DONE")
    db.close()


def cmd_set(args):
    if len(args) < 4:
        print("Usage: fp_pg set <table> <id> <column> <value>")
        return
    table, row_id, column, value = args[0], args[1], args[2], args[3]
    # Whitelist tables and validate column names
    allowed_tables = {"family_people", "family_documents", "family_key_dates", "family_finances", "family_tasks", "family_facts", "family_addresses"}
    if table not in allowed_tables:
        print(f"Table must be one of: {', '.join(sorted(allowed_tables))}")
        return
    if not re.match(r"^[a-z_]+$", column):
        print("Invalid column name")
        return
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"UPDATE {table} SET {column}=%s, updated_at=NOW() WHERE id=%s",
        (value, row_id),
    )
    db.commit()
    print(f"Updated {table}.{column} for id {row_id}")
    db.close()


def cmd_finances(asset_type=None, country=None):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT category, asset_type, country, key, value, notes FROM family_finances WHERE TRUE"
    params = []
    if asset_type:
        query += " AND asset_type=%s"
        params.append(asset_type)
    if country:
        query += " AND country=%s"
        params.append(country)
    query += " ORDER BY country, asset_type, key"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    # Get column names
    col_names = [desc[0] for desc in cursor.description]
    print(fmt_rows_for_llm(rows, col_names))
    db.close()


def cmd_dump():
    output_content = ""

    db = get_db()
    cursor = db.cursor()

    # Get all table names that start with 'family_'
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'family_%'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cursor.fetchall()]

    for table_name in tables:
        output_content += f"## {table_name}\n\n"
        
        cursor.execute(f"SELECT * FROM {table_name};")
        rows_data = cursor.fetchall()

        if rows_data:
            # Get column names for the table
            col_names = [desc[0] for desc in cursor.description]
            output_content += fmt_rows_for_llm(rows_data, col_names) + "\n\n"
        else:
            output_content += "(no records)\n\n"

    db.close()
    print(output_content)  # Print to stdout


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
        "search": lambda: cmd_search(rest[0]) if rest else print("Usage: fp_pg search <term>"),
        "sql": lambda: cmd_sql(" ".join(rest)) if rest else print("Usage: fp_pg sql <query>"),
        "exec": lambda: cmd_exec(" ".join(rest)) if rest else print("Usage: fp_pg exec <sql>"),
        "add-fact": lambda: cmd_add_fact(rest),
        "add-task": lambda: cmd_add_task(rest),
        "complete-task": lambda: cmd_complete_task(rest[0]) if rest else print("Usage: fp_pg complete-task <id>"),
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