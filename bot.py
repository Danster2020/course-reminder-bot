import datetime
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging

import database

# INIT
reminder_dates_list = ["2025-05-08"]
logger = logging.getLogger(__name__)
logging.basicConfig(filename='data.log', encoding='utf-8', level=logging.DEBUG)
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
async def course_reminder_task():
    current_date = str(datetime.datetime.now().date())
    guilds: list[dict] = database.get_all_guilds()
    
    for guild in guilds:
        channel_id = guild.get("channel_id")
        last_sent_date = str(guild.get("last_reminder_sent"))
        guild_id = guild["guild_id"]
    
        if channel_id:
            try:
                channel = await client.fetch_channel(int(channel_id))
            except discord.NotFound:
                logger.warning(f"Channel {channel_id} not found. It might have been deleted.")
                continue
            except discord.Forbidden:
                logger.warning(f"Cannot access channel {channel_id}. Missing permissions?")
                continue
            except Exception as e:
                logger.error(f"Failed to fetch channel {channel_id}: {e}")
                continue

            if channel:
                if current_date != last_sent_date:
                    await channel.send("Nu kan du registrera dig på kurser/tentor!")
                    logger.info(f"Reminder sent to server: {guild_id} in channel {channel_id}")
                    database.set_last_reminder_sent(guild_id, current_date)
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
        
    @tree.command(name="set_channel", description="Sets the channel for the bot to send reminders in.")
    async def command(interaction):
        if is_private_message(interaction):
            await interaction.response.send_message("Command not allowed in DM.")
        else:
            guild_id = interaction.guild.id
            channel_id = interaction.channel.id
            database.set_target_channel(guild_id, channel_id)
            print("guild_id:", guild_id, "channel_id", channel_id)
            await interaction.response.send_message("test response")
        
    client.run(os.environ['TOKEN'])