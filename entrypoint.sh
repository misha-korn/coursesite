#!/bin/sh
set -e

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"

if [ "$COLLECTSTATIC" = "1" ];
then
  python manage.py collectstatic --noinput
fi

exec "$@"