## What is the AWS Well-Architected Framework?
- A set of best practices from AWS to evaluate cloud architectures
- Has 5 pillars: Operational Excellence, Security, Reliability, Performance, Cost Optimization

---

## Pillar 1 — Operational Excellence
- What I did: Infrastructure managed as code using Terraform
- What I did: CloudWatch Log Groups for all Lambda functions
- What I can improve: Add CI/CD pipeline (GitHub Actions) to automate deployments
- What I can improve: Add structured JSON logging for easier searching

## Pillar 2 — Security
- What I did: IAM least privilege — Lambda only has 4 DynamoDB permissions
- What I did: No direct public access to DynamoDB
- What I can improve: Add API authentication (Amazon Cognito)
- What I can improve: Enable AWS CloudTrail for audit logging
- What I can improve: Enable DynamoDB encryption at rest (it is on by default but should be verified)

## Pillar 3 — Reliability
- What I did: DynamoDB ConditionExpression prevents conflicting updates
- What I did: All 3 services (Lambda, API Gateway, DynamoDB) are fully managed by AWS
- What I can improve: Enable DynamoDB Point-in-Time Recovery
- What I can improve: Add retry logic in Lambda for transient failures
- What I can improve: Deploy to a second region for disaster recovery

## Pillar 4 — Performance Efficiency
- What I did: DynamoDB Query instead of Scan (efficient, uses index)
- What I did: PAY_PER_REQUEST billing — scales automatically
- What I did: Lambda is stateless — scales automatically with traffic
- What I can improve: Add pagination to GET /orders for large datasets
- What I can improve: Add DynamoDB DAX (cache) if read volume is very high

## Pillar 5 — Cost Optimization
- What I did: Serverless — no idle server costs
- What I did: HTTP API Gateway (cheaper than REST API)
- What I did: 7-day CloudWatch log retention
- What I can improve: Set Lambda memory size based on actual profiling
- What I can improve: Use AWS Cost Explorer to monitor spending as traffic grows

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