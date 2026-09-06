## Why This Architecture is Cheap
- No servers running 24/7 — Lambda only charges when code runs
- DynamoDB PAY_PER_REQUEST — no capacity to pre-provision
- HTTP API Gateway is ~70% cheaper than REST API type
- Log retention set to 7 days to avoid storage buildup

## Cost Per Service

### Lambda
- Free Tier: 1 million requests/month + 400,000 GB-seconds
- At prototype scale (a few hundred calls/day) → $0.00

### API Gateway
- Free Tier: 1 million HTTP API calls/month (first 12 months)
- At prototype scale → $0.00

### DynamoDB
- Free Tier: 25 GB storage, always free (no expiry)
- PAY_PER_REQUEST: $1.25 per million writes, $0.25 per million reads
- At prototype scale → $0.00

### CloudWatch
- Free Tier: 5 GB log ingestion/month
- 7-day retention keeps logs minimal
- At prototype scale → $0.00

## Estimated Monthly Cost
- Prototype / Demo → $0.00
- Small business (1,000 orders/day) → ~$1–2
- Growing business (10,000 orders/day) → ~$5–15
- Large scale (100,000 orders/day) → ~$50–100

## Prototype Note
- No VPC means no NAT Gateway cost (saves ~$64/month in production)
- In production, extra costs would come from VPC, Cognito, X-Ray, and dashboards
