#!/bin/bash
set -e

DB_DIR="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/db_data"
DB_PATH="$DB_DIR/ps9.db"
INIT_SQL="/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/scripts/db/init.sql"

mkdir -p "$DB_DIR"

if [ ! -f "$DB_PATH" ]; then
    echo "Creating SQLite database..."
    sqlite3 "$DB_PATH" < "$INIT_SQL" || echo "SQLite init script had warnings but continuing..."
    echo "Done!"
else
    echo "SQLite database already exists, skipping initialization."
fi

# Keep container running
tail -f /dev/null
