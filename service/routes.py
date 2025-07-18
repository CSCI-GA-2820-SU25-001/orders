######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Order
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, OrderItem
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            {
                "service": "orders",
                "operations": {
                    "create": "POST /orders",
                    "get": "GET /orders/<order_id>",
                    "update": "PUT /orders/<order_id>",
                    "delete": "DELETE /orders/<order_id>",
                    "list": "GET /orders",
                    "cancel": "PUT /orders/<order_id>/cancel",
                    "return": "PUT /orders/<order_id>/return",
                },
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.post("/orders")
def create_order():
    """
    Create an Order
    This endpoint will create a Order based the data in the body that is posted
    """
    app.logger.info("Request to Create a Order...")
    check_content_type("application/json")

    order = Order()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    # Save the new Order to the database
    order.create()
    app.logger.info("Order with new id [%s] saved!", order.id)

    # Return the location of the new Order
    location_url = url_for("get_order", order_id=order.id, _external=True)
    return (
        jsonify(order.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# GET AN ORDER
######################################################################
@app.get("/orders/<int:order_id>")
def get_order(order_id: int):
    """Get an Order"""
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Check if only basic order info should be returned (use -o flag)
    only_order = request.args.get("o", "false").lower() == "true"

    if only_order:
        # Return basic order info without order_items
        return (
            jsonify(
                {
                    "id": order.id,
                    "customer_id": order.customer_id,
                    "status": order.status,
                }
            ),
            200,
        )

    # Default: return full order with order_items
    return jsonify(order.serialize()), 200


######################################################################
# UPDATE AN ORDER
######################################################################
@app.put("/orders/<int:order_id>")
def update_order(order_id: int):
    """
    Update an Order

    This endpoint will update an Order based on the body that is posted
    """
    app.logger.info("Request to Update an order with id [%s]", order_id)
    check_content_type("application/json")

    # Attempt to find the Order and abort if not found
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update the Order with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    # Save the updates to the database
    order.update()

    app.logger.info("Order with ID: %d updated.", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
######################################################################
@app.delete("/orders/<int:order_id>")
def delete_order(order_id: int):
    """
    Delete an Order

    This endpoint will delete an Order based on the id specified in the path
    """
    app.logger.info("Request to Delete an Order with id [%s]", order_id)

    order = Order.find(order_id)
    if order:
        app.logger.info("Order with ID: %d found.", order.id)
        order.delete()

    app.logger.info("Order with ID: %d delete complete.", order_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ORDERS
######################################################################
@app.get("/orders")
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for order list")

    orders = []

    # Parse any arguments from the query string
    customer_id = request.args.get("customer_id", type=int)
    only_order = request.args.get("o", "false").lower() == "true"

    if customer_id:
        app.logger.info("Find by customer_id: %s", customer_id)
        orders = Order.find_by_customer(customer_id)
    else:
        app.logger.info("Find all")
        orders = Order.all()

    # Serialize orders with or without order_items based on query parameter
    if only_order:
        # Return basic order info without order_items
        results = [
            {"id": order.id, "customer_id": order.customer_id, "status": order.status}
            for order in orders
        ]
    else:
        # Default: return full orders with order_items
        results = [order.serialize() for order in orders]

    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETURN ORDER
######################################################################
@app.put("/orders/<int:order_id>/return")
def return_order(order_id: int):
    """
    Return an entire order
    This endpoint allows users to return the entire order by changing its status to 'returned'
    """
    app.logger.info("Request to return order [%d]", order_id)

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Check order status - only allow returns for shipped orders
    if order.status != "shipped":
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot return order with status '{order.status}'. Only orders with status 'shipped' can be returned.",
        )

    # Update order status to returned
    order.status = "returned"
    order.update()
    app.logger.info("Order [%d] status updated to 'returned'", order_id)

    # Prepare response
    response_data = {
        "order_id": order_id,
        "status": order.status,
    }

    app.logger.info("Successfully returned order [%d]", order_id)

    return jsonify(response_data), status.HTTP_202_ACCEPTED


######################################################################
# CANCEL ORDER
######################################################################
@app.put("/orders/<int:order_id>/cancel")
def cancel_order(order_id: int):
    """
    Cancel an order
    This endpoint allows users to cancel an order by changing its status to 'canceled'
    Only orders with 'placed' status can be canceled (un-shipped orders)
    """
    app.logger.info("Request to cancel order [%d]", order_id)

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Check order status - only allow cancellation for placed orders (un-shipped)
    if order.status != "placed":
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot cancel order with status '{order.status}'. Only orders with status 'placed' can be canceled.",
        )

    # Update order status to canceled
    order.status = "canceled"
    order.update()
    app.logger.info("Order [%d] status updated to 'canceled'", order_id)

    app.logger.info("Successfully canceled order [%d]", order_id)

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW ORDER ITEM
######################################################################
@app.post("/orders/<int:order_id>/items")
def create_order_item(order_id: int):
    """Create an OrderItem and attach it to an existing Order"""
    app.logger.info("Request to create an OrderItem for order %d", order_id)
    check_content_type("application/json")

    # Check that the order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    data = request.get_json()

    # Insert the Order ID into the payload for OrderItem
    # Now, OrderItem.deserialize() wont error with KeyError
    data["order_id"] = order_id

    # Create the order item in the DB
    order_item = OrderItem()
    order_item.deserialize(data)
    order_item.create()

    # Get a Location URL for the order item
    location_url = url_for(
        "get_order_item",  # defined: /orders/<int:order_id>/items/<int:item_id>
        order_id=order_id,
        order_item_id=order_item.id,
        _external=True,
    )

    return (
        jsonify(order_item.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# GET A SINGLE ORDER ITEM
######################################################################
@app.get("/orders/<int:order_id>/items/<int:order_item_id>")
def get_order_item(order_id: int, order_item_id: int):
    """Get a specific OrderItem from an existing Order"""
    app.logger.info(
        "Request to get order_item [%d] from order [%d]", order_item_id, order_id
    )

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Check if the order_item exists and belongs to the correct order
    order_item = OrderItem.find(order_item_id)
    if not order_item or order_item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
        )

    return jsonify(order_item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ORDER ITEM
######################################################################
@app.put("/orders/<int:order_id>/items/<int:order_item_id>")
def update_order_item(order_id: int, order_item_id: int):
    """Update an OrderItem on an existing Order"""
    app.logger.info(
        "Request to update order_item [%d] from order [%d]", order_item_id, order_id
    )
    check_content_type("application/json")

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Check if the order_item exists and belongs to the correct order
    order_item = OrderItem.find(order_item_id)
    if not order_item or order_item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
        )

    # Update the OrderItem with the request data
    data = request.get_json()
    app.logger.info("Updating OrderItem [%s] on Order [%s]", order_item_id, order_id)

    # Prevent order_id from being modified during update
    if "order_id" in data:
        data.pop("order_id")
        app.logger.info("Removed order_id from update data to prevent modification")

    order_item.deserialize(data)

    # Save the new fields to the DB
    order_item.update()

    app.logger.info("OrderItem [%d] on Order [%s] updated.", order_item_id, order_id)
    return jsonify(order_item.serialize()), status.HTTP_200_OK


######################################################################
# LIST ORDER ITEMS
######################################################################
@app.get("/orders/<int:order_id>/items")
def list_order_items(order_id: int):
    """Returns all of the OrderItems for a specific Order"""
    app.logger.info("Request for List Order Items for Order id [%d]", order_id)
    order_items = OrderItem.find_by_order_id(order_id)

    # It doesn't really make sense to filter by anything here,
    # because filtering by product_id will always get you one OrderItem
    # (assuming the shopcart team knows what they're doing), and
    # filtering by quantity gets you every OrderItem with the same
    # quantity, which doesn't seem very useful to the user.

    results = [item.serialize() for item in order_items]
    app.logger.info("Returning %d order items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER ITEM
######################################################################
@app.delete("/orders/<int:order_id>/items/<int:order_item_id>")
def delete_order_item(order_id: int, order_item_id: int):
    """Delete a specific OrderItem from an existing Order"""
    app.logger.info(
        "Request to delete order_item [%d] from order [%d]", order_item_id, order_id
    )

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Check if the item exists and belongs to the correct order
    order_item = OrderItem.find(order_item_id)
    # If item doesn't exist at all → 204
    if not order_item:
        app.logger.info(
            "OrderItem [%d] not found. Nothing to delete, returning 204.",
            order_item_id,
        )
        return {}, status.HTTP_204_NO_CONTENT

    # Item exists but doesn't belong to the given order → 404
    if order_item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
        )

    order_item.delete()
    app.logger.info("OrderItem [%d] from Order [%d] deleted.", order_item_id, order_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type: str) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
