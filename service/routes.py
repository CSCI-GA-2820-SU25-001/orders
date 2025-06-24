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
        "Reminder: return some useful information in json format about the service here",
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
# UPDATE AN ORDER
######################################################################
@app.put("/orders/<order_id>")
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
# GET A NEW ORDER
######################################################################
@app.get("/orders/<int:order_id>")
def get_order(order_id):
    order = Order.find(order_id)
    if not order:
        abort(404)
    return jsonify(order.serialize()), 200

######################################################################
# CREATE A NEW ORDER ITEM
######################################################################
@app.post("/orders/<int:order_id>/items")
def create_item(order_id: int):
    """Create an OrderItem and attach it to an existing Order"""
    app.logger.info("Request to create an OrderItem for order %d", order_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    data = request.get_json()
    required = {"name", "product_id", "quantity"}
    missing = required - data.keys()
    if missing:
        abort(status.HTTP_400_BAD_REQUEST,
              f"Missing required fields: {', '.join(missing)}")

    order_item = OrderItem()
    order_item.deserialize(data)
    order_item.order_id = order_id

    order_item.create()

    #TODO: Uncomment when get order item is implemented
    # Return the location of the new Order
    # location_url = url_for(
    #     "get_item",  # to define : /orders/<int:order_id>/items/<int:item_id>
    #     order_id=order_id,
    #     item_id=order_item.id,
    #     _external=True,
    # )
    location_url = "unknown"
    return jsonify(order_item.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

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
