import motor.motor_asyncio
import asyncio

async def test():
    uri = "mongodb+srv://campus_agent:mTV4uc0Giu7VcEcy@campuscluster.lfgfvhe.mongodb.net/?retryWrites=true&w=majority&appName=CampusCluster"
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client["campus_admin"]
    print(await db.command("ping"))

asyncio.run(test())
