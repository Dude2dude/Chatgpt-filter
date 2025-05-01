# bot.py
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pymongo import MongoClient
import time

bot = Client("AutoFilterBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = MongoClient(MONGO_URI)["filterbot"]["files"]

# Force subscribe
@bot.on_message(filters.private & filters.incoming)
async def check_subscribe(client, message: Message):
    try:
        user = await client.get_chat_member(FORCE_SUB_CHANNEL, message.from_user.id)
    except:
        await message.reply(f"Please join @{FORCE_SUB_CHANNEL[1:]} to use this bot.")
        return

    await bot.process(message)

# Save files from channel
@bot.on_message(filters.channel & filters.document)
async def save_file(client, message):
    db.insert_one({
        "file_id": message.document.file_id,
        "file_name": message.document.file_name.lower()
    })

# Handle user search
@bot.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def search_file(client, message: Message):
    query = message.text.lower()
    result = db.find_one({"file_name": {"$regex": query}})
    
    if result:
        sent = await message.reply_document(result["file_id"])
        await asyncio.sleep(600)  # wait 10 minutes
        await sent.delete()
    else:
        await message.reply("No file found with that name.")

# Start command
@bot.on_message(filters.command("start") & filters.private)
async def start_msg(client, message):
    await message.reply("Hi! Send the movie name to search. Make sure you’ve joined our channel!")

bot.run()
