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

# This code is creating a list called `required_words` by iterating over a list called `terms` and
# appending each term in lowercase to the `required_words` list. This is likely being done to later
# check if a message contains any of the required words in order to earn a "feedback karma point".

required_words = []
for term in terms: 
    required_words.append(term.lower())

# Some filtering configuration values for the module

min_characters = 280
required_url_pattern = r'^(https?://)?(m.|soundcloud|youtube|clyp\.it|drive|onedrive|dropbox|bandcamp|mixcloud)\.'


# Commands for retreiving Karma point balance for themselves or another user
# Plan to place this in an embed. 

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}"
    print(log_entry)

    log_file = "bot_log.txt"
    with open(log_file, 'a') as f:
        f.write(log_entry + "\n")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def send_log(ctx):
    try:
        with open("feedback_log.txt", "rb") as f:
            await ctx.send("Sending bot log file...", file=discord.File(f, "feedback_log.txt"))
            log_message(f"{ctx.author} requested the bot log file.")
    except FileNotFoundError:
        await ctx.send("The Feedback log file does not exist.")
        log_message("The Feedback log file was not found.")

@bot.command()
async def getkarma(ctx, user: discord.User = None):
    if user is None:
        await ctx.send("Please mention a user to check their karma points.")
        return

    user_id = str(user.id)
    user_karma = karma.get_users().get(user_id, 0)
    print(f"Karma balance was retrieved via bot command for {user.mention}")
    log_message(f"Karma balance was retrieved via bot command for {user.mention}")
    await ctx.send(f"{user.mention} has {user_karma} feedback karma points!")

@bot.command()
async def mykarma(ctx):
    user_id = str(ctx.message.author.id)
    user_karma = karma.get_users().get(user_id, 0)
    print(f"{ctx.message.author.mention} retrieved their own Karma balance")
    log_message(f"{ctx.message.author.mention} retrieved their own Karma balance")
    await ctx.send(f"{ctx.message.author.mention}, you have {user_karma} feedback karma points!")

# Commands for setting allowed file types which are required to initiate a feedback request
# Manage messages permission is required to use the commands. 

@bot.command()
@commands.has_permissions(manage_messages=True)
async def add_extension(ctx, filetype: str):
    if filetype is None: 
        await ctx.send("Please add a file extension to add to the whitelist")
        return
    if filetype not in valid_attachments:
        valid_attachments.append(filetype)
        print(f"{ctx.message.author.mention} has added {filetype} to the whitelist")
        log_message(f"{ctx.message.author.mention} has added {filetype} to the whitelist")
        await ctx.send(f"{filetype} has been added to the list of allowed extensions.")
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
        print(f"{ctx.message.author.mention} has removed {filetype} from the whitelist")
        await ctx.send(f"{filetype} has been removed from the list of allowed extensions.")
        log_message(f"{ctx.message.author.mention} has removed {filetype} from the whitelist")
    else:
        await ctx.send(f"{filetype} is not on the whitelist.")

# These are two Discord bot commands that start and stop the enforcement of feedback requirements,
# respectively, and require administrator permissions to execute.

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

    print(f"Channel name: {message.channel.name}")
    log_message(f"Channel name: {message.channel.name}")
    print(f"Channel type: {message.channel.type}")
    log_message(f"Channel type: {message.channel.type}")

    # Check if the message is in a forum channel with a specific ID

    is_forum_channel = (
        message.channel.type == discord.ChannelType.public_thread
        and message.channel.parent
        and message.channel.parent.id == 1046847054024020029
    )

    # Check if the message is in a text channel with a specific ID 
    # This code block is in place so that a person with appropriate permissions
    # can send commands to the bot

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

    # This code block is checking if the initial post in a public thread contains a valid URL or a valid
    # audio file attachment. If it does not meet these requirements, the initial post is deleted and a
    # message is sent to the author of the post notifying them that their post did not meet the
    # requirements.
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


    # This code block is checking if the author of the current message is the same as the author of the
    # initial post in a public thread. If the authors are the same, it means that the current message was
    # posted by the same user who created the thread, and therefore no "feedback karma" should be awarded.
    # The code prints a message saying that "no reward" will be given and returns without awarding any
    # "feedback karma".

                if message.author == parent_message.author:
                    print("Message author is the initial poster - no reward")
                    log_message("Message author is the initial poster - no reward")
                    return

    # This code block is checking if the length of the message content is greater than or equal to the
    # value of `min_characters`. If it is, the message meets the length requirement and the code continues
    # to check for other criteria to award "feedback karma". If it is not, the message does not meet the
    # length requirement and the code returns without awarding any "feedback karma"..

                if len(message.content) >= min_characters:
                    print("Message length requirement met")
                    log_message("Message length requirement met")
                else:
                    print("Message length requirement not met")
                    log_message("Message length requirement not met")
                    return

    # This code block is checking if a message contains any of the required words in the `required_words`
    # list. If it does, the code prints a message saying that "karma will be awarded". If it does not, the
    # code prints a message saying that "karma will not be awarded" and returns without awarding any
    # "feedback karma".

                if any(word in message.content.lower() for word in required_words):
                    print("Message contains required words - karma will be awarded")
                    log_message("Message contains required words - karma will be awarded")
                else:
                    print("Message does not contain required words - karma will not be awarded")
                    log_message("Message does not contain required words - karma will not be awarded")
                    return

    # This code block is awarding "feedback karma" to a user who has posted a message in a public thread
    # that meets certain criteria.

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