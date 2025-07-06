"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order, OrderItem

STATUS_CHOICES = ["placed", "shipped", "returned", "canceled"]


class OrderFactory(factory.Factory):
    """Creates fake orders"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    customer_id = factory.Sequence(lambda n: n)
    status = factory.Faker("random_element", elements=STATUS_CHOICES)


class OrderItemFactory(factory.Factory):
    """Creates fake order item"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = OrderItem

    # Create a new Order by default to satisfy foreign key constraint
    order_id = factory.LazyFunction(lambda: OrderFactory.create().id)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Faker("pyint", min_value=1, max_value=10)
