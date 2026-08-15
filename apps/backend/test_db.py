import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def test():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT COUNT(*) FROM customers"))
        print(f"Total customers: {res.scalar()}")
        res = await conn.execute(text("SELECT id, tenant_id, first_name, last_name FROM customers LIMIT 5"))
        for row in res:
            print(row)

asyncio.run(test())
