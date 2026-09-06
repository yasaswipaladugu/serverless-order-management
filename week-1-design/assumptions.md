# Assumptions and Constraints

## 1. Purpose

This document records the assumptions made during the design of the
OrderFlow GmbH Serverless Order Management System. In any real project,
not every detail is fully specified. Assumptions make the design decisions
explicit so that they can be reviewed, challenged, or updated.


## 2. Assumptions

### 2.1 Authentication and Authorization

- It is assumed that API authentication and authorization are out of scope for this project.
- In a production system, API Gateway would be protected using an API key,
a Cognito User Pool authorizer, or a Lambda authorizer.
- For this project, the API endpoints are accessible without authentication.
This is a known simplification and is acceptable for a learning and demonstration project.

### 2.2 Order Creation

- It is assumed that orders are created by internal staff or a trusted system,
not directly by end customers. No customer identity verification is performed.
- It is assumed that the customerId provided in the request is valid.
The system does not validate whether a customer actually exists in any external system.
- It is assumed that the items and totalAmount fields are provided correctly by the caller.
The system validates that these fields are present but does not recalculate the total
from individual item prices.

### 2.3 Order Identifiers

- It is assumed that UUIDs (version 4) are sufficient for generating unique order IDs.
- UUID collision probability is negligible for the expected order volume.

### 2.4 Data Volume

- It is assumed that the system will handle a relatively small number of orders
during development and testing (hundreds, not millions).
- The design choices still follow scalability best practices so that the system
could handle larger volumes without redesign.

### 2.5 Listing Orders

- The GET /orders endpoint needs to return a list of orders efficiently.
Because DynamoDB requires a partition key for Query operations, it is assumed
that a fixed partition key value (for example, the string "ORDER") will be used
alongside a sort key of orderId. This allows the Query operation to be used
instead of a Scan.
- This is a deliberate design decision to avoid table scans and is documented
as an architectural trade-off.

### 2.6 Timestamps

- It is assumed that all timestamps are stored and returned in ISO 8601 UTC format.
- No timezone conversion is performed for individual users.

### 2.7 Concurrent Updates

- It is assumed that conflicting concurrent updates are rare but possible.
- DynamoDB conditional expressions will be used to handle this scenario safely.
- If a conflict is detected, the system will return an error to the caller.

### 2.8 Error Scenarios

- It is assumed that DynamoDB and Lambda will be available and functioning normally.
- Catastrophic infrastructure failures are considered out of scope for this project.
- Basic error handling covers invalid input, missing orders, and invalid state transitions.

### 2.9 Cost

- It is assumed that all usage during development and testing remains within or close
to the AWS Free Tier limits.

### 2.10 Terraform State

- It is assumed that Terraform state is stored locally for this project.
- In a production environment, Terraform state would be stored remotely
in an S3 bucket with DynamoDB state locking to enable team collaboration
and prevent concurrent Terraform runs.

## 3. Constraints

- The project must be completed within 4 weeks.
- Only the following AWS services may be used: API Gateway, Lambda, DynamoDB, IAM, CloudWatch.
Additional services must not be added without justification.
- The system must remain within or close to AWS Free Tier limits to avoid unexpected costs.
- All infrastructure must be managed through Terraform.
- The Lambda runtime must be Python 3.12.
- The deployment region is fixed at eu-central-1 (Frankfurt).