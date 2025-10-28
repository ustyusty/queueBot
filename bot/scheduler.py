import asyncio
import datetime
from .db import db

async def cleanup_scheduler():
    while True:
        now = datetime.datetime.now()

        if (now.weekday() in (1, 4) and now.hour >= 16):
            await db.cleanup_job()
            print(f"✅ Очистка завершена!")
            await asyncio.sleep(86400)
        else:
            await asyncio.sleep(3600)