"""
Seed data for the mock enterprise API.

This module provides reproducible seed data separate from production logic.
Run: python -m app.seed
"""

from app.main import CUSTOMERS, ORDERS, PAYMENTS


def seed():
    print("Mock Enterprise API seed data:")
    print(f"  Customers: {len(CUSTOMERS)}")
    for c in CUSTOMERS.values():
        print(f"    {c.id}: {c.name} ({c.tier})")
    print(f"  Orders: {len(ORDERS)}")
    for o in ORDERS.values():
        print(f"    {o.id}: ${o.total} ({o.status})")
    print(f"  Payments: {len(PAYMENTS)}")
    for p in PAYMENTS.values():
        print(f"    {p.id}: ${p.amount} ({p.status})")
    print("Seed data loaded in-memory.")


if __name__ == "__main__":
    seed()
