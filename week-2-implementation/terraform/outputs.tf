# The base URL of your API which will be used in all curl/Postman tests

output "api_base_url" {
  description = "Base URL for the OrderFlow API"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

# Quick-reference for all 4 endpoint URLs

output "endpoint_create_order" {
  description = "POST /orders"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/orders"
}

output "endpoint_get_order" {
  description = "GET /orders/{orderId}"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/orders/{orderId}"
}

output "endpoint_list_orders" {
  description = "GET /orders"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/orders"
}

output "endpoint_update_status" {
  description = "PATCH /orders/{orderId}/status"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/orders/{orderId}/status"
}
