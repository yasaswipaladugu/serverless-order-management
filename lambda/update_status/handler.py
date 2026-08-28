
# This Lambda handles: PATCH /orders/{orderId}/status
# Its job:
#   1. Get the current order from DynamoDB
#   2. Check if the requested status transition is allowed
#   3. If allowed → update with a ConditionExpression (prevents race conditions)
#   4. If not allowed → return 409 Conflict with a clear error message

import json
import os
import logging
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

PK_VALUE = "ORDER"

# State machine: defines ALL valid transitions
ALLOWED_TRANSITIONS = {
    "PENDING":    ["CONFIRMED", "CANCELLED"],
    "CONFIRMED":  ["PROCESSING", "CANCELLED"],
    "PROCESSING": ["SHIPPED"],
    "SHIPPED":    ["DELIVERED"],
    "DELIVERED":  [],   # Final state — nothing is allowed
    "CANCELLED":  [],   # Final state — nothing is allowed
}

VALID_STATUSES = set(ALLOWED_TRANSITIONS.keys())


def lambda_handler(event, context):
    logger.info("update_status invoked")
    logger.info(f"Event received: {json.dumps(event)}")

    # 1. Get orderId from the URL path 
    path_params = event.get("pathParameters") or {}
    order_id = path_params.get("orderId")

    if not order_id:
        return build_response(400, {"error": "Missing orderId in path."})

    # 2. Parse and validate the request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return build_response(400, {"error": "Request body must be valid JSON."})

    new_status = body.get("status")
    if not new_status:
        return build_response(400, {"error": "Missing 'status' in request body."})

    # Normalize to uppercase so "confirmed" and "CONFIRMED" both work
    new_status = new_status.upper().strip()

    if new_status not in VALID_STATUSES:
        return build_response(400, {
            "error": f"'{new_status}' is not a valid status.",
            "validStatuses": list(VALID_STATUSES)
        })

    # 3. Get the current order
    try:
        response = table.get_item(
            Key={"PK": PK_VALUE, "SK": order_id}
        )
    except Exception as e:
        logger.error(f"DynamoDB GetItem failed: {str(e)}")
        return build_response(500, {"error": "Failed to retrieve order."})

    item = response.get("Item")
    if not item:
        return build_response(404, {"error": f"Order '{order_id}' not found."})

    current_status = item["status"]
    logger.info(f"Order {order_id}: current status={current_status}, requested={new_status}")

    # 4. Check if the transition is allowed
    allowed_next = ALLOWED_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_next:
        # Build a helpful error message explaining exactly why it was rejected
        if not allowed_next:
            reason = f"Orders in '{current_status}' state are final and cannot be updated."
        else:
            reason = (
                f"Cannot transition from '{current_status}' to '{new_status}'. "
                f"Allowed transitions from '{current_status}': {allowed_next}"
            )
        logger.warning(f"Invalid transition rejected: {current_status} → {new_status}")
        return build_response(409, {   # 409 = Conflict
            "error": "Invalid state transition.",
            "detail": reason,
            "currentStatus": current_status,
            "requestedStatus": new_status,
        })

    # 5. Update DynamoDB with a ConditionExpression
   

    now = datetime.now(timezone.utc).isoformat()

    try:
        result = table.update_item(
            Key={"PK": PK_VALUE, "SK": order_id},
            UpdateExpression="SET #st = :new_status, updatedAt = :now",
            # ConditionExpression: only update if status in DB still equals current_status
            ConditionExpression=Attr("status").eq(current_status),
            ExpressionAttributeNames={
                "#st": "status"   
            },
            ExpressionAttributeValues={
                ":new_status": new_status,
                ":now":        now,
            },
            ReturnValues="ALL_NEW"   
        )
        logger.info(f"Order {order_id} updated: {current_status} → {new_status}")

    except ClientError as e:
        # This specific error means ConditionExpression failed
       
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.warning(f"Concurrent update conflict for order {order_id}")
            return build_response(409, {
                "error": "Conflict: the order status was changed by another request. Please retry."
            })
        # Any other DynamoDB error
        logger.error(f"DynamoDB UpdateItem failed: {str(e)}")
        return build_response(500, {"error": "Failed to update order status."})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return build_response(500, {"error": "Failed to update order status."})

    # 6. Return the updated order
    updated_item = result.get("Attributes", {})
    clean_item = {k: v for k, v in updated_item.items() if k not in ("PK", "SK")}
    return build_response(200, clean_item)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str)
    }