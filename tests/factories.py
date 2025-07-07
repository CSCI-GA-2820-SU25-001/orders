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

    # Use SubFactory to create related Order object
    order = factory.SubFactory(OrderFactory)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Faker("pyint", min_value=1, max_value=10)

    @factory.post_generation
    def set_order_id(obj, create, extracted, **kwargs):
        """Set the order_id after the order is created"""
        if obj.order:
            obj.order_id = obj.order.id
