## Why Monitoring?
- We need to know when something breaks or slows down
- CloudWatch automatically collects logs and metrics from Lambda and API Gateway

## What We Monitor

### Lambda
- Errors — Lambda crashed or threw an exception
- Duration — how long Lambda took to respond
- Throttles — Lambda was called too many times at once
- Invocations — total number of calls

### API Gateway
- 4XX errors — bad client requests (wrong input, not found)
- 5XX errors — server failures (Lambda crashed)
- Latency — total response time

### DynamoDB
- SuccessfulRequestLatency — how fast DB operations are
- SystemErrors — internal DynamoDB failures

## CloudWatch Log Groups Created
- /aws/lambda/orderflow-create-order (7-day retention)
- /aws/lambda/orderflow-read-order (7-day retention)
- /aws/lambda/orderflow-update-status (7-day retention)

## CloudWatch Alarms (Designed)
- Lambda Errors > 1 in 5 minutes → trigger alarm
- Lambda Duration > 3000ms → trigger alarm
- API 5XX errors > 0 → trigger alarm

## Prototype Note
- Alarms are defined but no email/SMS notifications are set up
- In production, alarms would connect to SNS to send alerts
- In production, AWS X-Ray would be added for request tracing
