# OrderFlow

OrderFlow is a local Python component for managing customers, orders, and the
shipment-backed order lifecycle. It has no external runtime dependencies and
uses in-memory persistence.

The application exposes use cases through `OrderApplication`. Domain objects
own their lifecycle rules, repository protocols separate the application from
storage, and the included adapters retain data for the lifetime of the Python
process.

Order and shipment identities, relationships, and statuses are read-only.
`Order.items` returns an immutable snapshot; use `add_item` and `remove_item`
while the order is DRAFT. New orders and shipments start in DRAFT and CREATED
respectively. Dispatch and completion must go through `OrderApplication`,
which coordinates the order and its shipment before changing either state.
Underscore-prefixed state and transition helpers are internal implementation
details. Repository saves replace an existing entity with the same identity
and owner; shipment saves also enforce one shipment per order.

## Run the tests

From the parent repository:

```text
python -m pytest orderflow/tests -q
```
