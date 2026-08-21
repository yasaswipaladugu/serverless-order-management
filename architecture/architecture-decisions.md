# Architecture Decisions

## 1. Purpose

This document records the major architectural decisions made for the
OrderFlow GmbH Serverless Order Management System. For each decision,
the problem is described, the chosen solution is explained, alternatives
that were considered are listed, and the trade-offs are documented.

This type of document is called an Architecture Decision Record (ADR).
It exists so that anyone reading the project can understand not just
what was built, but why it was built that way.

---

## 2. Decision 1 — Use a Serverless Architecture

### Problem
OrderFlow GmbH needs a backend that can handle increasing order volume
without requiring administrators to manage servers. The business is small
and does not have a dedicated operations team to maintain infrastructure.

### Decision
Use a fully serverless architecture built on AWS managed services:
API Gateway, Lambda, and DynamoDB.

### Why This Was Chosen
Serverless services scale automatically in response to traffic.
There are no servers to provision, patch, or restart.
Costs are based on actual usage, so there are no charges when the system is idle.
AWS manages the underlying infrastructure, which reduces operational burden significantly.

### Alternatives Considered

Alternative 1 — EC2 with a traditional web application server.
An EC2 instance could run a Python web framework such as Flask or FastAPI.
This was rejected because EC2 instances run continuously and incur costs
even when there is no traffic. They also require manual scaling configuration,
operating system maintenance, and security patching. This adds operational
complexity that is not appropriate for a small business or a learning project.

Alternative 2 — AWS Elastic Beanstalk.
Elastic Beanstalk manages EC2 instances automatically and simplifies deployment.
This was rejected for the same core reason as EC2 — it still relies on
continuously running servers and does not offer true pay-per-use billing.

### Trade-offs
Lambda functions have a maximum execution timeout of 15 minutes.
They are not suitable for very long-running background processes.
Cold starts can add a small latency delay when a function has not been
invoked recently. For the expected traffic pattern of OrderFlow GmbH,
neither of these is a significant concern.

---

## 3. Decision 2 — Use Amazon API Gateway

### Problem
The system needs a way to expose HTTP endpoints to the outside world
and route incoming requests to the correct Lambda function.

### Decision
Use Amazon API Gateway (HTTP API type) as the entry point for all requests.

### Why This Was Chosen
API Gateway is a fully managed service that handles request routing,
input validation, SSL termination, and throttling automatically.
It integrates natively with Lambda and requires no server management.
The HTTP API type is simpler and cheaper than the REST API type
and is sufficient for the requirements of this project.

### Alternatives Considered

Alternative 1 — Application Load Balancer (ALB) in front of Lambda.
An ALB can also route HTTP requests to Lambda functions.
This was rejected because API Gateway provides more built-in features
relevant to API management such as usage plans, request throttling,
and easier stage management. ALB is more suitable when routing to
EC2 or container targets.

Alternative 2 — Direct Lambda function URLs.
AWS Lambda now supports function URLs, which give each Lambda function
its own HTTPS endpoint without needing API Gateway.
This was rejected because function URLs do not provide centralised
request routing, throttling, or stage management. Managing four separate
function URLs would be harder to maintain than a single API Gateway.

### Trade-offs
API Gateway adds a small amount of latency to every request.
It also has its own cost per request, which is relevant at very high volumes.
For the scale of this project, both are negligible.

---

## 4. Decision 3 — Use AWS Lambda for Business Logic

### Problem
The system needs a compute layer that runs the business logic for each
API operation — validating input, enforcing state transition rules,
reading and writing to DynamoDB, and returning responses.

### Decision
Use AWS Lambda with Python 3.12. Each major operation has its own
dedicated Lambda function.

### Why This Was Chosen
Lambda runs code only when it is invoked. There are no idle costs.
It scales automatically — if 100 requests arrive simultaneously,
Lambda runs 100 concurrent instances of the function.
Python is a widely supported Lambda runtime with excellent AWS SDK support
through the boto3 library.
Separating functions by responsibility (create, read, update) follows
the principle of single responsibility and makes the code easier to
understand, test, and maintain.

### Alternatives Considered

Alternative 1 — A single Lambda function handling all routes.
All four endpoints could be handled by one Lambda function that inspects
the HTTP method and path to decide what to do.
This was rejected because it concentrates too much logic in one place,
makes the function harder to read and maintain, and means that a change
to the create logic could accidentally affect the retrieve logic.

Alternative 2 — AWS Fargate (containers).
Fargate runs containerised applications without managing servers.
This was rejected because containers have higher operational complexity
than Lambda. They require building and pushing Docker images, managing
container definitions, and configuring task scaling. For this project,
Lambda is simpler and more appropriate.

### Trade-offs
Lambda functions are stateless. They do not retain any information between
invocations. All state must be stored in DynamoDB. This is intentional
and is a core characteristic of serverless design.
Lambda has a 15-minute execution limit, which is not relevant for this project
because all operations complete in milliseconds.

---

## 5. Decision 4 — Use Amazon DynamoDB

### Problem
The system needs a database to store order data persistently.
The database must be managed, scalable, and integrate naturally with Lambda.

### Decision
Use Amazon DynamoDB with on-demand billing mode.

### Why This Was Chosen
DynamoDB is a fully managed NoSQL database. There is no database server
to provision, patch, or maintain.
It integrates natively with Lambda through the boto3 AWS SDK.
It scales automatically to handle variable read and write traffic.
On-demand billing means there are no charges when the database is idle.
GetItem lookups by primary key are extremely fast regardless of table size.

### Alternatives Considered

Alternative 1 — Amazon RDS (Relational Database Service).
RDS provides a managed relational database such as PostgreSQL or MySQL.
Relational databases use tables, rows, columns, and SQL queries.
This was rejected for several reasons.
RDS instances run continuously and incur costs even when idle.
RDS requires a VPC configuration with private subnets to be used securely
with Lambda, which adds significant infrastructure complexity.
The order data model for this project is straightforward and does not
require complex joins or relational queries. DynamoDB is simpler and
more appropriate for this use case.

Alternative 2 — Amazon Aurora Serverless.
Aurora Serverless is a relational database that can scale down to zero
when not in use, removing the idle cost problem of standard RDS.
This was rejected because it still requires VPC configuration,
has a cold start delay when scaling from zero, and adds relational
complexity that is not needed for this project's simple data model.

### Trade-offs
DynamoDB is not suitable for complex queries that filter by multiple
arbitrary attributes. For example, retrieving all orders for a specific
customerId is not directly supported by the current table design without
adding a Global Secondary Index. For the scope of this project, the four
defined access patterns are sufficient and the table design supports all of them.
If additional query patterns are needed in the future, a Global Secondary Index
can be added without redesigning the entire table.

---

## 6. Decision 5 — DynamoDB Table Key Design

### Problem
The application needs to both retrieve a single order by its ID efficiently
and list all orders efficiently. These two needs create a design tension
because a simple single-attribute partition key satisfies the first need
but forces a Scan operation for the second.

### Decision
Use a composite primary key with a fixed partition key value "ORDER"
and the orderId UUID as the sort key.

### Why This Was Chosen
With all orders sharing the partition key "ORDER", a Query operation
on that partition key returns all orders without scanning the rest of the table.
Individual orders can still be retrieved directly using GetItem with both
the partition key and sort key.
This satisfies both access patterns efficiently using only Query and GetItem operations.

### Alternatives Considered

Alternative 1 — orderId as the sole partition key.
This makes single-order retrieval simple and fast.
Listing all orders would require a Scan, which was rejected
because Scan reads the entire table regardless of how many results are needed.

Alternative 2 — customerId as the partition key and orderId as the sort key.
This allows efficient retrieval of all orders for a specific customer.
However, listing all orders across all customers would still require a Scan.
Since the current requirements do not include filtering by customer,
this design was not chosen for the primary table structure.

### Trade-offs
Using a fixed partition key means all orders are stored in a single DynamoDB partition.
At very high write volumes (thousands of writes per second), this could create
a hot partition that limits throughput. For the scale of this project,
this is not a concern. At larger scale, date-based partition keys or
other partitioning strategies could be introduced.

---

## 7. Decision 6 — Use Terraform for Infrastructure Management

### Problem
The system requires multiple AWS resources — API Gateway, Lambda functions,
DynamoDB table, IAM roles, and CloudWatch log groups. These need to be
created consistently, reproducibly, and without manual errors.

### Decision
Use Terraform to define and manage all AWS infrastructure as code.

### Why This Was Chosen
Terraform allows the entire infrastructure to be described in configuration files.
Running terraform apply creates all resources in the correct order automatically.
The infrastructure can be torn down and recreated identically at any time.
Changes to infrastructure are made by editing the configuration files and
applying them, which makes changes trackable in Git.
Terraform is cloud-agnostic and is widely used in the industry.

### Alternatives Considered

Alternative 1 — AWS CloudFormation.
CloudFormation is AWS's native infrastructure-as-code service.
It was not chosen because Terraform has a cleaner syntax (HCL),
better error messages, and is more widely adopted across the industry.
Terraform is also cloud-agnostic, making the skills more transferable.

Alternative 2 — AWS SAM (Serverless Application Model).
SAM is a framework specifically designed for serverless AWS applications.
It was not chosen because Terraform provides broader infrastructure coverage
and is more appropriate for demonstrating general infrastructure-as-code skills.

### Trade-offs
Terraform state is stored locally in a terraform.tfstate file for this project.
In a team environment, this would cause conflicts if two people ran Terraform
at the same time. The production solution would be to store state in an S3 bucket
with DynamoDB state locking. For a single-developer project, local state is acceptable.
