import asyncio
import aiosqlite

#  async_fetch_users() and async_fetch_older_users()
async def async_fetch_users():
    db = await aiosqlite.connect("users.db")
    async with db.execute("SELECT * FROM users") as cursor:
        return await cursor.fetchall()

async def async_fetch_older_users():
    db = await aiosqlite.connect("users.db")
    async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
        return await cursor.fetchall()

async def fetch_concurrently():
    coroutine_objects = [
        async_fetch_users(),
        async_fetch_older_users(),
    ]

    results = await asyncio.gather(*coroutine_objects)
    print("All data fetched:")
    print(results)
        


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())