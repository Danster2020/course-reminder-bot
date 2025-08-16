import os
from pymongo import MongoClient
import logging
logging.getLogger('pymongo').setLevel(logging.WARNING)

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/courseReminderBotDB")
client = MongoClient(mongo_uri)

db = client.courseReminderBotDB
guilds = db.guilds
guilds_coll = db["guilds"]

# guilds.insert_one({"guild_id": "1065289293733568582"})
# guilds.drop()
# client.drop_database("courseReminderBotDB")

# for guild in guilds_coll:
#     print(guild)

for doc in guilds_coll.find():
    print(doc)


def get_or_create_guild(guild_id: str) -> dict:
    query = {"guild_id": str(guild_id)}
    guild = guilds_coll.find_one(query)

    if guild is None:
        # Create a default document if not found
        new_guild = {
            "guild_id": str(guild_id),
            "channel_id": None,
            "last_reminder_sent": 0
        }
        guilds_coll.insert_one(new_guild)
        return new_guild

    return guild


def get_all_guilds() -> list[dict]:
    return list(guilds_coll.find())


def set_target_channel(guild_id: str, channel_id: str):
    get_or_create_guild(guild_id)
    query = {"guild_id": str(guild_id)}
    update = {"$set": {"channel_id": str(channel_id)}}
    guilds_coll.update_one(query, update, upsert=True)


def set_last_reminder_sent(guild_id: str, date: str):
    query = {"guild_id": str(guild_id)}
    update = {"$set": {"last_reminder_sent": str(date)}}
    guilds_coll.update_one(query, update, upsert=True)
