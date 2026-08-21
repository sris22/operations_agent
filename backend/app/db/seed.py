"""
Seed development data.

Run: python -m app.db.seed

This script creates:
- Development admin and operator users
- Sample knowledge documents
- Evaluation test cases

All data is for development only and must not be used in production.
"""

import asyncio
import sys

from sqlalchemy import select

from app.db.database import async_session, engine, Base
from app.db.models.user import User, UserRole
from app.core.security import hash_password


DEV_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "role": UserRole.ADMIN,
    },
    {
        "email": "operator@example.com",
        "password": "operator123",
        "role": UserRole.OPERATOR,
    },
]

SAMPLE_DOCUMENTS = [
    {
        "filename": "refund_policy.md",
        "content": """# Refund Policy

## Overview
Our company offers refunds for products and services under the following conditions.

## Eligibility
- Refund requests must be made within 30 days of purchase
- Products must be unused and in original packaging
- Digital products may be refunded within 14 days if not downloaded

## Process
1. Customer contacts support with order and payment details
2. Agent verifies purchase and eligibility
3. For amounts under $100, agent may process directly
4. For amounts over $100, supervisor approval is required
5. Refund is processed to original payment method within 5-7 business days

## Exceptions
- Custom orders are non-refundable
- Gift cards are non-refundable
- Shipping charges are non-refundable unless the error is on our part

## Contact
For refund inquiries, contact support@company.com or call 1-800-555-0199.
""",
        "metadata": {"category": "policy", "department": "support"},
    },
    {
        "filename": "troubleshooting_guide.md",
        "content": """# Common Issues and Troubleshooting

## Payment Issues
If a customer reports a payment was charged but the order was not completed:
1. Check payment status in the system
2. Verify order status
3. If payment is completed but order is pending, the order may need manual processing
4. If payment failed, inform the customer and suggest retrying

## Order Status
- PENDING: Order received, processing will begin shortly
- PROCESSING: Order is being prepared
- SHIPPED: Order has been shipped
- COMPLETED: Order delivered successfully
- CANCELLED: Order was cancelled

## Refund Processing
Always verify the payment amount before initiating a refund. Partial refunds are supported.

## Customer Tiers
- GOLD: Priority support, extended refund window (45 days)
- SILVER: Standard support, standard refund window (30 days)
- BRONZE: Basic support, standard refund window (30 days)
""",
        "metadata": {"category": "guide", "department": "support"},
    },
]


async def seed():
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Seed users
        for user_data in DEV_USERS:
            existing = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            if existing.scalar_one_or_none():
                print(f"  User {user_data['email']} already exists, skipping")
                continue

            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            session.add(user)
            print(f"  Created user: {user_data['email']} ({user_data['role'].value})")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
