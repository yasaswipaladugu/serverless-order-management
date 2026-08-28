
# This Lambda handles TWO endpoints:
#   GET /orders/{orderId}  → retrieve a single order
#   GET /orders            → list all orders
#
# API Gateway routes both to this same Lambda.

import json
import os
import logging

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

PK_VALUE = "ORDER"

# Maximum orders returned per page
DEFAULT_PAGE_SIZE = 20


def lambda_handler(event, context):
    logger.info("read_order invoked")
    logger.info(f"Event received: {json.dumps(event)}")

    # Check if this is a single-order or list-orders request
    path_params = event.get("pathParameters") or {}
    order_id = path_params.get("orderId")

    if order_id:
        # Single order request: GET /orders/{orderId}
        return get_single_order(order_id)
    else:
        # List orders request: GET /orders
        query_params = event.get("queryStringParameters") or {}
        return list_orders(query_params)


def get_single_order(order_id):
    """Retrieve one order by its ID."""
    logger.info(f"Fetching single order: {order_id}")

    try:
        response = table.get_item(
            Key={
                "PK": PK_VALUE,
                "SK": order_id
            }
        )
    except Exception as e:
        logger.error(f"DynamoDB GetItem failed: {str(e)}")
        return build_response(500, {"error": "Failed to retrieve order."})

    # DynamoDB returns the item inside response["Item"]
    item = response.get("Item")
    if not item:
        logger.warning(f"Order not found: {order_id}")
        return build_response(404, {"error": f"Order '{order_id}' not found."})

    # Remove internal DynamoDB keys from the response
    clean_item = {k: v for k, v in item.items() if k not in ("PK", "SK")}
    return build_response(200, clean_item)


def list_orders(query_params):
    """List all orders, with optional pagination."""
    logger.info("Listing all orders")


    try:
        limit = int(query_params.get("limit", DEFAULT_PAGE_SIZE))
        limit = max(1, min(limit, 100))  
    except (ValueError, TypeError):
        limit = DEFAULT_PAGE_SIZE

    # Build the Query parameters
    query_kwargs = {
        "KeyConditionExpression": Key("PK").eq(PK_VALUE),  
        "Limit": limit,
        "ScanIndexForward": False,  # Return newest orders first (reverse sort order)
    }

    # If the client sent a nextToken, decode and use it to continue pagination
    next_token = query_params.get("nextToken")
    if next_token:
        try:
            import base64
            decoded = json.loads(base64.b64decode(next_token).decode("utf-8"))
            query_kwargs["ExclusiveStartKey"] = decoded
        except Exception:
            return build_response(400, {"error": "Invalid nextToken value."})

    try:
        response = table.query(**query_kwargs)
    except Exception as e:
        logger.error(f"DynamoDB Query failed: {str(e)}")
        return build_response(500, {"error": "Failed to list orders."})

    # Clean the items (remove PK, SK)
    items = [
        {k: v for k, v in item.items() if k not in ("PK", "SK")}
        for item in response.get("Items", [])
    ]

    result = {
        "orders": items,
        "count":  len(items),
    }

    # If DynamoDB says there are more items, encode the cursor for the client
    if "LastEvaluatedKey" in response:
        import base64
        encoded = base64.b64encode(
            json.dumps(response["LastEvaluatedKey"]).encode("utf-8")
        ).decode("utf-8")
        result["nextToken"] = encoded
        result["hasMore"] = True
    else:
        result["hasMore"] = False

    logger.info(f"Returning {len(items)} orders")
    return build_response(200, result)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str)
    }