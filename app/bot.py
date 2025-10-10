import datetime
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

import database


# INIT
reminder_weeks_tuple = (28, 30, 34, 35, 41, 44)  # weeks when to be notified

# --- Setup log folder ---
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)  # create folder if it doesn't exist
log_file = log_dir / "data.log"

# --- Configure logging ---
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Rotating file handler: max 5 MB per file, keep 3 backups
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5_000_000,
    backupCount=3,
    encoding='utf-8'
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     filename='data.log',
#     encoding='utf-8',
#     level=logging.DEBUG,
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S %Z'
# )

env_path = Path(__file__).resolve().parent.parent / "stack.env"
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found in environment variables!")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def is_important_week(week):
    if int(week) in reminder_weeks_tuple:
        return True
    return False


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# returns True if message is private (DM)
def is_private_message(interaction) -> bool:
    if interaction.channel.type is discord.ChannelType.private:
        return True
    else:
        return False


@tasks.loop(seconds=10)
# runs every x seconds
async def course_reminder_task():
    current_date = datetime.datetime.now().date()
    current_week = current_date.isocalendar().week
    guilds: list[dict] = database.get_all_guilds()

    if not is_important_week(current_week):
        return

    for guild in guilds:
        channel_id = guild.get("channel_id")
        last_sent_week = int(str(guild.get("last_reminder_sent")))
        guild_id = guild["guild_id"]

        if channel_id:
            try:
                channel = await client.fetch_channel(int(channel_id))
            except discord.NotFound:
                logger.warning(
                    f"Channel {channel_id} not found. It might have been deleted.")
                continue
            except discord.Forbidden:
                logger.warning(
                    f"Cannot access channel {channel_id}. Missing permissions?")
                continue
            except Exception as e:
                logger.error(f"Failed to fetch channel {channel_id}: {e}")
                continue

            if channel:
                if int(current_week) != int(last_sent_week):
                    await channel.send("Nu kan du registrera dig på kurser/tentor!")
                    logger.info(
                        f"Reminder sent to server {guild_id} in channel {channel_id}")
                    database.set_last_reminder_sent(
                        guild_id, str(current_week))
            else:
                logger.info(f"Channel: {channel_id} not found. Removed?")
        else:
            logger.info("Channel not set")


def run_bot():
    # bot starting up
    @client.event
    async def on_ready():
        await tree.sync()  # syncs the "/" commands
        course_reminder_task.start()
        startup_message = f'{client.user} is now running!'
        logger.info(startup_message)
        print(startup_message)

    @client.event
    async def on_message(message):

        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # await send_message(message, user_message, is_private=False)

    # sets channel to receive reminders in
    @tree.command(name="set_channel", description="Ställer in vilken kanal som ska ta emot påminnelser")
    async def command(interaction: discord.Interaction, channel: discord.TextChannel):
        if is_private_message(interaction):
            await interaction.response.send_message("Command not allowed in DM.")
        else:
            guild_id = interaction.guild.id
            channel_id = channel.id
            logger.info(f"guild_id {guild_id}, channel_id, {channel_id}")
            database.set_target_channel(guild_id, channel_id)
            await interaction.response.send_message(f"Påminnelser kommer nu att skickas till kanal <#{channel_id}>")

    client.run(TOKEN)
