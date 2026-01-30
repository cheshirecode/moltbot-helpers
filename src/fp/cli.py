#!/usr/bin/env python3
"""fp — Family Planner CLI for mox.db"""

import os
import re
import sqlite3
import sys
from datetime import datetime

DB_PATH = os.path.expanduser(os.environ.get("FP_DB", "~/clawd/memory/mox.db"))

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
  search <term>         Search across all tables
  sql <query>           Run read-only SQL

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
        "SELECT key, value, notes FROM finances WHERE category='banking' ORDER BY key"
    ).fetchall()
    cad_total = 0.0
    sgd_total = 0.0
    for r in rows:
        val = r["value"] or ""
        m = re.search(r"[\d,.]+", val.replace(",", ""))
        if not m:
            continue
        amount = float(m.group())
        if "SGD" in val.upper() or "sgd" in (r["notes"] or "").lower():
            sgd_total += amount
        else:
            cad_total += amount
    print(f"CAD: {cad_total:,.0f}")
    print(f"SGD: {sgd_total:,.0f}")
    # rough conversion
    cad_equiv = sgd_total * 0.95  # approximate SGD->CAD
    print(f"Total (approx CAD): {cad_total + cad_equiv:,.0f}")
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
        "search": lambda: cmd_search(rest[0]) if rest else print("Usage: fp search <term>"),
        "sql": lambda: cmd_sql(" ".join(rest)) if rest else print("Usage: fp sql <query>"),
        "exec": lambda: cmd_exec(" ".join(rest)) if rest else print("Usage: fp exec <sql>"),
        "add-fact": lambda: cmd_add_fact(rest),
        "add-task": lambda: cmd_add_task(rest),
        "complete-task": lambda: cmd_complete_task(rest[0]) if rest else print("Usage: fp complete-task <id>"),
        "set": lambda: cmd_set(rest),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
