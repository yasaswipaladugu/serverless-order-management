## 3. Functional Requirements

### 3.1 Create Order

- The system must accept a POST request containing a customerId, a list of items, and a totalAmount.
- The system must validate that all required fields are present in the request.
- The system must generate a unique orderId.
- The system must assign the initial status PENDING to every new order.
- The system must save the order to DynamoDB.
-The system must return the created order.

### 3.2 Retrieve Single Order

- The system must accept a GET request with an orderId as a path parameter.
- The system must retrieve the matching order from DynamoDB.
- The response must include the orderId, customerId, items, totalAmount,
status, createdAt, and updatedAt fields.
- If the orderId does not exist, the system must return HTTP status 404.

### 3.3 Retrieve All Orders 

- The system must return a list of orders from DynamoDB.
- The system must use an efficient DynamoDB access pattern.
- A full table Scan must be avoided for standard queries.
- The system must support pagination to avoid returning an unbounded number of results.

### 3.4 Update Order Status 

- The system must accept a PATCH request containing the desired new status.
- The system must retrieve the current status of the order from DynamoDB.
- The system must validate whether the requested transition is allowed
according to the defined business rules.
- If the transition is not allowed, the system must return HTTP status 409
along with a clear error message explaining why the transition was rejected.
- If the transition is valid, the system must update the status and the
updatedAt timestamp in DynamoDB.
- The system must use a DynamoDB conditional expression when performing
the update to prevent conflicting concurrent updates.
- On success, the system must return the updated order with HTTP status 200.

### 3.5 Error Handling

- The system must return HTTP 400 for missing or invalid input fields.
- The system must return HTTP 404 when an order cannot be found.
- The system must return HTTP 409 when an invalid state transition is attempted.
- The system must return HTTP 500 for unexpected internal errors.
- All error responses must include a JSON body with a descriptive error message.


## 4. Non-Functional Requirements

### 4.1 Scalability

- The system must handle increasing API traffic without any manual intervention.
- Lambda and API Gateway scale automatically. DynamoDB will be configured
in on-demand mode so that it scales with request volume.

### 4.2 Availability

- The system must rely entirely on AWS-managed services that have built-in
high availability. 
- There are no EC2 instances or self-managed servers.

### 4.3 Security

- API clients must not have any direct access to DynamoDB.
- All requests must go through API Gateway and Lambda.
- Every Lambda function must run under a least-privilege IAM role.
 This means each function is granted only the specific permissions it needs
and nothing more.
- No AWS credentials or secret values may be hardcoded inside Lambda function code.

### 4.4 Performance

- Retrieving a single order using GET /orders/{orderId} must use DynamoDB's
GetItem operation, which looks up a record directly by its primary key.
This is efficient regardless of how many orders exist in the database.
- The system must not use DynamoDB Scan operations for standard queries
because Scan reads the entire table and becomes slow and expensive at scale.

### 4.5 Reliability

- Status update operations must use DynamoDB conditional expressions to
prevent race conditions. If two requests attempt to update the same order
at the same time, only one should succeed and the other should be rejected safely.

### 4.6 Cost Optimization

- The system must use only pay-per-use services. Lambda charges per invocation,
API Gateway charges per request, and DynamoDB will be set to on-demand billing.
There are no continuously running resources and therefore no idle costs.
- CloudWatch log retention will be set to 7 days to limit log storage costs.

### 4.7 Maintainability

- Lambda functions must be separated by responsibility.
One function handles order creation, one handles retrieval, and one handles status updates.
- Business logic such as state transition validation must be kept separate from
database access code so that it is easy to read, test, and modify.
- All infrastructure must be defined in Terraform so that the environment
can be reproduced consistently.


## 5. API Response Format

All API responses use JSON format.

A successful response looks like this:

{
  "orderId": "a1b2c3d4-...",
  "customerId": "C1001",
  "items": [...],
  "totalAmount": 49.98,
  "status": "PENDING",
  "createdAt": "2025-06-03T10:00:00Z",
  "updatedAt": "2025-06-03T10:00:00Z"
}

An error response looks like this:

{
  "error": "Invalid state transition: SHIPPED cannot be changed to CANCELLED"
}


## 6. Infrastructure Requirements

- All AWS resources must be created and managed through Terraform.
No resources will be created manually through the AWS Console during implementation.
- The deployment region is eu-central-1 (Frankfurt).
- DynamoDB billing mode will be set to PAY_PER_REQUEST (on-demand).
- The Lambda runtime will be Python 3.12.
- CloudWatch log retention will be set to 7 days.
- Terraform state will be stored locally in a terraform.tfstate file.


