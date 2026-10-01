from copy import deepcopy
from decimal import Decimal
from uuid import UUID

import pytest

from orderflow import (
    InvalidOperationError,
    Order,
    OrderApplication,
    OrderItem,
    OrderStatus,
    ShipmentStatus,
)
from .test_order_workflows import processing_order


def test_confirmed_items_cannot_be_mutated_through_returned_collection(app):
    customer = app.create_customer("Customer")
    order = app.create_draft_order(customer.id)
    app.add_item(order.id, "P", 1, Decimal("2"))
    app.confirm_order(order.id)
    items = app.get_order(order.id).items

    with pytest.raises(AttributeError):
        items.clear()
    with pytest.raises(AttributeError):
        items.append(OrderItem("Q", 1, Decimal("1")))
    with pytest.raises(TypeError):
        items[0] = OrderItem("Q", 1, Decimal("1"))
    with pytest.raises(AttributeError):
        order.items = []

    persisted = app.get_order(order.id)
    assert persisted.status is OrderStatus.CONFIRMED
    assert [item.product_code for item in persisted.items] == ["P"]


@pytest.mark.parametrize("field", ["id", "customer_id", "status"])
def test_order_public_identity_relationship_and_status_are_read_only(app, field):
    customer, order = processing_order(app)
    original_id = order.id
    value = OrderStatus.COMPLETED if field == "status" else UUID(int=999)

    with pytest.raises(AttributeError):
        setattr(order, field, value)

    persisted = app.get_order(original_id)
    assert persisted.id == original_id
    assert persisted.customer_id == customer.id
    assert persisted.status is OrderStatus.PROCESSING
    assert [entry.id for entry in app.list_customer_orders(customer.id)] == [original_id]


@pytest.mark.parametrize("field", ["id", "order_id", "status"])
def test_shipment_public_identity_relationship_and_status_are_read_only(
    app, repositories, field
):
    _, order = processing_order(app)
    shipment = app.create_shipment(order.id)
    original_id = shipment.id
    value = ShipmentStatus.DISPATCHED if field == "status" else UUID(int=999)

    with pytest.raises(AttributeError):
        setattr(shipment, field, value)

    persisted = repositories[2].get(original_id)
    assert persisted.id == original_id
    assert persisted.order_id == order.id
    assert persisted.status is ShipmentStatus.CREATED


@pytest.mark.parametrize("operation", ["mark_shipped", "complete"])
def test_shipment_free_order_has_no_independent_public_transition(app, operation):
    _, order = processing_order(app)

    with pytest.raises(AttributeError):
        getattr(order, operation)()
    with pytest.raises(InvalidOperationError, match="before shipment"):
        app.complete_order(order.id)

    assert app.get_order(order.id).status is OrderStatus.PROCESSING


def test_cancelled_orders_shipment_cannot_dispatch_independently(app, repositories):
    _, order = processing_order(app)
    shipment = app.create_shipment(order.id)
    app.cancel_order(order.id)

    with pytest.raises(AttributeError):
        shipment.dispatch()
    with pytest.raises(InvalidOperationError):
        app.dispatch_shipment(shipment.id)

    assert app.get_order(order.id).status is OrderStatus.CANCELLED
    assert repositories[2].get(shipment.id).status is ShipmentStatus.CREATED


def test_rejected_dispatch_validates_shipment_before_changing_order(app, repositories):
    _, order = processing_order(app)
    shipment = app.create_shipment(order.id)
    app.dispatch_shipment(shipment.id)

    # Simulate storage returning an older order alongside an already dispatched shipment.
    earlier_order = Order(order.id, order.customer_id)
    earlier_order.add_item(OrderItem("P", 1, Decimal("1")))
    earlier_order.confirm()
    earlier_order.begin_processing()
    repositories[1].save(earlier_order)

    with pytest.raises(InvalidOperationError, match="shipment with status dispatched"):
        app.dispatch_shipment(shipment.id)

    assert app.get_order(order.id).status is OrderStatus.PROCESSING
    assert repositories[2].get(shipment.id).status is ShipmentStatus.DISPATCHED


def test_repeated_dispatch_leaves_both_states_unchanged(app, repositories):
    _, order = processing_order(app)
    shipment = app.create_shipment(order.id)
    app.dispatch_shipment(shipment.id)

    with pytest.raises(InvalidOperationError):
        app.dispatch_shipment(shipment.id)

    assert app.get_order(order.id).status is OrderStatus.SHIPPED
    assert repositories[2].get(shipment.id).status is ShipmentStatus.DISPATCHED


class SnapshotRepository:
    """Test adapter: reads and writes cross a copy boundary, requiring explicit saves."""

    def __init__(self, repository):
        self.repository = repository

    def __getattr__(self, name):
        operation = getattr(self.repository, name)

        def call(*args):
            return deepcopy(operation(*deepcopy(args)))

        return call


@pytest.fixture
def snapshot_app(repositories):
    return OrderApplication(*(SnapshotRepository(repo) for repo in repositories))


def test_application_persists_lifecycle_with_detached_reads(snapshot_app, repositories):
    app = snapshot_app
    customer = app.create_customer("Customer")
    order = app.create_draft_order(customer.id)
    app.add_item(order.id, "P", 2, Decimal("3"))
    assert app.get_order(order.id).items == (OrderItem("P", 2, Decimal("3")),)
    app.remove_item(order.id, "P")
    assert not app.get_order(order.id).items
    app.add_item(order.id, "Q", 1, Decimal("4"))
    app.confirm_order(order.id)
    assert app.get_order(order.id).status is OrderStatus.CONFIRMED
    app.begin_processing(order.id)
    assert app.get_order(order.id).status is OrderStatus.PROCESSING
    shipment = app.create_shipment(order.id)
    app.dispatch_shipment(shipment.id)
    assert app.get_order(order.id).status is OrderStatus.SHIPPED
    assert repositories[2].get(shipment.id).status is ShipmentStatus.DISPATCHED
    app.complete_order(order.id)
    assert app.get_order(order.id).status is OrderStatus.COMPLETED
    assert app.list_customer_orders(customer.id)[0].status is OrderStatus.COMPLETED


@pytest.mark.parametrize("state", ["draft", "confirmed", "processing"])
def test_application_persists_cancellation_with_detached_reads(snapshot_app, state):
    app = snapshot_app
    customer = app.create_customer("Customer")
    order = app.create_draft_order(customer.id)
    app.add_item(order.id, "P", 1, Decimal("1"))
    if state != "draft":
        app.confirm_order(order.id)
    if state == "processing":
        app.begin_processing(order.id)

    app.cancel_order(order.id)

    assert app.get_order(order.id).status is OrderStatus.CANCELLED
