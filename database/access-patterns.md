# DynamoDB Access Patterns

## 1. What is an Access Pattern?

An access pattern describes a specific way that the application needs to
read or write data. In DynamoDB, you must design your table structure around
your access patterns before you start building, because DynamoDB does not
support flexible ad-hoc queries the way a relational database does.

If you design the table without thinking about access patterns first,
you will end up using Scan operations, which are slow and expensive at scale.

---

## 2. Identified Access Patterns

This project has four access patterns, one for each API endpoint.

---

### Access Pattern 1 — Create a new order

Operation: Write (PutItem)

When: A POST /orders request is received.

How it works:
The Lambda function constructs a new item with all order attributes
and writes it to the DynamoDB table using the PutItem operation.
The PK is set to "ORDER" and the SK is set to the newly generated orderId UUID.

DynamoDB operation: PutItem
Key used: PK = "ORDER", SK = generated orderId

This is a straightforward write operation and requires no special design consideration.

---

### Access Pattern 2 — Retrieve a single order by ID

Operation: Read (GetItem)

When: A GET /orders/{orderId} request is received.

How it works:
The Lambda function knows both parts of the primary key.
PK is always "ORDER" and SK is the orderId from the URL path parameter.
DynamoDB can locate the exact item immediately using the full primary key.

DynamoDB operation: GetItem
Key used: PK = "ORDER", SK = orderId from the request

GetItem is the most efficient DynamoDB read operation. It retrieves exactly
one item using its full primary key and does not read any other items.
Performance is consistent regardless of how many orders are in the table.

---

### Access Pattern 3 — Retrieve all orders

Operation: Read (Query)

When: A GET /orders request is received.

How it works:
The Lambda function queries DynamoDB using the partition key PK = "ORDER".
Because all orders share this partition key, DynamoDB returns all of them
from a single partition without scanning the rest of the table.

DynamoDB operation: Query
Key used: PK = "ORDER"

Pagination is applied using the Limit parameter and the LastEvaluatedKey
that DynamoDB returns when there are more results available.
The Lambda function converts LastEvaluatedKey into a nextToken in the API response.
The caller can pass this token back to retrieve the next page.

This is why the composite key design was chosen. Without a shared partition key,
listing all orders would require a Scan, which is unsuitable for production use.

---

### Access Pattern 4 — Update order status

Operation: Read then conditional write (GetItem + UpdateItem)

When: A PATCH /orders/{orderId}/status request is received.

How it works in two steps:

Step 1 — Read the current status.
The Lambda function uses GetItem with PK = "ORDER" and SK = orderId
to retrieve the current order and read its current status.

Step 2 — Validate and update.
The Lambda function checks whether the requested transition is allowed.
If the transition is valid, it calls UpdateItem with a conditional expression.

The conditional expression tells DynamoDB to only perform the update
if the current status in the database still matches what was read in Step 1.
This prevents a race condition where two requests try to update the same
order at the same time.

DynamoDB operation: UpdateItem with a ConditionExpression
Key used: PK = "ORDER", SK = orderId
Condition: the status attribute must still equal the value read in Step 1

If the condition fails (because another request already changed the status),
DynamoDB raises a ConditionalCheckFailedException.
The Lambda function catches this and returns an appropriate error to the caller.

---

## 3. Why Scan Must Be Avoided

A Scan operation reads every single item in the entire DynamoDB table.
It then filters the results in memory after reading them.

This means that even if you only want 10 orders, DynamoDB still reads
all 10,000 orders (or however many exist) and discards the ones you do not need.

The problems with Scan are:

It consumes read capacity proportional to the total size of the table,
not the number of results returned. This means costs grow as the table grows.

It becomes slower as the table grows because more data must be read each time.

It is not suitable for any operation that needs to be fast and predictable at scale.

The composite key design in this project ensures that listing orders uses
Query instead of Scan, which reads only the items in the "ORDER" partition
and scales efficiently.

---

## 4. Summary of Operations

Create order:
  DynamoDB operation — PutItem
  Keys used — PK = "ORDER", SK = new UUID

Retrieve single order:
  DynamoDB operation — GetItem
  Keys used — PK = "ORDER", SK = orderId

Retrieve all orders:
  DynamoDB operation — Query on PK = "ORDER"
  Supports pagination via LastEvaluatedKey

Update order status:
  DynamoDB operation — UpdateItem with ConditionExpression
  Keys used — PK = "ORDER", SK = orderId
  Condition — current status must match expected value
