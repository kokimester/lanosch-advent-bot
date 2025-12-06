import discord
import asyncio
import os
from dotenv import load_dotenv
import json
import dateutil.parser
import datetime

# Load .env file
load_dotenv()

# Get token from environment
TOKEN = os.getenv("TOKEN")
# Constants (keep these IDs updated to your setup)
ADVENT_ROLE_ID = os.getenv("ADVENT_ROLE_ID")
ADVENT_CHANNEL_ID = os.getenv("ADVENT_CHANNEL_ID")
# debug channel on my own server
DEBUG_CHANNEL_ID = os.getenv("DEBUG_CHANNEL_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

advent_info: dict = None
advent_json_file: str = 'input-advent.json'
task_last_run = None

# method for serializing datetime


def datetime_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

# custom Decoder for datetime


def DecodeDateTime(empDict):
    if 'date' in empDict:
        empDict["date"] = dateutil.parser.parse(empDict["date"])
    return empDict


with open(advent_json_file) as f:
    # use of object_hook
    advent_info = json.load(f, object_hook=DecodeDateTime)
    # print(advent_info)


async def log_to_debug_server(message: str = ""):
    for guild in client.guilds:
        debug_channel = guild.get_channel(DEBUG_CHANNEL_ID)
        if not debug_channel:
            # print(f"⚠️ Debug channel not found on server {guild}.")
            continue
        await debug_channel.send(f"Bot posted today's message. {message}")


async def step():
    global task_last_run
    task_last_run = datetime.datetime.now()

    for guild in client.guilds:
        advent_channel = guild.get_channel(ADVENT_CHANNEL_ID)
        # print(f"{guild}")
        # for emoji in guild.emojis:
        # print(f"<:{emoji.name}:{emoji.id}>")
        if not advent_channel:
            # print(f"⚠️ Advent channel not found on server {guild}.")
            continue

        messages = []

        for day in advent_info:
            now = datetime.datetime.now()
            post_date = day["date"]
            if post_date < now and day["is_posted"] is False:
                day["is_posted"] = True
                print(f"Post date: {day['date']}, posting at {now}")
                messages.append(day["intro"])
                for game in day["keys"]:
                    # print(game)
                    emoji = game["emoji"]
                    name = game["name"]
                    vendor = game["vendor"]
                    link = game["link"]
                    # Handle vendor link
                    vendor_text = f"[{vendor}]({link})" if link else vendor
                    key = game["key"]
                    person = game["person"]
                    contact = key
                    if key == "":
                        member = discord.utils.find(lambda m: m.name == person, guild.members)
                        contact = "A játékért keresd Kokit!"
                        if member:
                            f"A játékért keresd őt: {member.mention}"
                    game_msg = f"{emoji} **{name}** ({vendor_text}) - {contact}"
                    messages.append(game_msg)

        if messages:
            await advent_channel.send(f"🎄 **Mai <@&{ADVENT_ROLE_ID}> üzenet: 🎄**\n" + "\n".join(messages))
            await log_to_debug_server("Lanosch")

        # print(messages)
    with open(advent_json_file, 'w') as f:
        json.dump(advent_info, f, default=datetime_serializer)
        # print("Updating advent database")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower().strip()

    if content in ["/online", "!online", ".online"]:
        msg = "✅ Bot is online."

        if task_last_run:
            delta = datetime.datetime.now() - task_last_run
            msg += f"\n🕒 Background task last ran {delta.total_seconds():.1f}s ago."
        else:
            msg += "\n⚠️ Background task has not run yet."

        await message.channel.send(msg)

# ----------------------------
#   RUN TASK EVERY 10 SECONDS
# ----------------------------


async def background_task():
    await client.wait_until_ready()
    while not client.is_closed():
        await step()
        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    asyncio.create_task(background_task())

client.run(TOKEN)
