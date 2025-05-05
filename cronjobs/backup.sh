#!/bin/bash

# Set backup directory
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/appdb_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run pg_dump and compress the output
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h $POSTGRES_HOST \
    -U $POSTGRES_USER \
    -d $POSTGRES_DB \
    | gzip > "$BACKUP_FILE"

# Keep only the last 7 days of backups
find "$BACKUP_DIR" -type f -mtime +7 -name "appdb_*.sql.gz" -exec rm {} \;

echo "Backup completed: $BACKUP_FILE"
