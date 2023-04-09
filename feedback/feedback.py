import discord
import json
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


with open('feedback_terms.txt', 'r') as file:
    required_words = [line.strip() for line in file]

min_characters = 280

def load_karma_data():
    with open('karma.json', 'r') as f:
        return json.load(f)

def save_karma_data(data):
    with open('karma.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing feedback!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Channel name: {message.channel.name}")  # Name of the Thread 
    print(f"Channel type: {message.channel.type}")  # Type of Channel

    if message.channel.type == discord.ChannelType.public_thread:
        print("Processing message in forum channel")  # If a thread in the feedback channel

        thread_id = str(message.channel.id)
        user_id = str(message.author.id)
        data = load_karma_data()

        if thread_id not in data['threads']:
            print("Thread not in data. Creating new thread entry.")
            data['threads'][thread_id] = []

        if user_id not in data['threads'][thread_id]:
            print("User has not earned karma in this thread")  # Debug print

            async for msg in message.channel.history(oldest_first=True): # Get the initial message in the thread
                parent_message = msg
                break

            if message.author == parent_message.author:
                print("Message author is the initial poster")
                return


            if len(message.content) >= min_characters:
                print("Message length requirement met")  # Debug print
            else:
                print("Message length requirement not met")
                return

            if any(word in message.content.lower() for word in required_words):
                print("Message contains required words")  # Debug print
            else:
                print("Message does not contain required words")
                return

            data['threads'][thread_id].append(user_id)

            if user_id in data['users']:
                data['users'][user_id] += 1
            else:
                data['users'][user_id] = 1

            save_karma_data(data)
            await message.add_reaction('✅')
            await message.channel.send(f"{message.author.mention} has earned 1 feedback karma point!")

    await bot.process_commands(message)


bot.run(token)