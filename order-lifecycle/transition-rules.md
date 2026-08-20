# Order State Transition Rules

## 1. Purpose

This document defines every allowed and rejected state transition for
the OrderFlow order management system. These rules are implemented as
business logic inside the Lambda function and are enforced on every
status update request.

---

## 2. Allowed Transitions

The following transitions are valid and will be accepted by the system.

- PENDING → CONFIRMED
The order has been reviewed and accepted. This is the normal first step
after an order is received.
- PENDING → CANCELLED
The order was received but cancelled before it was accepted.
Cancellation at this stage is straightforward because no work has started.
- CONFIRMED → PROCESSING
The order has been accepted and work is beginning. The order moves into
active preparation.
- CONFIRMED → CANCELLED
The order was accepted but cancelled before preparation started.
This is still allowable because no physical work has begun.
- PROCESSING → SHIPPED
The order has been fully prepared and handed to a carrier.
This is the normal progression after processing is complete.
- SHIPPED → DELIVERED
The carrier has confirmed delivery and the customer has received the order.
This is the final step of a successful order.

---

## 3. Rejected Transitions

The following transitions are invalid and will be rejected by the system
with an HTTP 409 Conflict response and a descriptive error message.

- PROCESSING → CANCELLED
Once an order is in PROCESSING, physical preparation has already started.
Cancellation at this stage is not permitted because resources have been committed.
- SHIPPED → CANCELLED
The order is already in transit with a carrier. It cannot be recalled or cancelled.
- DELIVERED → any status
DELIVERED is a final state. The order lifecycle is complete.
No further changes are possible under any circumstances.
- CANCELLED → any status
CANCELLED is a final state. A cancelled order cannot be reopened, reactivated,
or transitioned to any other status.

Any backward transition
Orders cannot move backward through the lifecycle.
For example, CONFIRMED cannot go back to PENDING, and SHIPPED cannot go back to PROCESSING.
The system will reject any attempt to move to a previous state.

Any undefined transition
Any transition not listed in the allowed transitions above is rejected.
The system uses an explicit allowlist approach — only transitions that are
specifically defined as allowed will succeed. Everything else is denied.

---

## 4. Transition Rules in Code

The allowed transitions are represented in the Lambda function as a dictionary
where the key is the current status and the value is a list of statuses
that the order is allowed to move to from that current status.

ALLOWED_TRANSITIONS = {
    "PENDING":     ["CONFIRMED", "CANCELLED"],
    "CONFIRMED":   ["PROCESSING", "CANCELLED"],
    "PROCESSING":  ["SHIPPED"],
    "SHIPPED":     ["DELIVERED"],
    "DELIVERED":   [],
    "CANCELLED":   []
}

When a status update request arrives, the Lambda function:

1. Retrieves the current status of the order from DynamoDB.
2. Looks up the current status in the ALLOWED_TRANSITIONS dictionary.
3. Checks whether the requested new status is in the list of allowed transitions.
4. If it is allowed, the update proceeds.
5. If it is not allowed, the function returns HTTP 409 with an error message.

DELIVERED and CANCELLED map to empty lists, meaning no transitions
are allowed from these states.

---

## 5. Error Response for Invalid Transitions

When a transition is rejected, the system returns the following:

HTTP status code: 409 Conflict

Response body example:
{
  "error": "Invalid state transition: SHIPPED cannot be transitioned to CANCELLED"
}

The error message always includes the current status and the requested status
so that the caller understands exactly why the request was rejected.

---

## 6. Design Justification

The allowlist approach was chosen deliberately over a denylist approach.

- With a denylist, you list the transitions that are forbidden and allow everything else.
This is risky because any new status added in the future would be allowed by default,
which could introduce bugs.

- With an allowlist, you list only the transitions that are explicitly permitted
and reject everything else. This is safer because any unrecognised or future
transition is automatically rejected until it is explicitly added to the list.

This design makes the business rules easy to read, easy to test, and easy to modify.
