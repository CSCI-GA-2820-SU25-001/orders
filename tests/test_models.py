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
from service.models import Order, OrderItem, DataValidationError, db
from .factories import OrderFactory, OrderItemFactory

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

    def test_all(self):
        """It should list all Orders"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)

        found = Order.all()
        self.assertEqual(len(found), 1)

        data = Order.find(order.id)
        self.assertEqual(data.name, order.name)

    def test_find(self):
        """It should find an Order by ID"""
        order = Order(name="Test Order", customer_id=123)
        order.create()

        found = Order.find(order.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, order.id)
        self.assertEqual(found.name, "Test Order")
        self.assertEqual(found.customer_id, 123)

    def test_malformed(self):
        """It should error when malformed data is deserialized"""
        self.assertRaises(DataValidationError, lambda: Order().deserialize({}))

    def test_find_by_customer(self):
        """It should find Orders by customer_id"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        self.assertIsNotNone(order.customer_id)

        found = Order.find_by_customer(order.customer_id)
        self.assertEqual(found.count(), 1)

        order_found = found.first()
        self.assertEqual(order_found.id, order.id)
        self.assertEqual(order_found.customer_id, order.customer_id)
        self.assertEqual(order_found.name, order.name)


######################################################################
#  OrderItem   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrderItem(TestCase):
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
        db.session.query(OrderItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_all(self):
        """It should list all OrderItems"""
        item = OrderItemFactory()
        item.create()
        self.assertIsNotNone(item.id)

        found = OrderItem.all()
        self.assertEqual(len(found), 1)

        data = OrderItem.find(item.id)
        self.assertEqual(data.name, item.name)

    def test_find(self):
        """It should find an Order by ID"""
        order = OrderItem(name="Test Order", product_id=123, quantity=5)
        order.create()

        found = OrderItem.find(order.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, order.id)
        self.assertEqual(found.name, "Test Order")
        self.assertEqual(found.product_id, 123)
        self.assertEqual(found.quantity, 5)

    def test_malformed(self):
        """It should error when malformed data is deserialized"""
        self.assertRaises(DataValidationError, lambda: OrderItem().deserialize({}))

    def test_find_by_product(self):
        """It should find Orders by product_id"""
        item = OrderItemFactory()
        item.create()
        self.assertIsNotNone(item.id)
        self.assertIsNotNone(item.product_id)

        found = OrderItem.find_by_product(item.product_id)
        self.assertEqual(found.count(), 1)

        item_found = found.first()
        self.assertEqual(item_found.id, item.id)
        self.assertEqual(item_found.product_id, item.product_id)
        self.assertEqual(item_found.quantity, item.quantity)
        self.assertEqual(item_found.name, item.name)

    def test_delete(self):
        """It should delete an OrderItem"""
        item = OrderItemFactory()
        item.create()
        self.assertIsNotNone(item.id)

        found = OrderItem.all()
        self.assertEqual(len(found), 1)

        item.delete()

        found = OrderItem.all()
        self.assertEqual(len(found), 0)
