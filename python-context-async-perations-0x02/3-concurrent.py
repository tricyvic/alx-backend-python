import asyncio
import aiosqlite

#  async_fetch_users() and async_fetch_older_users()
async def async_fetch_users(db, query):
    async with db.execute(query) as cursor:
        return await cursor.fetchall()

async def async_fetch_older_users(db, age):
    query = "SELECT * FROM users WHERE age > ?"
    async with db.execute(query, (age,)) as cursor:
        return await cursor.fetchall()

async def main():
    coroutine_objects = [
        async_fetch_users(aiosqlite.connect("users.db"),"SELECT * FROM users"),
        async_fetch_older_users(aiosqlite.connect("users.db"),40),
    ]

    results = await asyncio.gather(*coroutine_objects)
    print("All data fetched:")
    print(results)
        


if __name__ == "__main__":
    asyncio.run(main())