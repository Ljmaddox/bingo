import discord
import json
import asyncio
import os
import redis

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Make sure your bot can read message content
intents.members = True  # To fetch members of the guild

# Create an instance of a client with intents
client = discord.Client(intents=intents)

# Connect to Redis (example configuration)
redis_client = redis.StrictRedis(host='your-redis-host', port=6379, db=0)

async def check_for_messages():
    while True:
        try:
            # Retrieve the message from Redis
            message_data = redis_client.get('message_to_send')
            if message_data:
                message_data = json.loads(message_data)
                player_name = message_data.get('name')
                message = message_data.get('message')

                if not player_name or not message:
                    print(f"Invalid data in Redis: {message_data}")
                    redis_client.delete('message_to_send')
                    continue

                channel = find_channel_with_permissions()
                if channel:
                    player_id = await get_member_id(channel.guild, player_name)
                    if player_id:
                        mention = f'<@{player_id}>'
                        await send_message(channel, f'{mention} {message}')
                    else:
                        print(f"Player '{player_name}' not found in the server.")
                    
                redis_client.delete('message_to_send')
        except Exception as e:
            print(f'Error: {e}')
            redis_client.delete('message_to_send')
        await asyncio.sleep(3)

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
        await channel.send(message)

# Hardcode your bot token here
token = os.environ.get('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN environment variable not set.")
client.run(token)
