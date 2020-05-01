#!/bin/sh

# Database
echo "Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

# Proceed with given program
exec "$@"
