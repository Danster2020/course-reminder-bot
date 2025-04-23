# import responses

import os
from dotenv import load_dotenv
import discord
from discord import app_commands

# INIT
load_dotenv()

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


def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    # bot starting up
    @client.event
    async def on_ready():
        await tree.sync()  # syncs the "/" commands
        print(f'{client.user} is now running!')

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


    client.run(os.environ['TOKEN'])