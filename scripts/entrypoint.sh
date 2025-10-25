#!/bin/bash
set -e

DB_DIR="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/db"
DB_PATH="$DB_DIR/ps9.db"
INIT_SQL="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/scripts/db/init.sql"

mkdir -p "$DB_DIR"

echo "Recreating SQLite database..."
rm -f "$DB_PATH"
sqlite3 "$DB_PATH" < "$INIT_SQL" || echo "SQLite init script had warnings but continuing..."

# Keep container running
tail -f /dev/null
