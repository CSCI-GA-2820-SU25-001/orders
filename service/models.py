"""
Models for Order

All of the models are stored in this module
"""

import logging
from typing import Any
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

ALLOWED_STATUS = {"placed", "shipped", "returned", "canceled"}
DEFAULT_STATUS = "placed"


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Order(db.Model):
    """
    Class that represents an order
    """

    __tablename__ = "Order"
    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    status = db.Column(db.String(16), nullable=False, default="placed")
    # maybe store any promotions used on this order?
    
    # Relationship to OrderItem with cascade delete
    order_items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def create(self):
        """
        Creates an order in the database
        """
        logger.info("Creating %s", self)
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates an order in the database
        """
        logger.info("Saving %s", self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an order from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self) -> dict[str, Any]:
        """Serializes an order into a dictionary"""
        return {
            "id": self.id, 
            "customer_id": self.customer_id, 
            "status": self.status,
            "order_items": [item.serialize() for item in self.order_items]
        }

    def deserialize(self, data: dict[str, Any]):
        """
        Deserializes an order from a dictionary
        """
        try:
            self.customer_id = data["customer_id"]
            status = str(data.get("status", self.status or DEFAULT_STATUS)).lower()

            if status not in ALLOWED_STATUS:
                raise DataValidationError(f"Invalid status '{status}'")

            self.status = status
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls) -> list["Order"]:
        """Returns all of the Orders in the database"""
        logger.info("Processing all Orders")
        return cls.query.all()  # type: ignore

    @classmethod
    def find(cls, by_id: Any):
        """Finds a Order by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_customer(cls, customer_id: Any):
        """Returns all orders with the given customer ID"""
        logger.info("Processing Order query with customer_id=%s", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)


class OrderItem(db.Model):
    """
    Class that represents an order item
    """

    __tablename__ = "OrderItem"
    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    order_id = db.Column(db.Integer, db.ForeignKey("Order.id"), nullable=False)
    product_id = db.Column(db.Integer)

    def create(self):
        """
        Creates an order item in the database
        """
        logger.info("Creating %s", self)
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates an order item in the database
        """
        logger.info("Saving %s", self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an order item from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self) -> dict[str, Any]:
        """Serializes an order item into a dictionary"""
        return {
            "id": self.id,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "product_id": self.product_id,
        }

    def deserialize(self, data: dict[str, Any]):
        """
        Deserializes an order item from a dictionary

        Args:
            data (dict): A dictionary containing the order data
        """
        try:
            # order_id is optional - can be set through relationship
            if "order_id" in data:
                self.order_id = data["order_id"]
            self.quantity = data["quantity"]
            self.product_id = data["product_id"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid OrderItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid OrderItem: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls) -> list["OrderItem"]:
        """Returns all of the order items in the database"""
        logger.info("Processing all order items")
        return cls.query.all()  # type: ignore

    @classmethod
    def find(cls, by_id: Any):
        """Finds an order item by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_order_id(cls, order_id: Any):
        """Returns all order items with the given order ID"""
        logger.info("Processing OrderItem lookup by order_id=%s", order_id)
        return cls.query.filter(cls.order_id == order_id)

    @classmethod
    def find_by_product(cls, product_id: Any):
        """Returns all order items with the given product ID"""
        logger.info("Processing OrderItem lookup by product_id=%s", product_id)
        return cls.query.filter(cls.product_id == product_id)
