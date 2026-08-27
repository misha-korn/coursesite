#!/bin/sh
trap exit TERM

while true; do
  sleep 6h & wait $!
  nginx -s reload
done