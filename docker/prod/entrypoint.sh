#!/bin/sh

# Database
echo "[Entrypoint] Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

echo "[Entrypoint] PostgreSQL started"

# Proceed with given program
exec "$@"
