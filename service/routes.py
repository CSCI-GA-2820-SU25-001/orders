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

import secrets
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Order, OrderItem
from service.common import http_status  # HTTP Status Codes

# Document the type of authorization required
authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}}

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Orders REST API Service",
    description="This is the API for the Orders service.",
    default="orders",
    default_label="Order operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    authorizations=authorizations,
    prefix="/api",  # THIS NEEDS TO BE REFLECTED IN test_routes.py's BASE_URL CONSTANT
)

# Configure the root route before OpenAPI


######################################################################
# GET INDEX
######################################################################
@app.get("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# GET HEALTH CHECK
######################################################################
@app.get("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), http_status.HTTP_200_OK


# Define the OrderItem model first since it's needed in create_order_model
create_order_item_model = api.model(
    "OrderItem",
    {
        "product_id": fields.Integer(
            required=True, description="The product this order item refers to"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the product"
        ),
    },
)

# Define the model so that the docs reflect what can be sent
create_order_model = api.model(
    "Order",
    {
        "customer_id": fields.Integer(
            required=True, description="The customer whom this order belongs to"
        ),
        "created_at": fields.DateTime(
            description="The date/time when this order was created. Set by the service.",
        ),
        "shipped_at": fields.DateTime(
            description="The date/time when this order was shipped. Set by the service.",
        ),
        "status": fields.String(description="The status of the order"),
        "order_items": fields.List(
            fields.Nested(create_order_item_model),
            description="List of order items to create with the order"
        ),
    },
)

order_model = api.inherit(
    "OrderModel",
    create_order_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

order_item_model = api.inherit(
    "OrderItemModel",
    create_order_item_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "order_id": fields.Integer(
            readOnly=True, description="The order this order item belongs to"
        ),
    },
)

# query string arguments
order_args = reqparse.RequestParser()
order_args.add_argument(
    "customer_id",
    type=int,
    location="args",
    required=False,
    help="List Orders by customer_id",
)
order_args.add_argument(
    "status", type=str, location="args", required=False, help="List Orders by status"
)


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /orders/{id} - Returns an Order with the id
    PUT /orders/{id} - Update an Order with the id
    DELETE /orders/{id} -  Deletes an Order with the id
    """

    ######################################################################
    # GET AN ORDER
    ######################################################################
    @api.doc("get_order")
    @api.response(404, "Order not found")
    def get(self, order_id: int):
        """Get an Order"""
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Check if only basic order info should be returned (use -o flag)
        only_order = request.args.get("o", "false").lower() == "true"

        return order.serialize(with_items=not only_order), 200

    ######################################################################
    # UPDATE AN ORDER
    ######################################################################
    @api.doc("update_order")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(order_model)
    def put(self, order_id: int):
        """
        Update an Order

        This endpoint will update an Order based on the body that is posted
        """
        app.logger.info("Request to Update an order with id [%s]", order_id)
        check_content_type("application/json")

        # Attempt to find the Order and abort if not found
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Update the Order with the new data
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        order.deserialize(data)

        # Save the updates to the database
        order.update()

        app.logger.info("Order with ID: %d updated.", order.id)
        return order.serialize(), http_status.HTTP_200_OK

    ######################################################################
    # DELETE AN ORDER
    ######################################################################
    @api.doc("delete_order")
    @api.response(204, "Order deleted")
    def delete(self, order_id: int):
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
        return "", http_status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """Handles all interactions with collections of Orders"""

    ######################################################################
    # LIST ORDERS
    ######################################################################
    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    def get(self):
        """Returns all of the Orders"""
        app.logger.info("Request for order list")

        orders = []

        # Parse any arguments from the query string
        customer_id = request.args.get("customer_id", type=int)
        status = request.args.get("status", type=str)
        only_order = request.args.get("o", "false").lower() == "true"

        if customer_id and status:
            app.logger.info(
                "Find by customer_id: %s and status: %s", customer_id, status
            )
            orders += Order.find_by_customer_and_status(customer_id, status)
        elif customer_id:
            app.logger.info("Find by customer_id: %s", customer_id)
            orders += Order.find_by_customer(customer_id)
        elif status:
            app.logger.info("Find by status: %s", status)
            orders += Order.find_by_status(status)
        else:
            app.logger.info("Find all")
            orders = Order.all()

        # Serialize orders with or without order_items based on query parameter
        results = [order.serialize(with_items=not only_order) for order in orders]

        app.logger.info("Returning %d orders", len(results))
        return results, http_status.HTTP_200_OK

    ######################################################################
    # CREATE A NEW ORDER
    ######################################################################
    @api.doc("create_order")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_order_model)
    def post(self):
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
        order.deserialize(data, require_fields=True)  # require customer_id on create

        # Save the new Order to the database
        order.create()
        app.logger.info("Order with new id [%s] saved!", order.id)

        # Return the location of the new Order
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)
        return (
            order.serialize(with_items=True),
            http_status.HTTP_201_CREATED,
            {"Location": location_url},
        )

    # ------------------------------------------------------------------
    # DELETE ALL ORDERS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_orders")
    @api.response(204, "All Orders deleted")
    def delete(self):
        """
        Delete all Orders

        This endpoint will delete all Orders only if the system is under testing mode
        """
        app.logger.info("Request to Delete all Orders...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Order.remove_all()
            app.logger.info("Removed all Orders from the database")
        else:
            app.logger.warning("Request to clear database while system not under test")

        return "", http_status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{id}/return
######################################################################
@api.route("/orders/<int:order_id>/return")
@api.param("order_id", "The Order identifier")
class ReturnOrder(Resource):
    """Return action for Order"""

    # pylint: disable=too-few-public-methods

    ######################################################################
    # RETURN ORDER
    ######################################################################
    @api.doc("return_order")
    @api.response(404, "Order not found")
    @api.response(400, "Order is not in 'shipped' status")
    @api.response(202, "Order returned")
    def put(self, order_id: int):
        """
        Return an entire order
        This endpoint allows users to return the entire order by changing its status to 'returned'
        """
        app.logger.info("Request to return order [%d]", order_id)

        # Check if the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Check order status - only allow returns for shipped orders
        if order.status != "shipped":
            abort(
                http_status.HTTP_400_BAD_REQUEST,
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

        return response_data, http_status.HTTP_202_ACCEPTED


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
@api.route("/orders/<int:order_id>/cancel")
@api.param("order_id", "The Order identifier")
class CancelOrder(Resource):
    """Cancel action for Order"""

    # pylint: disable=too-few-public-methods

    ######################################################################
    # CANCEL ORDER
    ######################################################################
    @api.doc("cancel_order")
    @api.response(404, "Order not found")
    @api.response(400, "Order is not in 'placed' status")
    @api.response(200, "Order canceled")
    def put(self, order_id: int):
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
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Check order status - only allow cancellation for placed orders (un-shipped)
        if order.status != "placed":
            abort(
                http_status.HTTP_400_BAD_REQUEST,
                f"Cannot cancel order with status '{order.status}'. Only orders with status 'placed' can be canceled.",
            )

        # Update order status to canceled
        order.status = "canceled"
        order.update()
        app.logger.info("Order [%d] status updated to 'canceled'", order_id)

        app.logger.info("Successfully canceled order [%d]", order_id)

        return order.serialize(), http_status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}/items/{id}
######################################################################
@api.route("/orders/<int:order_id>/items/<int:order_item_id>")
@api.param("order_id", "The order identifier")
@api.param("order_item_id", "The order item identifier")
class OrderItemResource(Resource):
    """OrderItemResource class"""

    ######################################################################
    # GET A SINGLE ORDER ITEM
    ######################################################################
    @api.doc("get_order_item")
    @api.response(404, "Order or order item not found")
    def get(self, order_id: int, order_item_id: int):
        """Get a specific OrderItem from an existing Order"""
        app.logger.info(
            "Request to get order_item [%d] from order [%d]", order_item_id, order_id
        )

        # Check if the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Check if the order_item exists and belongs to the correct order
        order_item = OrderItem.find(order_item_id)
        if not order_item or order_item.order_id != order_id:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
            )

        return order_item.serialize(), http_status.HTTP_200_OK

    ######################################################################
    # UPDATE AN ORDER ITEM
    ######################################################################
    @api.doc("update_order_item")
    @api.response(404, "Order or order item not found")
    @api.response(400, "The posted order item data was not valid")
    @api.expect(order_item_model)
    def put(self, order_id: int, order_item_id: int):
        """Update an OrderItem on an existing Order"""
        app.logger.info(
            "Request to update order_item [%d] from order [%d]", order_item_id, order_id
        )
        check_content_type("application/json")

        # Check if the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Check if the order_item exists and belongs to the correct order
        order_item = OrderItem.find(order_item_id)
        if not order_item or order_item.order_id != order_id:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
            )

        # Update the OrderItem with the request data
        data = request.get_json()
        app.logger.info(
            "Updating OrderItem [%s] on Order [%s]", order_item_id, order_id
        )

        # Prevent order_id from being modified during update
        if "order_id" in data:
            data.pop("order_id")
            app.logger.info("Removed order_id from update data to prevent modification")

        order_item.deserialize(data)

        # Save the new fields to the DB
        order_item.update()

        app.logger.info(
            "OrderItem [%d] on Order [%s] updated.", order_item_id, order_id
        )
        return order_item.serialize(), http_status.HTTP_200_OK

    ######################################################################
    # DELETE AN ORDER ITEM
    ######################################################################
    @api.doc("delete_order_item")
    @api.response(204, "Order item deleted")
    def delete(self, order_id: int, order_item_id: int):
        """Delete a specific OrderItem from an existing Order"""
        app.logger.info(
            "Request to delete order_item [%d] from order [%d]", order_item_id, order_id
        )

        # Check if the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
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
            return "", http_status.HTTP_204_NO_CONTENT

        # Item exists but doesn't belong to the given order → 404
        if order_item.order_id != order_id:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"OrderItem with id '{order_item_id}' was not found in order '{order_id}'.",
            )

        order_item.delete()
        app.logger.info(
            "OrderItem [%d] from Order [%d] deleted.", order_item_id, order_id
        )
        return "", http_status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{id}/items
######################################################################
@api.route("/orders/<int:order_id>/items")
@api.param("order_id", "The order identifier")
class OrderItemCollection(Resource):
    """OrderItemCollection class"""

    ######################################################################
    # LIST ORDER ITEMS
    ######################################################################
    @api.doc("list_order_items")
    @api.response(404, "Order not found")
    def get(self, order_id: int):
        """Returns all of the OrderItems for a specific Order"""
        app.logger.info("Request for List Order Items for Order id [%d]", order_id)

        # Check if the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        order_items = OrderItem.find_by_order_id(order_id)

        # It doesn't really make sense to filter by anything here,
        # because filtering by product_id will always get you one OrderItem
        # (assuming the shopcart team knows what they're doing), and
        # filtering by quantity gets you every OrderItem with the same
        # quantity, which isn't very useful to the user.

        results = [item.serialize() for item in order_items]
        app.logger.info("Returning %d order items", len(results))
        return results, http_status.HTTP_200_OK

    ######################################################################
    # CREATE A NEW ORDER ITEM
    ######################################################################
    @api.doc("create_order_item")
    @api.response(404, "Order not found")
    @api.response(400, "The posted data was not valid")
    @api.response(201, "Order item created")
    @api.expect(create_order_item_model)
    def post(self, order_id: int):
        """Create an OrderItem and attach it to an existing Order"""
        app.logger.info("Request to create an OrderItem for order %d", order_id)
        check_content_type("application/json")

        # Check that the order exists
        order = Order.find(order_id)
        if not order:
            abort(
                http_status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        data = request.get_json()

        # Insert the Order ID into the payload for OrderItem
        # Now, OrderItem.deserialize() wont error with KeyError
        data["order_id"] = order_id

        # Create the order item in the DB
        order_item = OrderItem()
        order_item.deserialize(data)
        order_item.create()

        # Get a Location URL for the order item
        location_url = api.url_for(
            OrderItemResource,
            order_id=order_id,
            order_item_id=order_item.id,
            _external=True,
        )

        return (
            order_item.serialize(),
            http_status.HTTP_201_CREATED,
            {"Location": location_url},
        )


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
            http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
