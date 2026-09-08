"""
Seed initial data for development.
Run after server has created tables:
    python seed_data.py
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.group import Group
from app.models.notification import NotificationPreference
from app.models.enums import UserRole


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(select(User).where(User.email == "admin@shura.local"))
        if result.scalar_one_or_none():
            print("Seed data already exists. Skipping.")
            return

        # Groups
        group1 = Group(name="Event Team", description="سالانہ اجتماع ٹیم")
        group2 = Group(name="General Helpers", description="عمومی معاونین")
        db.add_all([group1, group2])
        await db.flush()

        users = [
            User(
                email="admin@shura.local",
                hashed_password=hash_password("admin123"),
                full_name="System Admin",
                phone="+923001234567",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            ),
            User(
                email="shura@shura.local",
                hashed_password=hash_password("shura123"),
                full_name="رکن شوریٰ",
                phone="+923001111111",
                role=UserRole.SHURA_MEMBER,
                is_active=True,
                is_verified=True,
            ),
            User(
                email="assistant@shura.local",
                hashed_password=hash_password("assistant123"),
                full_name="اسسٹنٹ",
                phone="+923002222222",
                role=UserRole.ASSISTANT,
                is_active=True,
                is_verified=True,
            ),
            User(
                email="ahmed@shura.local",
                hashed_password=hash_password("helper123"),
                full_name="احمد",
                phone="+923003333331",
                role=UserRole.HELPER,
                group_id=group1.id,
                is_active=True,
                is_verified=True,
            ),
            User(
                email="ali@shura.local",
                hashed_password=hash_password("helper123"),
                full_name="علی",
                phone="+923003333332",
                role=UserRole.HELPER,
                group_id=group1.id,
                is_active=True,
                is_verified=True,
            ),
            User(
                email="hassan@shura.local",
                hashed_password=hash_password("helper123"),
                full_name="حسن",
                phone="+923003333333",
                role=UserRole.HELPER,
                group_id=group2.id,
                is_active=True,
                is_verified=True,
            ),
        ]
        db.add_all(users)
        await db.flush()

        for u in users:
            db.add(NotificationPreference(user_id=u.id))

        await db.commit()
        print("✅ Seed completed successfully!")
        print()
        print("Login credentials:")
        print("  Admin     → admin@shura.local / admin123")
        print("  Shura     → shura@shura.local / shura123")
        print("  Assistant → assistant@shura.local / assistant123")
        print("  Helpers   → ahmed@shura.local / helper123  (etc.)")


if __name__ == "__main__":
    asyncio.run(seed())
