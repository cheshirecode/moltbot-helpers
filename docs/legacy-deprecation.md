# Legacy Tool Deprecation Notice

## Important: Legacy SQLite Tools Being Deprecated

The following legacy tools using SQLite databases are being deprecated in favor of PostgreSQL-powered versions:

### Deprecated Tools
- `pt` → Use `pt_pg` instead
- `seek` → Use `seek_pg` instead  
- `fp` → Use `fp_pg` instead

### Why the Change?

- **Better Performance**: PostgreSQL offers superior performance for larger datasets
- **Enhanced Features**: Advanced querying, full-text search, and analytics capabilities
- **Scalability**: Better handling of concurrent access and larger data volumes
- **Reliability**: More robust transaction handling and crash recovery

### Migration Status

✅ All data has been successfully migrated from SQLite to PostgreSQL  
✅ New PostgreSQL tools are fully functional  
✅ All functionality preserved in new versions  

### Timeline

- **Immediate**: Begin using PostgreSQL versions for all new operations
- **Near-term**: Legacy tools will remain available for read-only access
- **Future**: Legacy tools will be removed entirely

### How to Switch

Simply replace your commands:

```bash
# Instead of:
pt --project myproject list
seek search "query"
fp people

# Use:
pt_pg --project myproject list
seek_pg search "query"
fp_pg people
```

### Support

For questions about the migration, refer to the PostgreSQL tools documentation in `docs/postgresql-tools.md`.