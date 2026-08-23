#!/usr/bin/env bash

set -euo pipefail

# Load .env
if [[ -f ".env" ]]; then
    set -a
    source ".env"
    set +a
fi

DATABASE="${TARGET_DATABASE:-${POSTGRES_DB:-}}"
USER="${POSTGRES_USER:-}"
HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5432}"

if [[ -z "$DATABASE" ]]; then
    echo "Error: POSTGRES_DB is not set in .env" >&2
    exit 1
fi

if [[ -z "$USER" ]]; then
    echo "Error: POSTGRES_USER is not set in .env" >&2
    exit 1
fi

echo "Connecting to database '$DATABASE' as user '$USER' on $HOST:$PORT"

for file in migrations/*.sql; do
    echo "Applying migration: $file"

    psql \
        -h "$HOST" \
        -p "$PORT" \
        -U "$USER" \
        -d "$DATABASE" \
        -v ON_ERROR_STOP=1 \
        -f "$file"
done

for file in seed/*.sql; do
    echo "Loading seed: $file"

    psql \
        -h "$HOST" \
        -p "$PORT" \
        -U "$USER" \
        -d "$DATABASE" \
        -v ON_ERROR_STOP=1 \
        -f "$file"
done

echo "Database successfully migrated and seeded."
