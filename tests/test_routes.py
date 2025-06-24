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
TestOrder API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from .factories import OrderFactory, OrderItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrder(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create orders
    ############################################################
    def _create_orders(self, count: int = 1) -> list:
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            test_order = OrderFactory()
            response = self.client.post(BASE_URL, json=test_order.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test order",
            )
            new_order = response.get_json()
            test_order.id = new_order["id"]
            orders.append(test_order)
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE ORDER
    # ----------------------------------------------------------
    def test_create_order(self):
        """It should Create a new Order"""
        test_order = OrderFactory()
        logging.debug("Test Order: %s", test_order.serialize())
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = response.get_json()
        self.assertEqual(new_order["name"], test_order.name)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_order = response.get_json()
        self.assertEqual(new_order["name"], test_order.name)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)

    # ----------------------------------------------------------
    # TEST GET
    # ----------------------------------------------------------
    def test_get_order(self):
        """It should Get an existing Order by ID"""
        # First create and save an order
        test_order = OrderFactory()
        test_order.create()

        # Send GET request to /orders/<id>
        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check returned data
        data = response.get_json()
        self.assertEqual(data["id"], test_order.id)
        self.assertEqual(data["name"], test_order.name)
        self.assertEqual(data["customer_id"], test_order.customer_id)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_order(self):
        """It should Delete an order"""
        test_order = self._create_orders(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_order(self):
        """It should Delete an order even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_order(self):
        """It should Update an existing Order"""
        # create a order to update
        test_order = OrderFactory()
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = response.get_json()
        logging.debug(new_order)
        new_order["name"] = "unknown"
        new_order["customer_id"] = -1
        response = self.client.put(f"{BASE_URL}/{new_order['id']}", json=new_order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = response.get_json()
        self.assertEqual(updated_order["name"], "unknown")
        self.assertEqual(updated_order["customer_id"], -1)

    def test_create_order_item(self):
        """It should create a new OrderItem inside an existing Order"""
       
        order = OrderFactory()
        response = self.client.post(BASE_URL, json=order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.get_json()["id"]

        order_item = OrderItemFactory()
        payload = {
            "name":       order_item.name,
            "product_id": order_item.product_id,
            "quantity":   order_item.quantity,
        }

        # 3) Appel POST /orders/<id>/items
        url = f"{BASE_URL}/{order_id}/item"
        resp = self.client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


         # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check that the location header was correct
        #TODO: Uncomment after get endpoint is defined
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["order_id"],   order_id)
        self.assertEqual(data["product_id"], payload["product_id"])
        self.assertEqual(data["quantity"],   payload["quantity"])
        self.assertEqual(data["name"],       payload["name"])

    # ----------------------------------------------------------
    # TEST GET ORDER LIST
    # ----------------------------------------------------------
    def test_get_order_list(self):
        """It should Get a list of Orders"""
        # list the order
        self._create_orders(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
