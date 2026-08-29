#!/bin/sh
set -eu

BACKUP_DIR=/backups
KEEP_DAYS=7

backup() {
    file="$BACKUP_DIR/${DB_NAME}_$(date +%Y-%m-%d_%H-%M).sql.gz"
    pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" | gzip > "$file"
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +"$KEEP_DAYS" -delete
    echo "Бэкап готов: $file"
}

trap exit TERM

while true; do
    backup
    sleep 24h & wait $!
done