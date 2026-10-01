"""In-memory persistence adapters for OrderFlow."""

from uuid import UUID

from .domain import Customer, Order, Shipment


class InMemoryCustomerRepository:
    def __init__(self) -> None:
        self._customers: dict[UUID, Customer] = {}

    def add(self, customer: Customer) -> None:
        if customer.id in self._customers:
            raise ValueError(f"customer {customer.id} already exists")
        self._customers[customer.id] = customer

    def get(self, customer_id: UUID) -> Customer | None:
        return self._customers.get(customer_id)


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}

    def add(self, order: Order) -> None:
        if order.id in self._orders:
            raise ValueError(f"order {order.id} already exists")
        self._orders[order.id] = order

    def save(self, order: Order) -> None:
        if order.id not in self._orders:
            raise ValueError(f"order {order.id} does not exist")
        if self._orders[order.id].customer_id != order.customer_id:
            raise ValueError("an order's customer cannot be changed")
        self._orders[order.id] = order

    def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)

    def list_for_customer(self, customer_id: UUID) -> list[Order]:
        return [
            order
            for order in self._orders.values()
            if order.customer_id == customer_id
        ]


class InMemoryShipmentRepository:
    def __init__(self) -> None:
        self._shipments: dict[UUID, Shipment] = {}

    def add(self, shipment: Shipment) -> None:
        if shipment.id in self._shipments:
            raise ValueError(f"shipment {shipment.id} already exists")
        if self.get_for_order(shipment.order_id) is not None:
            raise ValueError(f"order {shipment.order_id} already has a shipment")
        self._shipments[shipment.id] = shipment

    def save(self, shipment: Shipment) -> None:
        if shipment.id not in self._shipments:
            raise ValueError(f"shipment {shipment.id} does not exist")
        existing = self.get_for_order(shipment.order_id)
        if existing is not None and existing.id != shipment.id:
            raise ValueError(f"order {shipment.order_id} already has a shipment")
        if self._shipments[shipment.id].order_id != shipment.order_id:
            raise ValueError("a shipment's order cannot be changed")
        self._shipments[shipment.id] = shipment

    def get(self, shipment_id: UUID) -> Shipment | None:
        return self._shipments.get(shipment_id)

    def get_for_order(self, order_id: UUID) -> Shipment | None:
        return next(
            (
                shipment
                for shipment in self._shipments.values()
                if shipment.order_id == order_id
            ),
            None,
        )
