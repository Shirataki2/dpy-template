# type: ignore
import asyncio
from src.core.bot import Bot

async def main() -> None:
    await Bot().run()

if __name__ == "__main__":
    asyncio.run(main())
