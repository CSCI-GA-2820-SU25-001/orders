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


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Order(db.Model):
    """
    Class that represents an order
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    customer_id = db.Column(db.Integer)
    # maybe store any promotions used on this order?

    # Todo: Place the rest of your schema here...

    def __repr__(self):
        return f"<Order name='{self.name}' id={self.id} customer_id={self.customer_id}>"

    def create(self):
        """
        Creates an order in the database
        """
        logger.info("Creating %s", self)
        self.id = None  # pylint: disable=invalid-name
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
        return {"id": self.id, "name": self.name, "customer_id": self.customer_id}

    def deserialize(self, data: dict[str, Any]):
        """Deserializes an order from a dictionary"""
        try:
            self.name = data["name"]
            self.customer_id = data["customer_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
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
        """Finds a Order by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name: str):
        """Returns all Orders with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_customer(cls, customer_id: Any):
        """Returns all orders with the given customer ID"""
        logger.info("Processing Order query with customer_id=%s", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)


class OrderItem(db.Model):
    """
    Class that represents an order item
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    quantity = db.Column(db.Integer)
    order_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    # Todo: Place the rest of your schema here...

    def __repr__(self):
        return (
            f"<OrderItem name='{self.name}' id={self.id} quantity={self.quantity} "
            f"order_id={self.order_id} product_id={self.product_id}>"
        )

    def create(self):
        """
        Creates an order item in the database
        """
        logger.info("Creating %s", self)
        self.id = None  # pylint: disable=invalid-name
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
            "name": self.name,
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
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.order_id = data["order_id"]
            self.product_id = data["product_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
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
    def find_by_name(cls, name: str):
        """Returns all order items with the given name

        Args:
            name (string): the name of the order items you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_order_id(cls, order_id: Any):
        """Returns all order items with the given order ID"""
        logger.info("Processing OrderItem lookup by order_id=%s", order_id)
        return cls.query.filter(cls.order_id == order_id)

    @classmethod
    def find_by_product_id(cls, product_id: Any):
        """Returns all order items with the given product ID"""
        logger.info("Processing OrderItem lookup by product_id=%s", product_id)
        return cls.query.filter(cls.product_id == product_id)
