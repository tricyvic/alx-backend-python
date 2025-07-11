import asyncio

async def fetch_data(delay, item_id):
    print(f"Fetching data for item {item_id}...")
    await asyncio.sleep(delay)  # Simulate an I/O operation
    print(f"Finished fetching data for item {item_id}.")
    return f"Data for item {item_id}"

async def main():
    # Create a list of coroutine objects
    coroutine_objects = [
        fetch_data(2, 1),
        fetch_data(1, 2),
        fetch_data(3, 3)
    ]

    # Run them concurrently and gather results
    results = await asyncio.gather(*coroutine_objects)
    print("All data fetched:")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())