$API = "https://cu0qh9j5d7.execute-api.eu-central-1.amazonaws.com"

# 1. Create order
$order = Invoke-RestMethod -Method POST -Uri "$API/orders" `
  -ContentType "application/json" `
  -Body '{"customerId": "C1001", "items": [{"productId": "P100", "quantity": 2}], "totalAmount": 49.98}'
$order
$orderId = $order.orderId

# 2. Get the order
Invoke-RestMethod -Method GET -Uri "$API/orders/$orderId"

# 3. List all orders
$list = Invoke-RestMethod -Method GET -Uri "$API/orders"
$list.orders | ConvertTo-Json -Depth 5

# 4. Update status - valid transition
Invoke-RestMethod -Method PATCH -Uri "$API/orders/$orderId/status" `
  -ContentType "application/json" -Body '{"status": "CONFIRMED"}'

# 5. Update status - invalid transition
try {
  Invoke-RestMethod -Method PATCH -Uri "$API/orders/$orderId/status" `
    -ContentType "application/json" -Body '{"status": "PENDING"}'
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}

# 6. Missing fields
try {
  Invoke-RestMethod -Method POST -Uri "$API/orders" `
    -ContentType "application/json" -Body '{"customerId": "C1001"}'
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}

# 7. Order not found
try {
  Invoke-RestMethod -Method GET -Uri "$API/orders/ord-doesnotexist"
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}


# pick one order from the list
Invoke-RestMethod -Method GET -Uri "$API/orders/ord-631fef28-a1d1-460e-82a2-a45cfcdcc398"