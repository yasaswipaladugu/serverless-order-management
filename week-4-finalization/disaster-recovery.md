## What is Disaster Recovery?
- A plan for what happens if part of the system fails
- Goal: keep the system running or recover quickly after a failure

## Current Prototype — What is Resilient Already?
- Lambda automatically retries on internal failures
- DynamoDB is fully managed — AWS handles hardware failures
- API Gateway is managed by AWS — no single point of failure
- All services run across multiple AWS data centers automatically

## What the Prototype Does NOT Have
- No DynamoDB Point-in-Time Recovery (PITR) enabled
- No cross-region backup
- No automated failover to another region
- No alerting if the system goes down

## Recovery Time Estimates (Prototype)
- Lambda failure → AWS restarts automatically in seconds
- DynamoDB issue → AWS resolves internally, usually within minutes
- Full region outage → system would be unavailable (no multi-region setup)

## Production Disaster Recovery Plan

### RTO and RPO Goals
- RTO (Recovery Time Objective): how quickly we recover → target under 15 minutes
- RPO (Recovery Point Objective): how much data we can afford to lose → target under 5 minutes

### What to Add in Production
- Enable DynamoDB Point-in-Time Recovery (PITR) — restore data to any second in the last 35 days
- Enable DynamoDB global tables — replicate data to a second region (e.g. eu-west-1)
- Use CloudWatch Alarms with SNS to alert on failures immediately
- Deploy Lambda and API Gateway in a second region as a standby
- Use Route 53 health checks to auto-switch traffic to the backup region

### Backup Strategy
- DynamoDB PITR enabled — continuous automatic backups
- Daily DynamoDB on-demand backup exported to S3
- S3 bucket versioning enabled for backup files
- Backups stored in a different AWS region

## Prototype Note
- This prototype is a single-region, single-AZ design for demo purposes
- Data loss is acceptable in the prototype since it holds only test data
- In production, the steps above would be implemented before go-live