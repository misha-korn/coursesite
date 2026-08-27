#!/bin/sh
trap exit TERM

while true; do
  nginx -s reload
  sleep 6h & wait $!
done