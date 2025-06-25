"""
Test Factory to make fake objects for testing
"""

from datetime import datetime
import factory
from service.models import Order, OrderItem


class OrderFactory(factory.Factory):
    """Creates fake orders"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    customer_id = factory.Sequence(lambda n: n)
    created_at = factory.LazyFunction(datetime.now)


class OrderItemFactory(factory.Factory):
    """Creates fake order item"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = OrderItem

    name = factory.Faker("first_name")
    order_id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Faker("pyint", min_value=1, max_value=10)
