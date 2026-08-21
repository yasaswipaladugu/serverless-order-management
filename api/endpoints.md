# API Endpoints

## 1. Overview

The OrderFlow API is a REST API built on Amazon API Gateway.
It exposes four endpoints that together cover the complete order management lifecycle.
All requests and responses use JSON format.
The base URL is provided by API Gateway after deployment.

---

## 2. Endpoints Summary

POST   /orders                        Create a new order
GET    /orders/{orderId}              Retrieve a single order by ID
GET    /orders                        Retrieve a list of orders
PATCH  /orders/{orderId}/status       Update the status of an order

---

## 3. Endpoint Details

### 3.1 Create Order

Method:   POST
Path:     /orders
Purpose:  Creates a new order and stores it in DynamoDB with status PENDING.

Request body:

{
  "customerId": "C1001",
  "items": [
    {
      "productId": "P100",
      "quantity": 2
    }
  ],
  "totalAmount": 49.98
}

Field descriptions:

customerId is required. It identifies the customer placing the order.

items is required. It is a list of products being ordered.
Each item must contain a productId and a quantity.

totalAmount is required. It is the total monetary value of the order.

The system automatically generates the orderId, sets the status to PENDING,
and records the createdAt and updatedAt timestamps.
The caller does not provide these fields.

Success response — HTTP 201 Created:

{
  "orderId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "customerId": "C1001",
  "items": [
    {
      "productId": "P100",
      "quantity": 2
    }
  ],
  "totalAmount": 49.98,
  "status": "PENDING",
  "createdAt": "2025-06-03T10:00:00Z",
  "updatedAt": "2025-06-03T10:00:00Z"
}

Error responses:

HTTP 400 — if any required field is missing or the request body is invalid.

---

### 3.2 Retrieve Single Order

Method:   GET
Path:     /orders/{orderId}
Purpose:  Retrieves a single order by its unique ID.

Path parameter:

orderId is required. It is the UUID of the order to retrieve.

Request body: none

Success response — HTTP 200 OK:

{
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

Error responses:

HTTP 404 — if no order exists with the given orderId.

---

### 3.3 Retrieve All Orders

Method:   GET
Path:     /orders
Purpose:  Retrieves a list of orders from DynamoDB.

Request body: none

Query parameters (optional):

limit controls how many orders are returned per page.
If not provided, a default limit is applied.

nextToken is used for pagination. If the previous response included a nextToken,
passing it in the next request retrieves the next page of results.

Success response — HTTP 200 OK:

{
  "orders": [
    {
      "orderId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "customerId": "C1001",
      "status": "CONFIRMED",
      "totalAmount": 49.98,
      "createdAt": "2025-06-03T10:00:00Z",
      "updatedAt": "2025-06-03T10:05:00Z"
    },
    {
      "orderId": "a1b2c3d4-0000-1111-2222-333344445555",
      "customerId": "C1002",
      "status": "PENDING",
      "totalAmount": 29.99,
      "createdAt": "2025-06-03T11:00:00Z",
      "updatedAt": "2025-06-03T11:00:00Z"
    }
  ],
  "nextToken": "eyJvcmRlcklkIjogInh4eHgifQ=="
}

If there are no more pages, nextToken will not be present in the response.

Error responses:

HTTP 500 — if an unexpected internal error occurs.

---

### 3.4 Update Order Status

Method:   PATCH
Path:     /orders/{orderId}/status
Purpose:  Updates the status of an existing order if the transition is valid.

Path parameter:

orderId is required. It is the UUID of the order to update.

Request body:

{
  "status": "CONFIRMED"
}

The status field is required. It must be one of the defined valid statuses:
PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED.

The system validates that the transition from the current status to the
requested status is allowed according to the business rules.

Success response — HTTP 200 OK:

{
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

Error responses:

HTTP 400 — if the status field is missing or not a recognised value.
HTTP 404 — if no order exists with the given orderId.
HTTP 409 — if the requested transition is not allowed by the business rules.

Example HTTP 409 response body:

{
  "error": "Invalid state transition: SHIPPED cannot be transitioned to CANCELLED"
}

---

## 4. HTTP Status Codes Used

200 OK — the request succeeded and a result is returned.
201 Created — a new order was successfully created.
400 Bad Request — the request was missing required fields or contained invalid data.
404 Not Found — the requested order does not exist.
409 Conflict — the requested state transition is not allowed.
500 Internal Server Error — an unexpected error occurred on the server side.

---

## 5. Design Decisions

PATCH was chosen for status updates instead of PUT.
PUT replaces the entire resource. PATCH updates only a specific part of it.
Since we are only changing the status field, PATCH is the correct and more precise choice.

The status update endpoint is a separate path (/orders/{orderId}/status)
rather than a general update to /orders/{orderId}.
This makes the API intention clear — this endpoint exists specifically to
manage the order lifecycle, not to edit arbitrary order fields.

All four endpoints are resource-oriented, following REST principles.
The URL represents a resource (an order or a collection of orders)
and the HTTP method describes the action being performed on it.
