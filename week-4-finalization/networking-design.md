## Current Prototype — No VPC

- This prototype does NOT use a VPC
- API Gateway, Lambda, and DynamoDB are AWS-managed services
- They communicate over AWS internal networks automatically
- All endpoints are public — no custom network configuration was done
- This is acceptable for a prototype but not suitable for production

## Why No VPC in the Prototype?
- Lambda, API Gateway, and DynamoDB work outside a VPC by default
- Adding a VPC adds complexity and cost (NAT Gateways)
- For a demo/prototype this is the simplest and fastest approach

## Production Networking Design (Future State)

### Region and Availability Zones
- AWS Region: eu-central-1 (Frankfurt)
- Two Availability Zones: eu-central-1a and eu-central-1b
- Two AZs provide high availability — if one AZ fails, the other continues

### VPC
- VPC Name: orderflow-vpc
- CIDR Block: 10.0.0.0/16 (gives 65,536 IP addresses)

### Subnets
- Public Subnet AZ-a: 10.0.1.0/24 (for API Gateway VPC Link / NAT Gateway)
- Public Subnet AZ-b: 10.0.2.0/24
- Private Subnet AZ-a: 10.0.3.0/24 (for Lambda functions)
- Private Subnet AZ-b: 10.0.4.0/24

### How Traffic Would Flow in Production
- Client sends HTTPS request to API Gateway
- API Gateway uses a VPC Link to reach Lambda in a private subnet
- Lambda connects to DynamoDB via a VPC Endpoint (no public internet)
- NAT Gateway in the public subnet allows Lambda to reach the internet if needed

### Key Networking Components in Production
- VPC — isolated private network on AWS
- Public Subnets — host NAT Gateways
- Private Subnets — host Lambda functions (not exposed to internet)
- VPC Endpoint for DynamoDB — Lambda talks to DynamoDB privately inside AWS network
- Security Groups — control which services can talk to each other
- NAT Gateway — allows private Lambda to make outbound calls if needed

## Prototype vs Production Summary
- Prototype: public endpoints, no VPC, no subnets, no CIDR, no NAT Gateway
- Production: VPC with private subnets, VPC endpoints, security groups, 2 AZs