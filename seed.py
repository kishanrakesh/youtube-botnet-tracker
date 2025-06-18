import httpx

API_URL = "http://localhost:8000/channel/add_channel"  # Change to deployed endpoint if needed

async def main():
    with open("./seed.txt", "r") as f:
        ids = [line.strip() for line in f if line.strip()]

    async with httpx.AsyncClient() as client:
        for identifier in ids:
            payload = {
                "channel_identifier": identifier,
                "source": "bulk_script",
                "notes": "batch import"
            }
            try:
                response = await client.post(API_URL, json=payload)
                print(f"{identifier}: {response.status_code} {response.json()}")
            except Exception as e:
                print(f"{identifier}: ERROR - {e}")

import asyncio
asyncio.run(main())