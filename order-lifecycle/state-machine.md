# Order State Machine

## 1. What is a State Machine?

A state machine is a way of describing a system that can be in exactly one
state at any given time, and that can move between states only through
defined, allowed transitions.

In this project, every order has a status. That status is the current state
of the order. The order can only move from one status to another if the
transition is explicitly allowed by the business rules.

This approach ensures that an order can never end up in an impossible or
inconsistent situation — for example, moving from DELIVERED back to PENDING,
or from CANCELLED to SHIPPED.

---

## 2. States

The OrderFlow system defines six possible order states.

PENDING is the initial state. Every new order starts here.
It means the order has been received but not yet reviewed or accepted.

CONFIRMED means the order has been reviewed and accepted for fulfillment.
The business has committed to processing this order.

PROCESSING means the order is actively being prepared for shipment.
Physical goods may be picked, packed, or assembled at this stage.

SHIPPED means the order has been handed to a carrier and is in transit.
The order has left the warehouse.

DELIVERED means the order has been received by the customer.
This is a final state. No further transitions are possible.

CANCELLED means the order has been cancelled.
This is a final state. No further transitions are possible.

---

## 3. State Diagram

The following diagram shows all valid transitions between states.
                [ PENDING ]
                /         \
               /           \
              v             v
       [ CONFIRMED ]   [ CANCELLED ]
       /         \
      /           \
     v             v
[ PROCESSING ] [ CANCELLED ]
|
v
[ SHIPPED ]
|
v
[ DELIVERED ]
