#!/bin/sh
set -e
echo "Ждём базу..."
until python -c "import socket; socket.create_connection(('db', 5432), timeout=2)" 2>/dev/null; do
  sleep 1
done

if [ "$RUN_MIGRATIONS" = "1" ]; then       # ← только там, где флаг
  python manage.py migrate --noinput
fi

if [ "$COLLECTSTATIC" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"