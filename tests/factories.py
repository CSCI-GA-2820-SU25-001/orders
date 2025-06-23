"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order

class OrderFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    customer_id = factory.Sequence(lambda n: n)