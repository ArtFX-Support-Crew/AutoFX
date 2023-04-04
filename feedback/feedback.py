import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents = discord.Intents.all()



bot = commands.Bot(command_prefix='!', intents=intents)

required_words = ['drums', 'snare', 'low', 'high', 'mix', 'compression', 'womp', 'burrrrrrrrr', 'transient', 'reese']
min_characters = 280

#Functions to load and save karma data to json
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

    if message.channel.name == 'bot-dev-forum':
        if message.reference:
            initial_message = await message.channel.fetch_message(message.reference.message_id)
            if initial_message.author != bot.user and message.author != initial_message.author:  # Add the check here
                data = load_karma_data()
                thread_id = str(initial_message.id)
                user_id = str(message.author.id)

                if thread_id in data['threads']:
                    if user_id not in data['threads'][thread_id]:
                        data['threads'][thread_id].append(user_id)

                        if user_id in data['users']:
                            data['users'][user_id] += 1
                        else:
                            data['users'][user_id] = 1

                        save_karma_data(data)
                        await message.channel.send(f"{message.author.mention} has earned 1 feedback karma point!")
        else:
            if len(message.content) < min_characters:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, your feedback request must be at least {min_characters} characters long.")

            elif not any(word in message.content.lower() for word in required_words):
                await message.delete()
                await message.channel.send(f"{message.author.mention}, your feedback does not meet the municipal standard. Please provide meaningful feedback.")
    #Requirements met, make the feedback post
            else:
                print("Message meets requirements")  # Debug print
                data = load_karma_data()
                thread_id = str(message.id)
                data['threads'][thread_id] = []
                save_karma_data(data)

    await bot.process_commands(message)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot.run(BOT_TOKEN)