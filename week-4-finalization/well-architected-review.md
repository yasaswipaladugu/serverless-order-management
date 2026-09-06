## What is the AWS Well-Architected Framework?
- A set of best practices from AWS to evaluate cloud architectures
- Has 5 pillars: Operational Excellence, Security, Reliability, Performance, Cost Optimization

---

## Pillar 1 — Operational Excellence
- What we did: Infrastructure managed as code using Terraform
- What we did: CloudWatch Log Groups for all Lambda functions
- What we can improve: Add CI/CD pipeline (GitHub Actions) to automate deployments
- What we can improve: Add structured JSON logging for easier searching

## Pillar 2 — Security
- What we did: IAM least privilege — Lambda only has 4 DynamoDB permissions
- What we did: No direct public access to DynamoDB
- What we can improve: Add API authentication (Amazon Cognito)
- What we can improve: Enable AWS CloudTrail for audit logging
- What we can improve: Enable DynamoDB encryption at rest (it is on by default but should be verified)

## Pillar 3 — Reliability
- What we did: DynamoDB ConditionExpression prevents conflicting updates
- What we did: All 3 services (Lambda, API Gateway, DynamoDB) are fully managed by AWS
- What we can improve: Enable DynamoDB Point-in-Time Recovery
- What we can improve: Add retry logic in Lambda for transient failures
- What we can improve: Deploy to a second region for disaster recovery

## Pillar 4 — Performance Efficiency
- What we did: DynamoDB Query instead of Scan (efficient, uses index)
- What we did: PAY_PER_REQUEST billing — scales automatically
- What we did: Lambda is stateless — scales automatically with traffic
- What we can improve: Add pagination to GET /orders for large datasets
- What we can improve: Add DynamoDB DAX (cache) if read volume is very high

## Pillar 5 — Cost Optimization
- What we did: Serverless — no idle server costs
- What we did: HTTP API Gateway (cheaper than REST API)
- What we did: 7-day CloudWatch log retention
- What we can improve: Set Lambda memory size based on actual profiling
- What we can improve: Use AWS Cost Explorer to monitor spending as traffic grows

---

## Prototype Note
- This project is a working prototype that demonstrates all 5 pillars at a basic level
- It is not production-ready but can be extended to meet industry standards
- See networking-design.md and disaster-recovery.md for production extension plans

## How to Extend to Industry Standards
- Add authentication with Amazon Cognito
- Add a VPC with private subnets and VPC endpoints
- Enable DynamoDB PITR and cross-region replication
- Set up CI/CD with GitHub Actions and Terraform Cloud
- Add AWS X-Ray for distributed tracing
- Add CloudWatch dashboards and SNS alerting
- Conduct a full security audit with AWS Trusted Advisor