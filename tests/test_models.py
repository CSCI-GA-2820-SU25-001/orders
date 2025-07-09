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
Test cases for Order Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from datetime import datetime, UTC
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
        # Clean up OrderItems first due to foreign key constraint
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
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

        (order_found,) = found
        self.assertIsNotNone(order_found)
        self.assertEqual(order_found.id, order.id)
        self.assertEqual(order_found.customer_id, order.customer_id)

    def test_find(self):
        """It should find an Order by ID"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)

        found = Order.find(order.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, order.id)
        self.assertEqual(found.customer_id, order.customer_id)

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

    def test_order_create_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when creating an order"""
        o = OrderFactory()
        with patch.object(db.session, "commit", side_effect=Exception("boom")):
            with self.assertRaises(DataValidationError):
                o.create()

    def test_order_update_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when updating an order"""
        o = OrderFactory()
        o.create()
        with patch.object(db.session, "commit", side_effect=Exception("oops")):
            with self.assertRaises(DataValidationError):
                o.update()

    def test_order_delete_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when deleting an order"""
        o = OrderFactory()
        o.create()
        with patch.object(db.session, "commit", side_effect=Exception("fail")):
            with self.assertRaises(DataValidationError):
                o.delete()


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
        # Clean up both OrderItems and Orders to avoid foreign key issues
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
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

    def test_find(self):
        """It should find an Order by ID"""
        item = OrderItemFactory()
        item.create()
        self.assertIsNotNone(item.id)

        found = OrderItem.find(item.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, item.id)
        self.assertEqual(found.product_id, item.product_id)
        self.assertEqual(found.quantity, item.quantity)
        self.assertEqual(found.order_id, item.order_id)

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
        self.assertEqual(item_found.order_id, item.order_id)

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

    def test_orderitem_create_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when creating an order item"""
        i = OrderItemFactory()
        with patch.object(db.session, "commit", side_effect=Exception("boom")):
            with self.assertRaises(DataValidationError):
                i.create()

    def test_orderitem_update_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when updating an order item"""
        i = OrderItemFactory()
        i.create()
        with patch.object(db.session, "commit", side_effect=Exception("oops")):
            with self.assertRaises(DataValidationError):
                i.update()

    def test_orderitem_delete_raises_error_on_commit_fail(self):
        """It should raise DataValidationError on commit failure when deleting an order item"""
        i = OrderItemFactory()
        i.create()
        with patch.object(db.session, "commit", side_effect=Exception("fail")):
            with self.assertRaises(DataValidationError):
                i.delete()

    def test_orderitem_deserialize_missing_product_id(self):
        """It should raise DataValidationError when product_id is missing"""
        # Missing "product_id" → KeyError branch
        bad = {"quantity": 2, "order_id": 5}
        with self.assertRaises(DataValidationError) as cm:
            OrderItem().deserialize(bad)
        self.assertIn("missing product_id", str(cm.exception))

    def test_orderitem_deserialize_type_error(self):
        """It should raise DataValidationError when deserializing with bad data"""
        # Passing None (not a dict) → TypeError branch
        with self.assertRaises(DataValidationError) as cm:
            OrderItem().deserialize(None)
        self.assertIn("bad or no data", str(cm.exception))

    def test_find_by_order_id(self):
        """It should find OrderItems by order_id"""
        item = OrderItemFactory()
        item.create()

        found = OrderItem.find_by_order_id(item.order_id)
        self.assertEqual(found.count(), 1)

        item_found: OrderItem | None = found.first()
        self.assertIsNotNone(item_found)
        self.assertEqual(item_found.id, item.id)
        self.assertEqual(item_found.quantity, item.quantity)
        self.assertEqual(item_found.order_id, item.order_id)
        self.assertEqual(item_found.product_id, item.product_id)

    # -----------------------------------------------------------------
    # STATUS FIELD TESTS
    # -----------------------------------------------------------------

    def test_default_status_is_placed(self):
        """It should set status to 'placed' when none is supplied"""
        order = Order(customer_id=1)
        order.create()
        self.assertEqual(order.status, "placed")

        found = Order.find(order.id)
        self.assertEqual(found.status, "placed")

    def test_create_with_valid_status(self):
        """It should create an Order with an explicit valid status"""
        order = OrderFactory(status="shipped")
        order.create()

        found = Order.find(order.id)
        self.assertEqual(found.status, "shipped")

    def test_update_status(self):
        """It should update an Order's status"""
        order = OrderFactory(status="placed")
        order.create()

        # simulate deserialization from API payload
        order.deserialize(
            {
                "customer_id": order.customer_id,
                "status": "canceled",
                "created_at": order.created_at,
                "shipped_at": order.shipped_at,
            }
        )
        order.update()

        found = Order.find(order.id)
        self.assertEqual(found.status, "canceled")

    def test_invalid_status_raises(self):
        """It should raise DataValidationError when status is invalid"""
        bad = OrderFactory().serialize()
        bad["status"] = "invalid_status"

        self.assertRaises(DataValidationError, lambda: Order().deserialize(bad))

    # -----------------------------------------------------------------
    # shipped_at FIELD TESTS
    # -----------------------------------------------------------------
    def test_shipped_at_set_on_create(self):
        """If an order is created as 'shipped', shipped_at is auto filled AFTER the order is shipped"""
        before = datetime.now(UTC)
        order = Order(status= "shipped")
        order.create()
        after = datetime.now(UTC)
        found = Order.find(order.id)

        self.assertEqual(found.status, "shipped")
        self.assertIsNotNone(found.shipped_at)
        self.assertTrue(before <= found.shipped_at <= after)

    def test_shipped_at_not_set_for_placed(self):
        """If status is not shipped, shipped_at stays None"""
        order = Order(status= "placed")
        order.create()
        self.assertIsNone(order.shipped_at)

    def test_shipped_at_is_set_after_update(self):
        """If status updates from placed to shipped, shipped_at should be set"""
        order = Order(status = "placed")
        order.create()
        self.assertIsNone(order.shipped_at)

        order.status = "shipped"
        order.update()
        self.assertIsNotNone(order.shipped_at)

    def test_factory_creates_valid_order(self):
        order = OrderFactory()
        order.create()

        found = Order.find(order.id)
        self.assertEqual(found.status, order.status)
        if order.status == "shipped":
            self.assertIsNotNone(found.shipped_at)
        else:
            self.assertIsNone(found.shipped_at)
        
    # -----------------------------------------------------------------
    # created_at FIELD TESTS
    # -----------------------------------------------------------------
    def test_created_at_set_on_create(self):
        """If an order is created, created_at is auto filled AFTER the order is created"""
        before = datetime.now(UTC)
        order = Order(status="placed")
        order.create()
        after = datetime.now(UTC)
        found = Order.find(order.id)

        self.assertEqual(found.status, "placed")
        self.assertIsNotNone(found.created_at)
        self.assertTrue(before <= found.created_at <= after)

    def test_created_at_immutable(self):
        """If an order is created, created_at is auto filled and not change for any status update"""
        order = OrderFactory(status="placed")
        order.create()

        first_ts = order.created_at

        order.status = "returned"
        order.update()

        self.assertEqual(order.created_at, first_ts)