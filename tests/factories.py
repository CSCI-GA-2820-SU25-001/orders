"""
Test Factory to make fake objects for testing
"""
from datetime import datetime, UTC
import factory
from service.models import Order, OrderItem
from datetime import datetime, UTC


STATUS_CHOICES = ["placed", "shipped", "returned", "canceled"]


class OrderFactory(factory.Factory):
    """Creates fake orders"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    customer_id = factory.Sequence(lambda n: n)
    status = factory.Faker("random_element", elements=STATUS_CHOICES)
    created_at  = factory.LazyFunction(lambda: datetime.now(UTC))

    @factory.lazy_attribute
    def shipped_at(self):
        """Auto fill shipped_at only if the status is 'shipped' """
        return datetime.now(UTC) if self.status == 'shipped' else None



class OrderItemFactory(factory.Factory):
    """Creates fake order item"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = OrderItem

    order_id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Faker("pyint", min_value=1, max_value=10)
