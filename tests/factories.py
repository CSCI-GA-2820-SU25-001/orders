"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import OrderItem


class OrderItemFactory(factory.Factory):
    """Creates fake order item"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = OrderItem    

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    order_id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantity   = factory.Faker("pyint", min_value=1, max_value=10)