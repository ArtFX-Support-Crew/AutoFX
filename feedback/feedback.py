import discord
import json
from discord.ext import commands
from config import token
from terms import terms
import re

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

def load_karma_data():
    with open('karma.json', 'r') as f:
        return json.load(f)

def save_karma_data(data):
    with open('karma.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing feedback!')

required_url_pattern = r'^(https?://)?(www\.)?(soundcloud|youtube|clyp\.it|drive|onedrive|dropbox|bandcamp|mixcloud)\.'

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  


    print(f"Channel name: {message.channel.name}")  # Name of the Thread 
    print(f"Channel type: {message.channel.type}")  # Type of Channel

# This code block is checking if the message is being sent in a public thread channel. If it is, it
# retrieves the thread ID and user ID of the message sender, and loads the karma data from a JSON
# file.

    if message.channel.type == discord.ChannelType.public_thread:
        print("Processing message in forum channel")  # If a thread in the feedback channel

        thread_id = str(message.channel.id)
        user_id = str(message.author.id)
        data = load_karma_data()

# This code block is checking if the current thread ID is already in the `data` dictionary under the
# key `'threads'`. If it is not, it creates a new entry for the thread ID in the dictionary.

        if thread_id not in data['threads']:
            print("Thread not in data. Creating new thread entry.")
            data['threads'][thread_id] = []

        if user_id not in data['threads'][thread_id]:
            print("User has not earned karma in this thread")  # Debug print

            async for msg in message.channel.history(oldest_first=True): # Get the initial message in the thread
                parent_message = msg
                break
            


# This code block is checking if the initial post in a public thread channel contains a valid URL or
# audio file attachment. If it does not meet these requirements, the parent message is deleted and a
# message is sent to the author of the parent message indicating that their post did not meet the
# requirements. The `required_url_pattern` variable contains a regular expression pattern that matches
# valid URLs for certain websites, and the `valid_attachments` list contains file extensions for valid
# audio file attachments.
            
            if not re.search(required_url_pattern, parent_message.content, re.IGNORECASE):
                print("Initial post does not contain a valid URL")
                valid_attachments = [".wav", ".mp3", ".flac"]
                has_valid_attachment = any(att.filename.lower().endswith(tuple(valid_attachments)) for att in parent_message.attachments)
                if not has_valid_attachment:
                    print("Initial post does not contain a valid audio file attachment")
                    await parent_message.delete()
                    await message.channel.send(f"{parent_message.author.mention}, your post did not meet the requirements (URL or audio file attachment).")
                    return


           # This code block is checking if a message sent in a public thread channel meets certain
           # criteria in order to earn a "feedback karma point". The criteria include: 
           # - The message is not sent by the bot itself
           # - The message is sent in a public thread channel
           # - The initial post in the thread (the parent message) contains a valid URL or audio file
           # attachment
           # - The message is not sent by the same user who posted the initial message
           # - The message contains at least a certain number of characters (specified by the
           # `min_characters` variable)
           # - The message contains at least one of the required words (specified by the
           # `required_words` list)
           # If all of these criteria are met, the user who sent the message earns a feedback karma
           # point, which is recorded in a JSON file named "karma.json". The user's karma points are
           # also added to their total count in the JSON file. Finally, a checkmark reaction is added
      
      
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