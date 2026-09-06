## The Problem
- Two users could try to update the same order at the same time
- Without protection, one update could silently overwrite the other
- Example: User A changes PENDING → CONFIRMED while User B changes PENDING → CANCELLED at the same time

## How We Prevent This — Optimistic Locking
- We use DynamoDB ConditionExpression on every UpdateItem call
- The update only succeeds if the current status in the database matches what we expect
- If another request already changed the status, our update fails with a clear error
- Client receives a 409 Conflict response

## How Errors Are Handled

- Missing required fields in request → 400 Bad Request
- Invalid status transition (e.g. DELIVERED → PENDING) → 409 Conflict
- Order does not exist → 404 Not Found
- Status already changed by another request → 409 Conflict
- DynamoDB temporarily unavailable → 500 Internal Server Error

## State Machine Rules
- PENDING → CONFIRMED or CANCELLED
- CONFIRMED → PROCESSING or CANCELLED
- PROCESSING → SHIPPED
- SHIPPED → DELIVERED
- DELIVERED → nothing (terminal state)
- CANCELLED → nothing (terminal state)

## Prototype Note
- No retry logic — client must retry on failure
- In production, we would add SQS queues and exponential backoff retries
- In production, we would add idempotency keys to prevent duplicate orders
