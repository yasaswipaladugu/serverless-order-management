# DynamoDB Data Model

## 1. Why DynamoDB?

- DynamoDB is a fully managed NoSQL database provided by AWS.
It was chosen for this project for the following reasons.
- It requires no server management. There are no database servers to provision,
patch, or maintain. This fits the serverless architecture of the project.
- It scales automatically. DynamoDB handles increasing read and write traffic
without any manual configuration changes.
- It integrates natively with Lambda and IAM, making it a natural fit for a
serverless AWS backend.
- It charges on a pay-per-use basis when configured in on-demand mode,
which is cost-conscious for a small project with variable traffic.
- It provides single-digit millisecond latency for key-based lookups,
which is appropriate for an order management system where individual
order retrieval must be fast.

---

## 2. DynamoDB Key Concepts (Explained Simply)

- Before describing the data model, it helps to understand a few DynamoDB concepts.
- A table in DynamoDB is like a collection of items. Each item is like a row,
but items in the same table do not need to have the same attributes.
- Every item must have a primary key. The primary key uniquely identifies the item.
- A primary key can be made up of one or two parts.
- If it is one part, it is called a partition key (also written as PK).
DynamoDB uses the partition key to decide where to store the item physically.
- If it is two parts, the first part is still the partition key (PK)
and the second part is called the sort key (SK).
Items with the same partition key are stored together and sorted by the sort key.
- A Query operation retrieves items that share the same partition key.
This is efficient because DynamoDB knows exactly where to look.
- A Scan operation reads every item in the entire table.
This is inefficient and expensive at scale and must be avoided for normal operations.

---

## 3. The Design Challenge

The project requires two very different access patterns.

1. The first is retrieving a single order by its orderId.
This is straightforward — orderId can be the partition key and DynamoDB
will find the item instantly.
2. The second is retrieving a list of all orders.
This is the challenge. If orderId is the partition key, then each order
is stored in a different partition. To list all orders, DynamoDB would
need to scan the entire table, which is slow and expensive.

To solve this, a composite primary key design is used.

---

## 4. Table Design

Table name: orders

Primary key:
  Partition key (PK): a fixed string value — "ORDER"
  Sort key (SK): the orderId (a UUID)

Because all orders share the same partition key value "ORDER",
they are all stored together in DynamoDB. This means a Query operation
on the partition key "ORDER" will return all orders efficiently,
without needing to scan the entire table.

The sort key orderId makes each item unique within that partition.
A single order can still be retrieved directly using both PK and SK together.

---

## 5. Order Item Attributes

Each order item stored in DynamoDB contains the following attributes.

1. PK — the partition key. Always the string "ORDER" for all orders.
2. SK — the sort key. The unique orderId (UUID) for this specific order.
3. orderId — the unique identifier for the order. Same value as SK.
This is stored as a separate attribute so that it appears clearly in API responses.
4. customerId — the ID of the customer who placed the order.
5. items — the list of products in the order. Each item contains a productId and quantity.
This is stored as a DynamoDB List attribute.
6. totalAmount — the total monetary value of the order. Stored as a Number.
7. status — the current status of the order. One of: PENDING, CONFIRMED, PROCESSING,
SHIPPED, DELIVERED, CANCELLED.
8. createdAt — the timestamp when the order was created. Stored as a String in ISO 8601 UTC format.
9. updatedAt — the timestamp when the order was last updated. Stored as a String in ISO 8601 UTC format.

---

## 6. Example DynamoDB Item

```json
{
  "PK": "ORDER",
  "SK": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "orderId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "customerId": "C1001",
  "items": [
    {
      "productId": "P100",
      "quantity": 2
    }
  ],
  "totalAmount": 49.98,
  "status": "CONFIRMED",
  "createdAt": "2025-06-03T10:00:00Z",
  "updatedAt": "2025-06-03T10:05:00Z"
}
```

---

## 7. DynamoDB Billing Mode

The table uses PAY_PER_REQUEST billing mode (also called on-demand mode).

In this mode, DynamoDB automatically scales capacity up and down
based on actual traffic. There is no need to predict or configure
read and write capacity units in advance.

For a small project with variable or unpredictable traffic,
on-demand mode is simpler to manage and more cost-conscious
than provisioned capacity mode.

---

## 8. Alternative Design Considered

An alternative design was considered where orderId alone is used as the partition key,
with no sort key.

This works perfectly for retrieving a single order by ID.
However, listing all orders would require a Scan operation because there
is no shared partition key to Query against.

This alternative was rejected because Scan operations read the entire table,
consume more read capacity, and become slower and more expensive as the
number of orders grows. The composite key design avoids this problem entirely.

---

## 9. Trade-offs of the Chosen Design

The composite key design with a fixed partition key "ORDER" works well
for small to medium order volumes.

At very high volumes (millions of orders), storing all items under a single
partition key could create a hot partition, meaning one physical partition
in DynamoDB receives all the read and write traffic.

For the scale of this project (small business, hundreds to thousands of orders),
this is not a concern. At larger scale, the design could be evolved to use
date-based partition keys (for example, partitioning by month) combined with
a Global Secondary Index for flexible querying.

This trade-off is documented here as part of the architecture decision record.
