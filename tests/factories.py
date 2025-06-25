"""
Test Factory to make fake objects for testing
"""

from datetime import datetime
import factory
from service.models import Order


class OrderFactory(factory.Factory):
    """Creates fake orders"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    created_at = factory.LazyFunction(datetime.now)
