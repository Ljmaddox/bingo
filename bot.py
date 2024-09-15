import discord
import json
import asyncio
import os

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Make sure your bot can read message content
intents.members = True  # To fetch members of the guild

# Create an instance of a client with intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Start a background task to check for new messages
    client.loop.create_task(check_for_messages())

async def check_for_messages():
    while True:
        try:
            if os.path.exists('message_to_send.json'):
                with open('message_to_send.json', 'r') as f:
                    data = json.load(f)
                    message = data.get('message')
                    player_name = data.get('name')

                    # Ensure both message and player_name are present
                    if not player_name or not message:
                        print(f"Invalid data in message_to_send.json: {data}")
                        os.remove('message_to_send.json')  # Remove invalid file to stop the loop
                        continue

                    # Find the first text channel the bot has permission to send messages to
                    channel = find_channel_with_permissions()
                    if channel:
                        player_id = await get_member_id(channel.guild, player_name)
                        if player_id:
                            # Format mention properly
                            mention = f'<@{player_id}>'
                            await send_message(channel, f'{mention} {message}')
                        else:
                            print(f"Player '{player_name}' not found in the server.")
                        
                # Remove the file only after successful processing
                os.remove('message_to_send.json')
        except Exception as e:
            print(f'Error: {e}')
            # Consider removing or renaming the file here if processing fails
            if os.path.exists('message_to_send.json'):
                os.remove('message_to_send.json')
        await asyncio.sleep(3)  # Check every 3 seconds

def find_channel_with_permissions():
    for guild in client.guilds:
        for channel in guild.text_channels:
            # Check if the bot has permission to send messages in this channel
            permissions = channel.permissions_for(guild.me)
            if permissions.send_messages:
                return channel
    return None

async def get_member_id(guild, player_name):
    # Get all members in the guild (server)
    for member in guild.members:
        # Check if player_name is valid and compare with the member's username or nickname
        if player_name and (player_name.lower() == member.name.lower() or player_name.lower() == member.display_name.lower()):
            return member.id
    return None

async def send_message(channel, message):
    if channel:
        try:
            await channel.send(message)
            print(f"Message sent to {channel.name}: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")

# Hardcode your bot token here
token = os.environ.get('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN environment variable not set.")
client.run(token)
