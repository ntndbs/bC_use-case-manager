"""Seed script to populate database with initial data."""

import asyncio
import json
from pathlib import Path

import bcrypt

from db.database import async_session_maker, init_db
from db.models import Industry, Company, User, Role

SEED_DIR = Path(__file__).parent / "data" / "seed"


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def seed_industries(session):
    """Seed industries."""
    with open(SEED_DIR / "industries.json", encoding="utf-8") as f:
        industries = json.load(f)
    
    for data in industries:
        industry = Industry(**data)
        session.add(industry)
    
    await session.commit()
    print(f"✅ Seeded {len(industries)} industries")


async def seed_companies(session):
    """Seed companies."""
    with open(SEED_DIR / "companies.json", encoding="utf-8") as f:
        companies = json.load(f)
    
    for data in companies:
        company = Company(**data)
        session.add(company)
    
    await session.commit()
    print(f"✅ Seeded {len(companies)} companies")


async def seed_users(session):
    """Seed users with hashed passwords."""
    with open(SEED_DIR / "users.json", encoding="utf-8") as f:
        users = json.load(f)
    
    for data in users:
        user = User(
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=Role(data["role"]),
        )
        session.add(user)
    
    await session.commit()
    print(f"✅ Seeded {len(users)} users")


async def main():
    """Run all seed functions."""
    print("🌱 Starting database seed...")
    
    # Initialize database (create tables)
    await init_db()
    print("✅ Database tables created")
    
    async with async_session_maker() as session:
        await seed_industries(session)
        await seed_companies(session)
        await seed_users(session)
    
    print("🎉 Seed completed!")


if __name__ == "__main__":
    asyncio.run(main())