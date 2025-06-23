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

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...
    def test_get_order(self):
        """It should return an order with its items"""
        # Create an order
        order = Order(name="Test Order", customer_id=123)
        order.create()

        # Add an order item manually
        item = OrderItem(
            name="Product A", quantity=2, order_id=order.id, product_id=456
        )
        item.create()

        # Refresh the order object to load related items
        order = Order.find(order.id)

        # Send GET request
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        # Check top-level order fields
        self.assertEqual(data["id"], order.id)
        self.assertEqual(data["name"], "Test Order")
        self.assertEqual(data["customer_id"], 123)

        # Check items list
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)

        item_data = data["items"][0]
        self.assertEqual(item_data["name"], "Product A")
        self.assertEqual(item_data["quantity"], 2)
        self.assertEqual(item_data["order_id"], order.id)
        self.assertEqual(item_data["product_id"], 456)

