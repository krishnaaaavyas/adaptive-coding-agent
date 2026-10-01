"""Application use cases for customer, order, and shipment workflows."""

from collections.abc import Callable
from decimal import Decimal
from uuid import UUID, uuid4

from .domain import Customer, Order, OrderItem, OrderStatus, Shipment, ShipmentStatus
from .errors import InvalidOperationError, NotFoundError
from .repositories import CustomerRepository, OrderRepository, ShipmentRepository


class OrderApplication:
    def __init__(
        self,
        customers: CustomerRepository,
        orders: OrderRepository,
        shipments: ShipmentRepository,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._customers = customers
        self._orders = orders
        self._shipments = shipments
        self._id_factory = id_factory

    def create_customer(self, name: str) -> Customer:
        customer = Customer(id=self._id_factory(), name=name)
        self._customers.add(customer)
        return customer

    def create_draft_order(self, customer_id: UUID) -> Order:
        self._require_customer(customer_id)
        order = Order(id=self._id_factory(), customer_id=customer_id)
        self._orders.add(order)
        return order

    def add_item(
        self,
        order_id: UUID,
        product_code: str,
        quantity: int,
        unit_price: Decimal,
    ) -> Order:
        order = self._require_order(order_id)
        order.add_item(OrderItem(product_code, quantity, unit_price))
        self._orders.save(order)
        return order

    def remove_item(self, order_id: UUID, product_code: str) -> OrderItem:
        order = self._require_order(order_id)
        removed = order.remove_item(product_code)
        self._orders.save(order)
        return removed

    def confirm_order(self, order_id: UUID) -> Order:
        order = self._require_order(order_id)
        order.confirm()
        self._orders.save(order)
        return order

    def begin_processing(self, order_id: UUID) -> Order:
        order = self._require_order(order_id)
        order.begin_processing()
        self._orders.save(order)
        return order

    def cancel_order(self, order_id: UUID) -> Order:
        order = self._require_order(order_id)
        order.cancel()
        self._orders.save(order)
        return order

    def create_shipment(self, order_id: UUID) -> Shipment:
        order = self._require_order(order_id)
        if order.status is not OrderStatus.PROCESSING:
            raise InvalidOperationError(
                f"cannot create a shipment for an order with status {order.status.value}"
            )
        if self._shipments.get_for_order(order_id) is not None:
            raise InvalidOperationError("an order may have only one shipment")
        shipment = Shipment(id=self._id_factory(), order_id=order_id)
        self._shipments.add(shipment)
        return shipment

    def dispatch_shipment(self, shipment_id: UUID) -> Shipment:
        shipment = self._require_shipment(shipment_id)
        order = self._require_order(shipment.order_id)
        if order.status is not OrderStatus.PROCESSING:
            raise InvalidOperationError(
                f"cannot mark shipped an order with status {order.status.value}"
            )
        if shipment.status is not ShipmentStatus.CREATED:
            raise InvalidOperationError(
                f"cannot dispatch a shipment with status {shipment.status.value}"
            )
        order._mark_shipped()
        shipment._dispatch()
        self._orders.save(order)
        self._shipments.save(shipment)
        return shipment

    def complete_order(self, order_id: UUID) -> Order:
        order = self._require_order(order_id)
        shipment = self._shipments.get_for_order(order_id)
        if shipment is None or shipment.status is not ShipmentStatus.DISPATCHED:
            raise InvalidOperationError("an order cannot be completed before shipment")
        order._complete()
        self._orders.save(order)
        return order

    def get_order(self, order_id: UUID) -> Order:
        return self._require_order(order_id)

    def list_customer_orders(self, customer_id: UUID) -> list[Order]:
        self._require_customer(customer_id)
        return self._orders.list_for_customer(customer_id)

    def _require_customer(self, customer_id: UUID) -> Customer:
        customer = self._customers.get(customer_id)
        if customer is None:
            raise NotFoundError(f"customer {customer_id} was not found")
        return customer

    def _require_order(self, order_id: UUID) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise NotFoundError(f"order {order_id} was not found")
        return order

    def _require_shipment(self, shipment_id: UUID) -> Shipment:
        shipment = self._shipments.get(shipment_id)
        if shipment is None:
            raise NotFoundError(f"shipment {shipment_id} was not found")
        return shipment
