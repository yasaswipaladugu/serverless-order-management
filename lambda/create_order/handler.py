
# This Lambda is triggered by: POST /orders
# Its job:
#   1. Validate the incoming request body
#   2. Generate a unique order ID
#   3. Save the order to DynamoDB
#   4. Return the created order

import json
import uuid
import os
import logging
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB client
dynamodb = boto3.resource("dynamodb")

# The table name comes from an environment variable we'll set in Terraform
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

# All orders share the same Partition Key value "ORDER"
PK_VALUE = "ORDER"

# Initial status for every new order
INITIAL_STATUS = "PENDING"


def lambda_handler(event, context):
    """
    AWS Lambda always calls a function named 'lambda_handler'.
    - event: the incoming HTTP request data (body, headers, path params, etc.)
    - context: AWS runtime info (function name, memory, timeout, etc.)
    """
    logger.info("create_order invoked")
    logger.info(f"Event received: {json.dumps(event)}")

    # 1. Parse the request body
    try:
        # API Gateway sends the body as a JSON string, so we parse it
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        logger.error("Request body is not valid JSON")
        return build_response(400, {"error": "Request body must be valid JSON"})

    # 2. Validate required fields
    # These three fields are required — reject the request if any are missing
    required_fields = ["customerId", "items", "totalAmount"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        logger.warning(f"Missing required fields: {missing}")
        return build_response(400, {
            "error": f"Missing required fields: {', '.join(missing)}"
        })

    # Validate field types and values
    if not isinstance(body["items"], list) or len(body["items"]) == 0:
        return build_response(400, {"error": "'items' must be a non-empty list"})

    if not isinstance(body["totalAmount"], (int, float)) or body["totalAmount"] <= 0:
        return build_response(400, {"error": "'totalAmount' must be a positive number"})

    if not isinstance(body["customerId"], str) or not body["customerId"].strip():
        return build_response(400, {"error": "'customerId' must be a non-empty string"})

    # Validate each item in the items list
    for i, item in enumerate(body["items"]):
        if "productId" not in item or "quantity" not in item:
            return build_response(400, {
                "error": f"Item at index {i} must have 'productId' and 'quantity'"
            })
        if not isinstance(item["quantity"], int) or item["quantity"] <= 0:
            return build_response(400, {
                "error": f"Item at index {i}: 'quantity' must be a positive integer"
            })

    # 3. Generate a unique order ID
    order_id = f"ord-{uuid.uuid4()}"

    # 4. Build the order item
    now = datetime.now(timezone.utc).isoformat()  

    order_item = {
        "PK":          PK_VALUE,             
        "SK":          order_id,             
        "orderId":     order_id,             
        "customerId":  body["customerId"],
        "items":       body["items"],
        "totalAmount": str(body["totalAmount"]), 
        "status":      INITIAL_STATUS,     
        "createdAt":   now,
        "updatedAt":   now,
    }

    # 5. Save to DynamoDB
    try:
        # PutItem: creates a new item (or replaces if same PK+SK already exists)
        table.put_item(Item=order_item)
        logger.info(f"Order created successfully: {order_id}")
    except Exception as e:
        logger.error(f"DynamoDB PutItem failed: {str(e)}")
        return build_response(500, {"error": "Failed to create order. Please try again."})

    # 6. Return the created order
    response_body = {k: v for k, v in order_item.items() if k not in ("PK", "SK")}
    return build_response(201, response_body)  # 201 = Created


# Helper: build a standard HTTP response
def build_response(status_code, body):
    """
    API Gateway expects Lambda to return a dict with this exact structure.
    Without this, API Gateway won't know how to format the HTTP response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, default=str)
    }