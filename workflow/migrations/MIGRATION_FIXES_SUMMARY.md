# Migration Fixes for PostgreSQL Compatibility

## Problem
Several migrations contained SQLite-specific SQL that failed when running on PostgreSQL:
- `sqlite_master` table queries
- `PRAGMA table_info()` commands

## Files Fixed

### 1. `0057_replace_fix_clienteentrevista_table.py`
**Original Issue:** Used `sqlite_master` to check table existence
**Fix:** Replaced with PostgreSQL's `information_schema.tables`

```sql
-- OLD (SQLite)
SELECT name FROM sqlite_master WHERE type='table' AND name='workflow_clienteentrevista';

-- NEW (PostgreSQL)
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'workflow_clienteentrevista'
);
```

### 2. `0058_emergency_clienteentrevista_noop.py`
**Original Issue:** Used `sqlite_master` in RunSQL migration
**Fix:** Replaced with PostgreSQL's `information_schema.tables`

### 3. `0031_auto_20250724_2158.py`
**Original Issue:** Used `PRAGMA table_info()` to check column existence
**Fix:** Replaced with PostgreSQL's `information_schema.columns`

```sql
-- OLD (SQLite)
PRAGMA table_info(table_name)

-- NEW (PostgreSQL)
SELECT EXISTS (
    SELECT FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = %s
    AND column_name = %s
);
```

### 4. `0031_auto_20250724_2158_fixed.py`
**Original Issue:** Same as above
**Fix:** Same PostgreSQL-compatible solution

## Result
All migrations should now run successfully on PostgreSQL without the error:
```
psycopg2.errors.UndefinedTable: relation "sqlite_master" does not exist
```

## Backup Files Created
- `0057_replace_fix_clienteentrevista_table.py.backup` - Original SQLite version

## Testing
After these fixes, run:
```bash
python manage.py migrate
```

The migration should complete successfully without SQLite-related errors.
