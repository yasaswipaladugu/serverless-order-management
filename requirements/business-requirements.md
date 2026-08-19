# Business Requirements

## 1. Project Context

OrderFlow GmbH is a small business that sells products through an online platform.
The company currently manages customer orders through a basic application.
As customer volume grows, the existing system is no longer sufficient.

OrderFlow GmbH requires a new backend system that can manage the complete
lifecycle of customer orders — from creation through to delivery or cancellation.

## 2. Business Goals

The new system must:
1. Allow an order to be created.
2. Assign a unique order identifier.
3. Store order information persistently.
4. Allow authorized users to retrieve an order.
5. Allow authorized users to retrieve multiple orders.
6. Allow order status to be updated.
7. Prevent invalid order-state transitions.
8. Allow appropriate orders to be cancelled.
9. Validate incoming requests.
10. Handle errors gracefully.
11. Automatically scale as request volume increases.
12. Avoid continuously running application servers.
13. Protect order data from unauthorized access.
14. Provide logging and monitoring.
15. Keep the architecture simple and cost-conscious.
16. Support infrastructure management through Terraform.

## 3. Order Lifecycle

An order at OrderFlow GmbH moves through a defined set of stages.
Each stage represents a real-world business event.
- PENDING means the order has been received but not yet reviewed.
- CONFIRMED means the order has been reviewed and accepted for fulfillment.
- PROCESSING means the order is being prepared for shipment.
- SHIPPED means the order has been dispatched to the customer.
- DELIVERED means the order has been received by the customer. This is a final state.
- CANCELLED means the order has been cancelled. This is a final state.
The normal progression is:
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED

## 4. Cancellation Rules

Not every order can be cancelled. The following rules apply:
1. An order in PENDING status can be cancelled because it has not yet been accepted.
2. An order in CONFIRMED status can be cancelled because preparation has not yet started.
3. An order in PROCESSING status cannot be cancelled because preparation has already begun.
4. An order in SHIPPED status cannot be cancelled because it is already in transit.
5. An order in DELIVERED status cannot be cancelled because it has already been completed.
6. An order that is already CANCELLED cannot be cancelled again.

## 5. Invalid Transitions

The system must reject any attempt to move an order into an invalid state.
- DELIVERED cannot transition to any other status because it is a final state.
- CANCELLED cannot transition to any other status because it is a final state.
- SHIPPED cannot transition to CANCELLED because the order is already in transit.
- PROCESSING cannot transition to CANCELLED because preparation has already started.
No order can move backward through the lifecycle.
- For example, CONFIRMED cannot go back to PENDING.

