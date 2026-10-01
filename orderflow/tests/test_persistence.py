from copy import deepcopy
from decimal import Decimal
from uuid import UUID

import pytest

from orderflow import Customer, Order, OrderItem, OrderStatus, Shipment, ShipmentStatus
from orderflow.in_memory import (
    InMemoryCustomerRepository,
    InMemoryOrderRepository,
    InMemoryShipmentRepository,
)


def test_customer_repository_retains_customer():
    repository = InMemoryCustomerRepository()
    customer = Customer(UUID(int=1), "Customer")

    repository.add(customer)

    assert repository.get(customer.id) is customer


def test_order_repository_retains_and_filters_orders():
    repository = InMemoryOrderRepository()
    first = Order(UUID(int=1), UUID(int=10))
    second = Order(UUID(int=2), UUID(int=20))
    repository.add(first)
    repository.add(second)

    assert repository.get(first.id) is first
    assert repository.list_for_customer(UUID(int=10)) == [first]
    assert repository.list_for_customer(UUID(int=99)) == []


def test_shipment_repository_retains_one_shipment_per_order():
    repository = InMemoryShipmentRepository()
    shipment = Shipment(UUID(int=1), UUID(int=10))
    repository.add(shipment)

    assert repository.get(shipment.id) is shipment
    assert repository.get_for_order(shipment.order_id) is shipment

    with pytest.raises(ValueError, match="already has a shipment"):
        repository.add(Shipment(UUID(int=2), shipment.order_id))


def test_order_save_replaces_existing_entity_and_preserves_customer():
    repository = InMemoryOrderRepository()
    original = Order(UUID(int=1), UUID(int=10))
    repository.add(original)
    replacement = Order(original.id, original.customer_id)
    replacement.add_item(OrderItem("P", 1, Decimal("2")))
    replacement.confirm()

    repository.save(replacement)

    persisted = repository.get(original.id)
    assert persisted.status is OrderStatus.CONFIRMED
    assert persisted.items == replacement.items
    assert persisted.customer_id == original.customer_id
    assert repository.list_for_customer(original.customer_id) == [persisted]


@pytest.mark.parametrize(
    "repository, entity",
    [
        (InMemoryOrderRepository(), Order(UUID(int=1), UUID(int=10))),
        (InMemoryShipmentRepository(), Shipment(UUID(int=1), UUID(int=10))),
    ],
)
def test_save_rejects_missing_id(repository, entity):
    with pytest.raises(ValueError, match="does not exist"):
        repository.save(entity)
    assert repository.get(entity.id) is None


def test_order_save_rejects_customer_reassignment():
    repository = InMemoryOrderRepository()
    original = Order(UUID(int=1), UUID(int=10))
    repository.add(original)

    with pytest.raises(ValueError, match="customer cannot be changed"):
        repository.save(Order(original.id, UUID(int=20)))

    assert repository.get(original.id).customer_id == original.customer_id
    assert repository.list_for_customer(UUID(int=20)) == []


def test_shipment_save_rejects_duplicate_order_without_changing_either_shipment():
    repository = InMemoryShipmentRepository()
    first = Shipment(UUID(int=1), UUID(int=10))
    second = Shipment(UUID(int=2), UUID(int=20))
    repository.add(first)
    repository.add(second)

    with pytest.raises(ValueError, match="already has a shipment"):
        repository.save(Shipment(second.id, first.order_id))

    assert repository.get(first.id).order_id == first.order_id
    assert repository.get(second.id).order_id == second.order_id
    assert repository.get_for_order(first.order_id).id == first.id
    assert repository.get_for_order(second.order_id).id == second.id


def test_shipment_save_rejects_reassignment_to_unoccupied_order():
    repository = InMemoryShipmentRepository()
    original = Shipment(UUID(int=1), UUID(int=10))
    repository.add(original)

    with pytest.raises(ValueError, match="order cannot be changed"):
        repository.save(Shipment(original.id, UUID(int=20)))

    assert repository.get(original.id).order_id == original.order_id
    assert repository.get_for_order(UUID(int=20)) is None


def test_shipment_save_accepts_replacement_with_same_identity_and_owner(app):
    customer = app.create_customer("Customer")
    order = app.create_draft_order(customer.id)
    app.add_item(order.id, "P", 1, Decimal("1"))
    app.confirm_order(order.id)
    app.begin_processing(order.id)
    shipment = app.create_shipment(order.id)
    repository = InMemoryShipmentRepository()
    repository.add(deepcopy(shipment))
    app.dispatch_shipment(shipment.id)

    repository.save(deepcopy(shipment))

    persisted = repository.get(shipment.id)
    assert persisted.status is ShipmentStatus.DISPATCHED
    assert persisted.order_id == order.id
    assert repository.get_for_order(order.id).id == shipment.id
