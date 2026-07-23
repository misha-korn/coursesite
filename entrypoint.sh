#!/bin/sh
set -e

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"

echo "Ждём базу..."
until python -c "import socket, os; socket.create_connection((os.environ['DB_HOST'], int(os.environ['DB_PORT'])), timeout=2)" 2>/dev/null;
do
    sleep 1
done

if [ "$RUN_MIGRATIONS" = "1" ];
then
  python manage.py migrate --noinput
fi

if [ "$COLLECTSTATIC" = "1" ];
then
  python manage.py collectstatic --noinput
fi

exec "$@"