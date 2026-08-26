#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load manifest
source "$ROOT_DIR/manifest.env"

# PostgreSQL connection settings
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-postgres}"
export PGDATABASE="${PGDATABASE:-we_trade}"

pass() {
    echo "✅ PASS: $1"
}

fail() {
    echo "❌ FAIL: $1"
    exit 1
}


echo "================================="
echo " PostgreSQL Harness Check"
echo "================================="

echo
echo "Checking database connection..."

psql -v ON_ERROR_STOP=1 -c "SELECT 1;" >/dev/null \
    || fail "Unable to connect to PostgreSQL"

pass "Database connection successful"


echo
echo "Checking account state values..."

echo
echo "Checking account state values..."

INVALID_COUNT=$(psql -tAc "
SELECT COUNT(*)
FROM $ACCOUNTS_TABLE
WHERE $ACCOUNTS_STATE_COLUMN::text NOT IN (
    '$ACCOUNT_STATE_VALUE_1',
    '$ACCOUNT_STATE_VALUE_2',
    '$ACCOUNT_STATE_VALUE_3'
);
")

if [ "$INVALID_COUNT" -eq 0 ]; then
    pass "Account states are valid"
else
    fail "Invalid account states found: $INVALID_COUNT"
fi


echo
echo "Checking duplicate idempotency keys already stored..."

DUPLICATE_COUNT=$(psql -tAc "
SELECT COUNT(*)
FROM (
    SELECT $ORDERS_IDEMPOTENCY_KEY_COLUMN, COUNT(*)
    FROM $ORDERS_TABLE
    GROUP BY $ORDERS_IDEMPOTENCY_KEY_COLUMN
    HAVING COUNT(*) > 1
) duplicates;
")

if [ "$DUPLICATE_COUNT" -eq 0 ]; then
    pass "No duplicate idempotency keys found"
else
    fail "Duplicate idempotency keys exist"
fi


echo
echo "Testing duplicate idempotency key rejection..."

if psql \
    -v ON_ERROR_STOP=1 \
    -f "$ROOT_DIR/probes/duplicate-idempotency-key.sql" \
    >/tmp/duplicate-idempotency.log 2>&1
then
    fail "Duplicate idempotency key was accepted"
else
    pass "Duplicate idempotency key rejected"
fi


echo
echo "Testing orphan foreign key rejection..."

if psql \
    -v ON_ERROR_STOP=1 \
    -f "$ROOT_DIR/probes/orphan-foreign-key.sql" \
    >/tmp/orphan-foreign-key.log 2>&1
then
    fail "Orphan account reference was accepted"
else
    pass "Foreign key rejected orphan order"
fi


echo
echo "Checking foreign key constraint..."

FK_COUNT=$(psql -tAc "
SELECT COUNT(*)
FROM information_schema.table_constraints
WHERE table_name='$ORDERS_TABLE'
AND constraint_type='FOREIGN KEY';
")

if [ "$FK_COUNT" -gt 0 ]; then
    pass "Foreign key constraint exists"
else
    fail "Missing foreign key constraint"
fi


echo
echo "Checking idempotency unique constraint/index..."

IDEMPOTENCY_INDEX=$(psql -tAc "
SELECT COUNT(*)
FROM pg_indexes
WHERE tablename='$ORDERS_TABLE'
AND indexdef ILIKE '%$ORDERS_IDEMPOTENCY_KEY_COLUMN%';
")

if [ "$IDEMPOTENCY_INDEX" -gt 0 ]; then
    pass "Idempotency key index exists"
else
    fail "Missing idempotency key unique index"
fi


echo
echo "================================="
echo " 🎉 All checks passed"
echo "================================="