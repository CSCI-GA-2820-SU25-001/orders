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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Order, db
from .factories import OrderFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Order   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrder(TestCase):
    """Test Cases for Order Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """It should create a Order"""

        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        found = Order.all()
        self.assertEqual(len(found), 1)
        data = Order.find(order.id)
        self.assertEqual(data.name, order.name)

    # Todo: Add your test cases here...
    def test_find_order(self):
        """It should find an Order by ID"""
        order = Order(name="Test Order", customer_id=123)
        order.create()

        found = Order.find(order.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, order.id)
        self.assertEqual(found.name, "Test Order")
        self.assertEqual(found.customer_id, 123)
        self.assertEqual(len(found.items), 0)

    def test_serialize_order_with_items(self):
        """It should serialize an Order with its items"""
        order = Order(name="Order with item", customer_id=1)
        order.create()

        item = OrderItem(name="Item A", quantity=3, product_id=111, order_id=order.id)
        item.create()

        order = Order.find(order.id)
        data = order.serialize()

        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["name"], "Item A")

    def test_delete_order_cascades_items(self):
        """It should delete related items when an order is deleted"""
        order = Order(name="Order to delete", customer_id=2)
        order.create()

        item = OrderItem(
            name="Item to delete", quantity=1, product_id=222, order_id=order.id
        )
        item.create()

        self.assertEqual(len(OrderItem.find_by_order_id(order.id).all()), 1)

        order.delete()

        # After deletion, items should also be gone
        items = OrderItem.find_by_order_id(order.id).all()
        self.assertEqual(len(items), 0)
