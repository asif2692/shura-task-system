"""Test DB connection. Run: python test_db.py"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *  # noqa

async def main():
    print("DATABASE_URL:", settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Database connected and tables created.")
    await engine.dispose()

asyncio.run(main())
