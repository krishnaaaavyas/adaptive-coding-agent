from uuid import UUID

import pytest

from orderflow import (
    InMemoryCustomerRepository,
    InMemoryOrderRepository,
    InMemoryShipmentRepository,
    OrderApplication,
)


class SequentialIds:
    def __init__(self) -> None:
        self._value = 0

    def __call__(self) -> UUID:
        self._value += 1
        return UUID(int=self._value)


@pytest.fixture
def repositories():
    return (
        InMemoryCustomerRepository(),
        InMemoryOrderRepository(),
        InMemoryShipmentRepository(),
    )


@pytest.fixture
def app(repositories):
    customers, orders, shipments = repositories
    return OrderApplication(customers, orders, shipments, SequentialIds())
