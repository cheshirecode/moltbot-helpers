"""
DEPRECATION NOTICE

The legacy SQLite versions of these tools are being deprecated in favor of PostgreSQL-powered versions.

Please use:
- `pt_pg` instead of `pt` for project tracking
- `seek_pg` instead of `seek` for semantic search  
- `fp_pg` instead of `fp` for family planning

Legacy tools will be removed in future releases. All data has been migrated to PostgreSQL.
"""
import sys

def show_deprecation_warning(tool_name):
    """Show deprecation warning for legacy tool."""
    print(f"⚠️  DEPRECATION WARNING: {tool_name} is deprecated", file=sys.stderr)
    print(f"⚠️  Please use {tool_name}_pg instead", file=sys.stderr)
    print(f"⚠️  Legacy tools will be removed in future releases", file=sys.stderr)
    print("", file=sys.stderr)