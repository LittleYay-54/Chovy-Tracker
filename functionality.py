# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)  # Command prefix is "/"

data = {'chovy_mentions': {}}


def load_data():
    """Loads the data from a JSON file 'data.json'. If it doesn't exist, then it is created"""
    global data
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # creates the file if it already doesn't exist
        # with open(file_name, 'w') does this
        with open('data.json', 'w') as file:
            json.dump(data, file)


def save_data():
    """Saves the data into the JSON file 'data.json'"""
    with open('data.json', 'w') as file:
        json.dump(data, file)


@bot.event
async def on_ready():
    load_data()
    try:
        synced = await bot.tree.sync()  # Sync all slash commands
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    # the bottom doesn't track its own messages
    if message.author == bot.user:
        return

    # for testing purposes
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # BIG T
    if message.content.startswith('sup sup'):
        await message.channel.send('WE IS ARE DO BE BACK IT hAYET HAGAIN!!')

    # checks if the message contains "chovy"
    if "chovy" in message.content.lower():
        # react to the message with '+' and '1' emojis
        await message.add_reaction('\u2795')  # plus emoji
        await asyncio.sleep(0.25)  # waits 0.25 to avoid emoji rate limit message
        await message.add_reaction('1\uFE0F\u20E3')  # 1 emoji

        # update the count for the user who said the word
        user_id = str(message.author.id)  # store as a string for JSON compatibility
        if user_id in data['chovy_mentions']:
            data['chovy_mentions'][user_id] += 1
        else:
            data['chovy_mentions'][user_id] = 1

        # save the updated data to the JSON file
        save_data()

    # lets the bot process any commands
    await bot.process_commands(message)


# slash command to display chovy count for the user who calls the command
@bot.tree.command(name="chovycountpersonal", description="Display how many times you've mentioned 'Chovy'")
async def chovycountpersonal(interaction: discord.Interaction):
    user_id = str(interaction.user.id)  # get user ID as a string

    # check if the user has a count and reply with their count
    if user_id in data['chovy_mentions']:
        count = data['chovy_mentions'][user_id]
        await interaction.response.send_message(f"You mentioned 'Chovy' {count} times!")
    else:
        await interaction.response.send_message("You haven't mentioned 'Chovy' yet!")


# slash command to display top 10 chovy counts for people in the server
@bot.tree.command(name="chovycountleaderboard", description="Displays who has mentioned 'Chovy' the most in this server")
async def chovycountleaderboard(interaction: discord.Interaction):
    # Sort the users by their chovy count, in descending order
    sorted_chovy_counts = sorted(data['chovy_mentions'].items(), key=lambda item: item[1], reverse=True)

    # Take the top 10 users
    top_10 = sorted_chovy_counts[:10]

    # Build the leaderboard message
    leaderboard_message = "**Top 10 'Chovy' Mentions Leaderboard**\n"
    for i, (user_id, count) in enumerate(top_10, start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch user object by ID
        leaderboard_message += f"{i}. {user.name}: {count} mentions\n"

    # Send the leaderboard as a response
    await interaction.response.send_message(leaderboard_message)