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
Store order information persistently.
Allow authorized users to retrieve an order.
Allow authorized users to retrieve multiple orders.
Allow order status to be updated.
Prevent invalid order-state transitions.
Allow appropriate orders to be cancelled.
Validate incoming requests.
Handle errors gracefully.
Automatically scale as request volume increases.
Avoid continuously running application servers.
Protect order data from unauthorized access.
Provide logging and monitoring.
Keep the architecture simple and cost-conscious.
Support infrastructure management through Terraform.
Be suitable for implementation as a small AWS project.

