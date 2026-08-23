```markdown
# Trade Execution Retention and Incremental Extraction Design

## 1. Overview

This document describes how executed trade information is retained, populated, and extracted from the trading database.

The design separates orders from executions because an order represents customer intent, while an execution represents the actual completed trade.

An order may be:

- partially filled
- filled through multiple executions
- executed at different prices

Therefore, execution data is stored separately as the source of truth for completed trades.

---

# 2. Retention Grain

The `execution` table stores data at **execution/fill grain**.

One row represents one completed trade execution.

Example:

An order requests 100 shares:

```

## Order

order_id: ORD001
quantity: 100

```

The market may fill the order in multiple executions:

```

## Execution

## execution_id | order_id | units | price

EX001        | ORD001   | 40    | 100.00
EX002        | ORD001   | 60    | 100.50

```

Each execution record stores:

- `execution_id`
- `order_id`
- executed quantity
- execution price
- execution timestamp

The order table stores the requested transaction, while the execution table stores the actual trade outcome.

---

# 3. Data Retained Beyond the Order

The following information is retained after execution:

| Field | Purpose |
|---|---|
| execution_id | Unique identifier for the completed trade event |
| order_id | Links the execution to the original order |
| units | Number of units actually executed |
| execution_price | Price achieved during execution |
| executed_at | Time the trade completed |

Execution information cannot be derived only from the order because:

- An order quantity may not fully execute.
- Multiple executions may occur for one order.
- Each execution may have a different execution price.
- Execution time differs from order creation time.

---

# 4. Population of Execution Data

Execution records are populated by the execution processing component.

The flow is:

```

Customer
|
v
Order Service
|
v
Order Created
|
v
Broker / Exchange
|
v
Execution Event
|
v
Execution Processor
|
v
Execution Table

````

## Order Service Responsibilities

The Order Service is responsible for:

- accepting customer orders
- creating order records
- managing order lifecycle state

## Execution Processor Responsibilities

The Execution Processor is responsible for:

- consuming execution confirmations
- validating execution events
- creating execution records

Execution records are append-only because they represent historical trade facts.

Existing executions are not modified during normal operation.

---

# 5. Incremental Sprint 7 Extraction Design

## Problem

The extraction process must avoid scanning the entire execution history.

A full scan such as:

```sql
SELECT *
FROM execution;
````

becomes increasingly expensive as execution volume grows.

---

## Solution

The Sprint 7 extract uses incremental extraction with a watermark.

The extraction cursor is:

```
(executed_at, execution_id)
```

The extractor stores the last successfully processed execution position.

Example:

Previous checkpoint:

```
executed_at = 2026-08-20 10:00:00
execution_id = EX1000
```

The next extraction retrieves records after this position:

```sql
SELECT
    execution_id,
    order_id,
    units,
    execution_price,
    executed_at
FROM execution
WHERE
(
    executed_at > :last_executed_at
)
OR
(
    executed_at = :last_executed_at
    AND execution_id > :last_execution_id
)
ORDER BY executed_at, execution_id
LIMIT 10000;
```

After successful processing:

1. The new watermark is stored.
2. The next extraction starts from that position.

---

# 6. Failure Handling and Retry Behaviour

The extraction process is designed to be restartable.

If extraction fails:

* the previous watermark remains unchanged
* the same records can be retrieved again
* downstream processing must handle duplicates safely

This prevents execution records from being lost during failures.

---

# 7. Behaviour at 100x Volume

The design supports growth without requiring a major redesign.

At 100 times the current execution volume:

## Incremental Queries

The extractor does not scan historical executions.

It uses the watermark and index to locate only new records.

## Batch Processing

Executions are extracted in batches.

Benefits:

* controlled memory usage
* smaller database transactions
* easier failure recovery
* predictable processing time

Example:

```
Batch size = 10,000 executions
```

Large execution histories can therefore be processed continuously.

---

# 8. Indexing Strategy

The execution table requires an index supporting incremental extraction.

Recommended index:

```sql
CREATE INDEX idx_execution_incremental_extract
ON execution(executed_at, execution_id);
```

This allows the database to quickly find executions after the previous watermark.

Without this index, the database may need to scan a large portion of historical execution data.

---

# 9. Write Cost and Operational Complexity

The incremental extraction index introduces additional write cost.

Every execution insert performs:

1. Insert execution record.
2. Update extraction index.

The additional write cost is acceptable because execution records are append-heavy and extraction performance is important.

Operational costs include:

* additional index storage
* database maintenance
* backup growth
* watermark management
* monitoring extraction failures

The design intentionally trades a small increase in write cost for significantly better read and extraction performance.

---

# 10. Partitioning Decision

## Decision: Do Not Partition Initially

The initial design does not use database partitioning.

A properly indexed execution table with incremental extraction is sufficient for the expected scale.

Partitioning introduces additional operational complexity:

* partition creation and management
* more complex migrations
* additional monitoring requirements
* more complicated backup and restore processes

The complexity is not justified until the database reaches a scale where measurable performance problems occur.

---

# 11. Future Partitioning Approach

Partitioning will be reconsidered when:

* execution table size becomes difficult to maintain
* index performance decreases
* backups become too large
* query latency increases beyond acceptable limits

If partitioning becomes necessary, time-based partitioning will be used.

Example:

```
execution_2026_01
execution_2026_02
execution_2026_03
```

The partition key would be:

```
executed_at
```

This allows older trade history to be managed independently.

---

# 12. Archival and Retention Strategy

Execution records represent financial trade history and must be retained according to business and compliance requirements.

The active database stores operationally required execution history.

Older executions may be archived to lower-cost storage when:

* retention requirements allow
* operational reporting no longer requires active database access

Archived records remain immutable.

Archiving does not affect incremental extraction because new executions continue using the same watermark-based extraction process.

---

# 13. Final Design Summary

The system retains executions separately from orders because executions represent the actual completed trades.

The retention grain is one row per execution/fill.

Execution records are populated by the Execution Processor after receiving execution confirmations.

Sprint 7 extraction uses watermark-based incremental extraction instead of scanning the entire execution history.

The design supports 100x growth through:

* indexed extraction
* batch processing
* append-only execution storage

Partitioning is intentionally deferred until scale requires it.

This approach balances performance, operational simplicity, and future scalability.

```
```
