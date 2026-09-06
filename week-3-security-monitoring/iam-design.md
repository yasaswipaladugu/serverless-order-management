## What is IAM?
- IAM controls who can do what on AWS
- Every Lambda needs permission to use DynamoDB and CloudWatch
- We follow Least Privilege — give only the minimum permissions needed

## IAM Role Created
- Role name: orderflow-lambda-execution-role
- Attached to all 3 Lambda functions
- Allows the Lambda service to use this role

## DynamoDB Permissions Given
- PutItem — create-order Lambda saves a new order
- GetItem — read-order Lambda fetches one order
- UpdateItem — update-status Lambda changes status
- Query — read-order Lambda lists all orders

## What is NOT Allowed
- No Scan (would read entire table — bad for performance)
- No DeleteItem (orders should not be deleted)
- No access to any other DynamoDB table
- No direct public access to DynamoDB

## CloudWatch Permissions
- Policy used: AWSLambdaBasicExecutionRole (AWS managed)
- Allows Lambda to write logs to CloudWatch

## Prototype Note
- This prototype has no API authentication — anyone with the URL can call the API
- In production, we would add Amazon Cognito or API Keys
- In production, AWS CloudTrail would be enabled to audit all API calls
