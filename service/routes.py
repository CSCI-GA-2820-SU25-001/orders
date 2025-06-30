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

    if customer_id:
        app.logger.info("Find by customer_id: %s", customer_id)
        orders = Order.find_by_customer(customer_id)
    else:
        app.logger.info("Find all")
        orders = Order.all()

    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


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

    # Verify required fields exist
    data = request.get_json()
    required = {"name", "product_id", "quantity"}
    missing = required - data.keys()
    if missing:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Missing required fields: {', '.join(missing)}",
        )

    # Insert the Order ID into the payload for OrderItem
    # Otherwise, OrderItem.deserialize() will error with KeyError
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
