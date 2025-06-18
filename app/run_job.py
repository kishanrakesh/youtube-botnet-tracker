import asyncio
from app.api.channels import update_all_stored_channels

async def main():
    print("Starting channel update job...")
    await update_all_stored_channels()
    print("Channel update job complete.")

if __name__ == "__main__":
    asyncio.run(main())