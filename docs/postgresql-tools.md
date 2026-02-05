# PostgreSQL-Powered Tools Documentation

This document describes the new PostgreSQL-powered versions of the tools, which replace the legacy SQLite versions.

## Overview

All tools have been migrated from SQLite to PostgreSQL for better scalability, reliability, and advanced features. The new tools maintain the same interfaces while offering improved performance and capabilities.

## Tool Mappings

| Legacy (SQLite) | New (PostgreSQL) | Status |
|----------------|------------------|---------|
| `pt` | `pt_pg` | ✅ Complete |
| `seek` | `seek_pg` | ✅ Complete |
| `fp` | `fp_pg` | ✅ Complete |

## PostgreSQL Tools

### pt_pg - PostgreSQL Project Tracker

The PostgreSQL-powered project tracker with enhanced capabilities:

```bash
# List projects
pt_pg --project myproject list

# Add a task
pt_pg --project myproject add "New task" --priority high

# Search tasks
pt_pg --project myproject search "keyword"
```

### seek_pg - PostgreSQL Semantic Search

The PostgreSQL-powered semantic search engine:

```bash
# Search across indexed content
seek_pg search "query terms"

# View status
seek_pg status

# Index new content (requires environment configuration)
SEEK_INDEX_PATHS="/path/to/index" seek_pg index
```

### fp_pg - PostgreSQL Family Planner

The PostgreSQL-powered family planning tool:

```bash
# View family members
fp_pg people

# View tasks
fp_pg tasks

# View finances
fp_pg finances

# Search across family data
fp_pg search "keyword"
```

## Environment Variables

The PostgreSQL tools use the following environment variables:

```bash
PT_DB_HOST=localhost      # PostgreSQL host
PT_DB_PORT=5433          # PostgreSQL port
PT_DB_NAME=financial_analysis  # Database name
PT_DB_USER=finance_user  # Database user
PT_DB_PASSWORD=secure_finance_password  # Database password
```

## Migration Status

- All data has been migrated from SQLite to PostgreSQL
- New tools are fully functional
- Legacy tools are being deprecated
- Documentation updated to recommend PostgreSQL versions