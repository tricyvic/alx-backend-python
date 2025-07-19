import asyncio
import os
import time

async def fun(x):
        print(f"Function {x} started")
        await asyncio.sleep(x)
        print(f"Function {x} completed")
        time.sleep(x)
        print("All functions started")
        await asyncio.sleep(x)
        print("All functions completed")
        await asyncio.sleep(x)
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:  # For Unix/Linux/macOS
            os.system('clear')
        print("Done")


asyncio.run(fun(2))