import discord
import json
from discord.ext import commands
from config import token
from terms import terms
import re
from karma import Karma 

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# This code is creating a list called `required_words` by iterating over a list called `terms` and
# appending each term in lowercase to the `required_words` list. This is likely being done to later
# check if a message contains any of the required words in order to earn a "feedback karma point".

required_words = []
for term in terms: 
    required_words.append(term.lower())

min_characters = 280
karma = Karma()
required_url_pattern = r'^(https?://)?(www\.)?(soundcloud|youtube|clyp\.it|drive|onedrive|dropbox|bandcamp|mixcloud)\.'


@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing feedback!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Channel name: {message.channel.name}")
    print(f"Channel type: {message.channel.type}")

    if message.channel.type == discord.ChannelType.public_thread:
        print("Processing message in forum channel")

        thread_id = str(message.channel.id)
        user_id = str(message.author.id)

        if thread_id not in karma.get_threads():
            karma.add_thread(thread_id)

        if not karma.user_in_thread(thread_id, user_id):
            async for msg in message.channel.history(oldest_first=True):
                parent_message = msg
                break

            if not re.search(required_url_pattern, parent_message.content, re.IGNORECASE):
                print("Initial post does not contain a valid URL")
                valid_attachments = [".wav", ".mp3", ".flac"]
                has_valid_attachment = any(att.filename.lower().endswith(tuple(valid_attachments)) for att in parent_message.attachments)
                if not has_valid_attachment:
                    print("Initial post does not contain a valid audio file attachment")
                    await parent_message.delete()
                    await message.channel.send(f"{parent_message.author.mention}, your post did not meet the requirements (URL or audio file attachment).")
                    return

            if message.author == parent_message.author:
                print("Message author is the initial poster - no reward")
                return

            if len(message.content) >= min_characters:
                print("Message length requirement met")
            else:
                print("Message length requirement not met")
                return

            if any(word in message.content.lower() for word in required_words):
                print("Message contains required words - karma will be awarded")
            else:
                print("Message does not contain required words - karma will not be awarded")
                return

            karma.add_user_to_thread(thread_id, user_id)
            if karma.user_exists(user_id):
                karma.increment_user_karma(user_id)
            else:
                karma.add_user(user_id)

            karma.save()
            await message.add_reaction('✅')
            await message.channel.send(f"{message.author.mention} has earned 1 feedback Karma!")

    await bot.process_commands(message)


bot.run(token)