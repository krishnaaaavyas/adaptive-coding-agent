from decimal import Decimal
from uuid import UUID

import pytest

from orderflow import (
    InvalidOperationError,
    NotFoundError,
    OrderStatus,
    ShipmentStatus,
    ValidationError,
)


def order_with_item(app):
    customer = app.create_customer("Acme Supplies")
    order = app.create_draft_order(customer.id)
    app.add_item(order.id, "WIDGET", 2, Decimal("12.50"))
    return customer, order


def processing_order(app):
    customer, order = order_with_item(app)
    app.confirm_order(order.id)
    app.begin_processing(order.id)
    return customer, order


def test_create_customer_and_draft_order(app):
    customer = app.create_customer("Acme Supplies")
    order = app.create_draft_order(customer.id)

    assert customer.name == "Acme Supplies"
    assert order.customer_id == customer.id
    assert order.status is OrderStatus.DRAFT
    assert not order.items


def test_normal_order_lifecycle(app):
    _, order = processing_order(app)

    shipment = app.create_shipment(order.id)
    assert shipment.status is ShipmentStatus.CREATED

    app.dispatch_shipment(shipment.id)
    assert shipment.status is ShipmentStatus.DISPATCHED
    assert order.status is OrderStatus.SHIPPED

    completed = app.complete_order(order.id)
    assert completed.status is OrderStatus.COMPLETED


def test_add_and_remove_item_from_draft(app):
    customer = app.create_customer("Local Store")
    order = app.create_draft_order(customer.id)

    app.add_item(order.id, "PAPER", 3, Decimal("4.25"))
    removed = app.remove_item(order.id, "PAPER")

    assert removed.product_code == "PAPER"
    assert not order.items


@pytest.mark.parametrize(
    ("quantity", "price"),
    [(0, Decimal("1")), (-1, Decimal("1")), (1, Decimal("-0.01"))],
)
def test_invalid_item_values_are_rejected(app, quantity, price):
    customer = app.create_customer("Local Store")
    order = app.create_draft_order(customer.id)

    with pytest.raises(ValidationError):
        app.add_item(order.id, "PAPER", quantity, price)


def test_empty_order_cannot_be_confirmed(app):
    customer = app.create_customer("Empty Cart Customer")
    order = app.create_draft_order(customer.id)

    with pytest.raises(InvalidOperationError, match="empty order"):
        app.confirm_order(order.id)
    assert order.status is OrderStatus.DRAFT


@pytest.mark.parametrize("operation", ["add", "remove"])
def test_items_cannot_change_after_draft(app, operation):
    _, order = order_with_item(app)
    app.confirm_order(order.id)

    with pytest.raises(InvalidOperationError, match="status confirmed"):
        if operation == "add":
            app.add_item(order.id, "SECOND", 1, Decimal("2"))
        else:
            app.remove_item(order.id, "WIDGET")


def test_transitions_must_follow_lifecycle(app):
    _, order = order_with_item(app)

    with pytest.raises(InvalidOperationError, match="cannot begin processing"):
        app.begin_processing(order.id)
    with pytest.raises(AttributeError):
        order.mark_shipped()
    with pytest.raises(InvalidOperationError, match="cannot be completed"):
        app.complete_order(order.id)

    assert order.status is OrderStatus.DRAFT


@pytest.mark.parametrize(
    "prepare",
    [
        lambda app, order: None,
        lambda app, order: app.confirm_order(order.id),
        lambda app, order: (
            app.confirm_order(order.id),
            app.begin_processing(order.id),
        ),
    ],
)
def test_cancellation_is_allowed_before_shipping(app, prepare):
    _, order = order_with_item(app)
    prepare(app, order)

    app.cancel_order(order.id)

    assert order.status is OrderStatus.CANCELLED


@pytest.mark.parametrize("terminal_status", ["shipped", "completed", "cancelled"])
def test_cancellation_is_rejected_from_terminal_states(app, terminal_status):
    _, order = processing_order(app)
    if terminal_status in {"shipped", "completed"}:
        shipment = app.create_shipment(order.id)
        app.dispatch_shipment(shipment.id)
        if terminal_status == "completed":
            app.complete_order(order.id)
    else:
        app.cancel_order(order.id)

    with pytest.raises(InvalidOperationError, match="cannot cancel"):
        app.cancel_order(order.id)


def test_shipment_requires_processing_order(app):
    _, order = order_with_item(app)

    with pytest.raises(InvalidOperationError, match="cannot create a shipment"):
        app.create_shipment(order.id)


def test_only_one_shipment_may_exist_per_order(app):
    _, order = processing_order(app)
    app.create_shipment(order.id)

    with pytest.raises(InvalidOperationError, match="only one shipment"):
        app.create_shipment(order.id)


def test_order_cannot_complete_before_shipment(app):
    _, order = processing_order(app)

    with pytest.raises(InvalidOperationError, match="before shipment"):
        app.complete_order(order.id)


def test_retrieve_order_and_list_customer_orders(app):
    first_customer = app.create_customer("First Customer")
    second_customer = app.create_customer("Second Customer")
    first_order = app.create_draft_order(first_customer.id)
    second_order = app.create_draft_order(first_customer.id)
    app.create_draft_order(second_customer.id)

    assert app.get_order(first_order.id) is first_order
    assert app.list_customer_orders(first_customer.id) == [first_order, second_order]


def test_missing_entities_fail_explicitly(app):
    with pytest.raises(NotFoundError, match="customer"):
        app.create_draft_order(UUID(int=999))
    with pytest.raises(NotFoundError, match="order"):
        app.get_order(UUID(int=998))
