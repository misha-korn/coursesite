#!/bin/sh
trap exit TERM

while true; do
  certbot renew --quiet
  sleep 12h & wait $!
done