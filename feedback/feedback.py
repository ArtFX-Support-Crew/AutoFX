import discord
from discord.ext import commands
from config import token
from terms import terms
import re
import os
import datetime
from karma import Karma 

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
karma = Karma()
enforce_requirements = True
valid_attachments = [".wav", ".mp3", ".flac"]

# Create list of required words for posting 

required_words = []
for term in terms: 
    required_words.append(term.lower())

# Some filtering configuration values for the module

min_characters = 280
required_url_pattern = r'^(?=.*\b(soundcloud|youtube|clyp\.it|mixcloud|drive|onedrive|bandcamp|dropbox)\b).*'

# Message Logging 

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}"
    print(log_entry)

    log_file = "feedback_log.txt"
    with open(log_file, 'a') as f:
        f.write(log_entry + "\n")

# function clears the contents of a feedback log file, if it exists and logs the action

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear_log(ctx):
    try:
        with open('feedback_log.txt', mode='w') as f:
            f.write('')
            await ctx.send("Log file cleared.")
            log_message("The Feedback log file has been cleared")
    except FileNotFoundError: 
        await ctx.send("The Feedback log file does not exist.")
        log_message("The Feedback log file could not be cleared.")


# Admin / Moderator command:: This commands sends a log file to the user who requested - 
# it if it exists. The request is then logged

@bot.command()
@commands.has_permissions(manage_messages=True)
async def get_log(ctx):
    try:
        with open("feedback_log.txt", "rb") as f:
            await ctx.send("Sending bot log file...", file=discord.File(f, "feedback_log.txt"))
            log_message(f"{ctx.author} requested the bot log file.")
    except FileNotFoundError:
        await ctx.send("The Feedback log file does not exist.")
        log_message("The Feedback log file was not found.")

# Admin / Moderator command: Change the number of required characters
# required in a feedback post reply, to qualify for karma reward

@bot.command()
@commands.has_permissions(manage_messages=True)
async def set_minchars(ctx, minchars: None):
    if minchars is None: 
        await ctx.send("Please enter a valid number of characters")
    else: 
        min_characters == minchars
        await ctx.send(f"The number feedback reply characters to qualify for karma reward has been set to {minchars}.")
        log_message(f"Minimum characters set to {minchars}.")


# Retrieve the Karma points from karma.json for a given user.

@bot.command()
async def get_karma(ctx, user: discord.User = None):
    if user is None:
        await ctx.send("Please mention a user to check their karma points.")
        return

    user_id = str(user.id)
    user_karma = karma.get_users().get(user_id, 0)
    await ctx.send(f"{user.mention} has {user_karma} feedback karma points!")
    log_message(f"Karma balance was retrieved via bot command for {user.mention}")

# Retrieve Karma points for the user entering the command. 

@bot.command()
async def my_karma(ctx):
    user_id = str(ctx.message.author.id)
    user_karma = karma.get_users().get(user_id, 0)
    await ctx.send(f"{ctx.message.author.mention}, you have {user_karma} feedback karma points!")
    log_message(f"{ctx.message.author.mention} retrieved their own Karma balance")

# Admin / Moderator command: 
# Command for setting allowed file types which are required to initiate a feedback request

@bot.command()
@commands.has_permissions(manage_messages=True)
async def add_extension(ctx, filetype: str):
    if filetype is None: 
        await ctx.send("Please add a file extension to add to the whitelist")
        return
    if filetype not in valid_attachments:
        valid_attachments.append(filetype)
        await ctx.send(f"{filetype} has been added to the list of allowed extensions.")
        log_message(f"{ctx.message.author.mention} has added {filetype} to the whitelist")
    else:
        await ctx.send(f"{filetype} is already in the whitelist.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def remove_extension(ctx, filetype: str):
    if filetype is None: 
        await ctx.send("Please add a file extension to remove it from the whitelist")
        return
    if filetype in valid_attachments:
        valid_attachments.remove(filetype)
        await ctx.send(f"{filetype} has been removed from the list of allowed extensions.")
        log_message(f"{ctx.message.author.mention} has removed {filetype} from the whitelist")
    else:
        await ctx.send(f"{filetype} is not on the whitelist.")

# Admin / Moderator command: These are two Discord bot commands that start and stop 
# the enforcement of feedback requirements,

@bot.command()
@commands.has_permissions(manage_messages=True)
async def start_enforce(ctx):
    global enforce_requirements
    enforce_requirements = True
    await ctx.send("Feedback requirements enforcement started!")
    log_message("Feedback requirements enforcement started!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def stop_enforce(ctx):
    global enforce_requirements
    enforce_requirements = False
    await ctx.send("Feedback requirements enforcement stopped!")
    log_message("Feedback requirements enforcement stopped!")

# Ready the bot

@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing feedback!')
    log_message(f'{bot.user.name} is now enforcing feedback!')

# Check if the message author is the bot itself, if not, continue to process messages 

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.type == discord.ChannelType.public_thread:
        print(f"Channel name: {message.channel.name}")
        log_message(f"Channel name: {message.channel.name}")
        print(f"Channel type: {message.channel.type}")
        log_message(f"Channel type: {message.channel.type}")

    # Define the forum channel with a specific ID where the bot will be enforcing

    is_forum_channel = (
        message.channel.type == discord.ChannelType.public_thread
        and message.channel.parent
        and message.channel.parent.id == 1046847054024020029
    )

    # Define the text channel with a specific ID where the bot will listen for admin commands

    is_text_channel = (
        message.channel.type == discord.ChannelType.text
        and message.channel.id == 1043598071231160401
    )

    if is_forum_channel:
        global enforce_requirements
        if enforce_requirements:
            print("Processing message in forum channel")
            log_message("Processing message in forum channel")

            thread_id = str(message.channel.id)
            user_id = str(message.author.id)

            if thread_id not in karma.get_threads():
                karma.add_thread(thread_id)

            if not karma.user_in_thread(thread_id, user_id):
                async for msg in message.channel.history(oldest_first=True):
                    parent_message = msg
                    break

    # Check if the initial post in a public thread contains a valid URL or a valid
    # audio file attachment. If it does not meet these requirements, the initial post is deleted and a
    # message is sent to the author of the post notifying them

                if not re.search(required_url_pattern, parent_message.content, re.IGNORECASE):
                    print(f"Initial post by {parent_message.author.mention} does not contain a valid URL")
                    log_message(f"Initial post by {parent_message.author.mention} does not contain a valid URL")
                    has_valid_attachment = any(att.filename.lower().endswith(tuple(valid_attachments)) for att in parent_message.attachments)
                    if not has_valid_attachment:
                        print(f"Initial post by {parent_message.author.mention} does not contain a valid audio file attachment")
                        log_message(f"Initial post by {parent_message.author.mention} does not contain a valid audio file attachment")
                        # Delete the thread
                        await message.channel.delete()
                        # Send a DM to the user
                        dm_channel = await parent_message.author.create_dm()
                        await dm_channel.send(f"{parent_message.author.mention}, your post in the thread did not meet the requirements (URL or audio file attachment). The thread has been deleted.")
                        return


    # Check if the author of the current message is the same as the author of the
    # initial post in a public thread. If the authors are the same, it means that the current message was
    # posted by the same user who created the thread, and therefore no karma should be awarded.


                if message.author == parent_message.author:
                    print("Message author is the initial poster - no reward")
                    log_message("Message author is the initial poster - no reward")
                    return

    # Check if the length of the message content is greater than or equal to the
    # value of `min_characters`. If it is, the message meets the length requirement and the code continues
    # to check for other criteria to award karma. 

                if len(message.content) >= min_characters:
                    print("Message length requirement met")
                    log_message("Message length requirement met")
                else:
                    print("Message length requirement not met")
                    log_message("Message length requirement not met")
                    return

    # Check if a message contains any of the required words in the `required_words`
    # list. 

                if any(word in message.content.lower() for word in required_words):
                    print("Message contains required words - karma will be awarded")
                    log_message("Message contains required words - karma will be awarded")
                else:
                    print("Message does not contain required words - karma will not be awarded")
                    log_message("Message does not contain required words - karma will not be awarded")
                    return

    # Award Karma

                karma.add_user_to_thread(thread_id, user_id)
                if karma.user_exists(user_id):
                    karma.increment_user_karma(user_id)
                else:
                    karma.add_user(user_id)

                karma.save()
                await message.add_reaction('✅')
                await message.channel.send(f"{message.author.mention} has earned 1 feedback Karma!")
                log_message(f"{message.author.mention} has earned 1 feedback Karma!")
        
    if is_text_channel:   
            await bot.process_commands(message)

bot.run(token)