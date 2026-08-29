#!/bin/sh
set -e

if [ "$COLLECTSTATIC" = "1" ];
then
  python manage.py collectstatic --noinput
fi

exec "$@"