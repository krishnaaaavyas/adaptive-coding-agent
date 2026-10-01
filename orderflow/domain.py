"""Domain objects and lifecycle behavior for OrderFlow."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from uuid import UUID

from .errors import InvalidOperationError, NotFoundError, ValidationError


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShipmentStatus(str, Enum):
    CREATED = "created"
    DISPATCHED = "dispatched"


@dataclass(frozen=True)
class Customer:
    id: UUID
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("customer name must not be blank")


@dataclass(frozen=True)
class OrderItem:
    product_code: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if not self.product_code.strip():
            raise ValidationError("product code must not be blank")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValidationError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValidationError("quantity must be greater than zero")
        if not isinstance(self.unit_price, Decimal):
            raise ValidationError("unit price must be a Decimal")
        if not self.unit_price.is_finite() or self.unit_price < Decimal("0"):
            raise ValidationError("unit price must be a finite non-negative amount")


class Order:
    def __init__(self, id: UUID, customer_id: UUID) -> None:
        self._id = id
        self._customer_id = customer_id
        self._status = OrderStatus.DRAFT
        self._items: list[OrderItem] = []

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def customer_id(self) -> UUID:
        return self._customer_id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    def add_item(self, item: OrderItem) -> None:
        self._require_status(OrderStatus.DRAFT, "add items")
        if any(existing.product_code == item.product_code for existing in self.items):
            raise InvalidOperationError(
                f"product {item.product_code!r} is already in the order"
            )
        self._items.append(item)

    def remove_item(self, product_code: str) -> OrderItem:
        self._require_status(OrderStatus.DRAFT, "remove items")
        for index, item in enumerate(self.items):
            if item.product_code == product_code:
                return self._items.pop(index)
        raise NotFoundError(f"product {product_code!r} is not in the order")

    def confirm(self) -> None:
        self._require_status(OrderStatus.DRAFT, "confirm")
        if not self.items:
            raise InvalidOperationError("an empty order cannot be confirmed")
        self._status = OrderStatus.CONFIRMED

    def begin_processing(self) -> None:
        self._require_status(OrderStatus.CONFIRMED, "begin processing")
        self._status = OrderStatus.PROCESSING

    def cancel(self) -> None:
        allowed = {OrderStatus.DRAFT, OrderStatus.CONFIRMED, OrderStatus.PROCESSING}
        if self.status not in allowed:
            raise InvalidOperationError(
                f"cannot cancel an order with status {self.status.value}"
            )
        self._status = OrderStatus.CANCELLED

    # Cross-entity transitions are internal to OrderApplication's coordinated use cases.
    def _mark_shipped(self) -> None:
        self._require_status(OrderStatus.PROCESSING, "mark shipped")
        self._status = OrderStatus.SHIPPED

    def _complete(self) -> None:
        self._require_status(OrderStatus.SHIPPED, "complete")
        self._status = OrderStatus.COMPLETED

    def _require_status(self, expected: OrderStatus, operation: str) -> None:
        if self.status is not expected:
            raise InvalidOperationError(
                f"cannot {operation} an order with status {self.status.value}"
            )


class Shipment:
    def __init__(self, id: UUID, order_id: UUID) -> None:
        self._id = id
        self._order_id = order_id
        self._status = ShipmentStatus.CREATED

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def status(self) -> ShipmentStatus:
        return self._status

    def _dispatch(self) -> None:
        if self.status is not ShipmentStatus.CREATED:
            raise InvalidOperationError(
                f"cannot dispatch a shipment with status {self.status.value}"
            )
        self._status = ShipmentStatus.DISPATCHED
