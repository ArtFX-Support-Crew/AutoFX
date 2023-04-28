# imports
# ----------------------------------------------    
import asyncio
import datetime
import logging
import re
import json
import io

import discord
from discord.ext import commands
from discord import Embed, File

from config import token
from feedback_points import Points
from karma import Karma
from terms import terms

# Constants and Configurations
# ----------------------------------------------

logger = logging.getLogger("feedback_log")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("feedback_bot.log", encoding="utf-8", mode="a")
print(f"Log file created at: {handler.baseFilename}")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
points = Points()
karma = Karma()
enforce_requirements = True
valid_attachments = [".wav", ".mp3", ".flac"]   

required_words = [term.lower() for term in terms]
required_points = 1

min_characters = 280

required_url_pattern = r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be|soundcloud\.com|(?:www\.)?dropbox\.com|(?:www\.)?drive\.google\.com|clyp\.it)/'

# Logging configuration setup
# ----------------------------------------------    

@bot.command(name="log", help="Sends the log file as an attachment or clears it.\n Usage: /log <get/clear>")
@commands.has_permissions(manage_messages=True)
async def log(ctx, action: str = "get"):
    """Feedback - log: Get or Clear the log file.

    Args:
        action (str): get / clear. Defaults to "get".

    Examples:
        /log get - Sends the log file as an attachment.
        /log clear - Clears the log file.
    """
    log_file = next(
        (
            handler.baseFilename
            for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ),
        None,
    )
    if log_file is None:
        await ctx.send("No log file found.")
        return

    if action.lower() == "get":
        try:
            with open('feedback_bot.log', 'rb') as log_file:
                log_content = log_file.read()

            if log_content:
                log_bytes = io.BytesIO(log_content)
                log_attachment = discord.File(log_bytes, filename="feedback_bot.log")
                await ctx.send(file=log_attachment)
            else:
                await ctx.send("The log file is empty.")
        except FileNotFoundError:
            await ctx.send("The log file could not be found.")
    elif action.lower() == "clear":
        try:
            with open(log_file, 'w') as f:
                f.truncate(0)

            await ctx.send("The log file has been cleared.")
        except FileNotFoundError:
            await ctx.send("The log file could not be found.")
    else:
        await ctx.send("Invalid action. Usage: /log <get/clear>")



# If the user lacks permissions to use a bot command, or the command doesn't exist,
# inform the user
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send("An error occurred while processing your command.")

def help_command(ctx):
    """
    Displays a list of available bot commands.
    """
    # Create a new Embed object
    embed = discord.Embed(title="Feedback Bot Command List")

    # Loop through all of the bot's commands and add them to the Embed
    for command in bot.commands:
        # Check if the command is hidden or not
        if not command.hidden:
            # Add the command name and help string to the Embed
            embed.add_field(name=f"{command.name}", value=f"{command.help}", inline=False)

    # Send the Embed to the channel where the command was issued
    ctx.send(embed=embed)

# Feedback text channels for bot commands and forum channels for feedback enforcement
# are set in feedback_channels.json
# function reads the channel IDs from the file

def read_channel_ids():
    with open("feedback_channels.json", "r") as file:
        data = json.load(file)
        return data["forum_channel_ids"], data["text_channel_ids"]

def update_channel_ids(forum_channel_ids, text_channel_ids):
    data = {
        "forum_channel_ids": forum_channel_ids,
        "text_channel_ids": text_channel_ids
    }
    with open("feedback_channels.json", "w") as file:
        json.dump(data, file)




@bot.command(name="channel", help="Add or remove a forum or text channel ID where the bot enforces rules.\n Usage: /channel <add/remove> <forum/text> <channel_id>")
@commands.has_permissions(manage_messages=True)
async def set_channel(ctx, action: str, channel_type: str, channel_id: int):
    """Feedback - set_channel: Add or remove a forum or text channel ID where the bot enforces rules.
        Args:
        action (str): add / remove.
        channel_type (str): forum / text.

    Examples:
        /log get - Sends the log file as an attachment.
        /log clear - Clears the log file.
    """
    forum_channel_ids, text_channel_ids = read_channel_ids()

    if action.lower() not in ["add", "remove"]:
        await ctx.send("Invalid action. Usage: /channel <add/remove> <forum/text> <channel_id>")
        logger.warning("An invalid set_channel action was entered.")
        return

    if channel_type.lower() == "forum":
        if action.lower() == "add":
            if channel_id not in forum_channel_ids:
                forum_channel_ids.append(channel_id)
                await ctx.send(f"Forum channel ID {channel_id} has been added.")
                logger.info(f"Forum channel ID {channel_id} has been added.")
            else:
                await ctx.send(f"Forum channel ID {channel_id} is already in the list.")
                logger.info(f"Forum channel ID {channel_id} is already in the list.")
        elif action.lower() == "remove":
            if channel_id in forum_channel_ids:
                forum_channel_ids.remove(channel_id)
                await ctx.send(f"Forum channel ID {channel_id} has been removed.")
                logger.info(f"Forum channel ID {channel_id} has been removed.")
            else:
                await ctx.send(f"Forum channel ID {channel_id} is not in the list.")
    elif channel_type.lower() == "text":
        if action.lower() == "add":
            if channel_id not in text_channel_ids:
                text_channel_ids.append(channel_id)
                await ctx.send(f"Text channel ID {channel_id} has been added.")
            else:
                await ctx.send(f"Text channel ID {channel_id} is already in the list.")
        elif action.lower() == "remove":
            if channel_id in text_channel_ids:
                text_channel_ids.remove(channel_id)
                await ctx.send(f"Text channel ID {channel_id} has been removed.")
            else:
                await ctx.send(f"Text channel ID {channel_id} is not in the list.")
    else:
        await ctx.send("Invalid channel type. Usage: /channel <add/remove> <forum/text> <channel_id>")

    # Update the channel IDs in the JSON file
    update_channel_ids(forum_channel_ids, text_channel_ids)

# Admin / Moderator command: Grant a specific number of Feedback Points to a user.
@bot.command(name="grant", help="Grant a specific number of Feedback Points to a user.\nUsage: /grant <@user> <points_to_grant>")
@commands.has_permissions(manage_messages=True)
async def grant_points(ctx, user: discord.User, points_to_grant: int):
    if user is None or points_to_grant is None:
        await ctx.send("Please mention a user and provide the number of points to grant.")
        logger.warning("grant_points function was called without sufficient arguments.")
        return

    user_id = str(user.id)
    points.grant_points(user_id, points_to_grant)
    new_points = points.get_users().get(user_id, 0)

    await ctx.send(f"{user.mention} has been granted {points_to_grant} Feedback Points! Their new balance is {new_points}.")
    logger.info(f"{ctx.author} granted {points_to_grant} Feedback Points to {user.mention}.")

@bot.command(name="requiredpoints", help="Set the required number of Feedback Points for a user to initiate a new Feedback Request.\n Usage: /requiredpoints <number>")
@commands.has_permissions(manage_messages=True)
async def requiredpoints(ctx, new_required_points: int):
    global required_points
    if new_required_points is None: 
        await ctx.send("The required points value must be a valid number.")
        return
    if new_required_points < 0:
        await ctx.send("The required points value must be at least 0.")
        return
    else:
        required_points = new_required_points
        await ctx.send(f"Required points value has been set to {required_points}.")
        logger.info(f"The required points value has been updated. The new value is {required_points}")


# Admin / Moderator command: Change the number of required characters
# required in a feedback post reply, to qualify for Feedback Point reward

@bot.command(name="minchars", help="Set the required number of characters for Feedback to be eligable for rewards.\n Usage: /minchars <number>")
@commands.has_permissions(manage_messages=True)
async def minchars(ctx, chars: int):
    global min_characters
    if chars is None: 
        await ctx.send("Please enter a valid number of characters")
        return
    try: 
        min_characters = chars
        await ctx.send(f"The number feedback reply characters to qualify for Feedback Points reward has been set to {min_characters}.")
        logger.info(f"Minimum characters set to {min_characters}.")
    except ValueError: 
        await ctx.send("Please enter a valid integer for number of characters")


# Retrieve the Feedback points from feedback_points.json for a given user.

@bot.command(name="points", help="Get the number of Feedback Points for a given user. \n Usage: /points <@user>")
async def feedbackpoints(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
        points_balance = points.get_users().get(user, 0)
        await ctx.send(f"{ctx.author} has {points_balance} Feedback Points.")
        return
    user_id = str(user.id)
    user_points = points.get_users().get(user_id, 0)
    await ctx.send(f"{user.mention} has {user_points} Feedback Points!")
    logger.info(f"Feedback Points value was retrieved via bot command for {user.mention}")

@bot.command(name="karma", help="Check your Karma.\n Usage: /karma <@user>")
async def karmapoints(ctx, user: discord.User = None):
    if user is None: 
        user = ctx.author
    user_id = str(user.id)
    karma_total = karma.get_karma_total(user_id)

    if user == ctx.author:
        embed = discord.Embed(title=f"Karma - {ctx.author}", description=f"Your Karma: {karma_total}", color=0x00ff00)
        logger.info(f"{ctx.author} retrieved their Karma.")
    else:
        embed = discord.Embed(title=f"Karma - {user}", description=f"{user}'s Karma: {karma_total}", color=0x00ff00) 
        logger.info(f"{ctx.author} retrieved {user}'s Karma.")
    
    # Create the embed

    await ctx.send(embed=embed)

@bot.command(name="leaderboard", help="Displays a server leaderboard ranked by Karma.\n Usage: /leaderboard")
# Displays a server leaderboard ranked by Karma
async def leaderboard(ctx): 
    # get a list of user total karma from karma.json and sort it as a leaderboard
    leaderboard = karma.get_leaderboard()
    leaderboard_string = "\n\n"
    for user_id, karma_total in leaderboard:
        user = await bot.fetch_user(user_id)
        leaderboard_string += f"{user} - {karma_total}\n"

    embed = discord.Embed(title="Feedback - Karma Leaderboard", description=leaderboard_string, color=0x00ff00)
    await ctx.send(embed=embed)


# Admin / Moderator command: 
# Command for setting allowed file types which are required to initiate a Feedback Request.

@bot.command(name="extension", help="Add/Remove an extension from the allowed extensions list. \n Usage: /extension <add/remove> <filetype>")
@commands.has_permissions(manage_messages=True)
async def extension(ctx, action: str, filetype: str):
    """Add/Remove an extension from the allowed extensions list.

    Args:
        action (str): add / remove
        filetype (str examples): .mp3, .wav, .ogg
    """
    if action is None or filetype is None:
        await ctx.send("Please provide an action (add/remove) and a file extension.")
        return

    action = action.lower()

    if action == "add":
        if filetype not in valid_attachments:
            valid_attachments.append(filetype)
            await ctx.send(f"{filetype} has been added to the list of allowed extensions.")
            logger.info(f"{ctx.author} has added {filetype} to the whitelist")
        else:
            await ctx.send(f"{filetype} is already in the whitelist.")
    elif action == "remove":
        if filetype in valid_attachments:
            valid_attachments.remove(filetype)
            await ctx.send(f"{filetype} has been removed from the list of allowed extensions.")
            logger.info(f"{ctx.author} has removed {filetype} from the whitelist")
        else:
            await ctx.send(f"{filetype} is not on the whitelist.")
    else:
        await ctx.send("Invalid action. Usage: /extension <add/remove> <filetype>")


# Admin / Moderator command: Toggle the enforcement for initial post requirements. Setting to Enabled
# will enforce a check that a user has minimum feedback points to post a new request. Subsequently, if a Feedback
# Request is made, Feedback points are deducted from their balance tracked in feedback_points.json

@bot.command(name="enforce", help="Enable or Disable Feedback Enforcement \n Usage: /enforce <enable/disable>")
@commands.has_permissions(manage_messages=True)
async def enforce(ctx, status: str):
    """Enable or Disable Feedback Enforcement

    Args:
        status (str): enable / disable
    """
    global enforce_requirements
    status = status.lower()
    if status is None or status not in ["enable", "disable"]:
        await ctx.send("Please enter a valid enforcement status.")
        return
    if status == 'disable':
        if enforce_requirements:
            enforce_requirements = False
            await ctx.send("Feedback Request enforcement disabled.")
        else:
            await ctx.send("Feedback Request enforcement is already disabled.")
    elif status == 'enable':
        if not enforce_requirements:
            enforce_requirements = True
            await ctx.send("Feedback Request enforcement enabled.")
        else:
            await ctx.send("Feedback Request enforcement is already enabled.")
    else:
        await ctx.send("Invalid argument. Usage: /enforce <enable/disable>")


@bot.command(name="keywords", help="Add or remove a required keyword from the Feedback word filter.\n Usage: /keywords <add/remove> <keyword>")
@commands.has_permissions(manage_messages=True)
async def keywords(ctx, action: str, word: str):
    """ Admin / Moderator command: Add or remove a required keyword from the Feedback word filter. 
    Args:
        action (str): add / remove
        keyword (str examples): compression, mix, sidechain
    """
    action = action.lower()
    if word is None:
        await ctx.send("Please enter a word to add or remove from the Feedback word filter.")
        return
    if action == 'add':
        if word.lower() not in required_words:
            required_words.append(word.lower())
            await ctx.send(f"{word} has been added to the Feedback word filter.")
            logger.info(f"{ctx.author} added {word} to Feedback word filter.")
        else:
            await ctx.send(f"{word} is already in the Feedback word filter.")
    elif action == 'remove':
        if word.lower() in required_words:
            required_words.remove(word.lower())
            await ctx.send(f"{word} has been removed from the Feedback word filter.")
            logger.info(f"{ctx.author} removed {word} from Feedback word filter.")
        else:
            await ctx.send(f"{word} is not in the Feedback word filter.")
    else:
        await ctx.send("Invalid action. Usage: !keyword <add/remove> <word>")


@bot.command(name='commands', help='Show a list of all Feedback bot commands\n Usage: /commands')
async def commands_list(ctx):
    embed = Embed(
        title="Feedback Commands",
        description="Here's a list of available commands:",
        color=0x00FF00  # Green color
    )

    # Add a field to embed. embed. add_field name value help inline False
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)

    await ctx.send(embed=embed)

# Ready the bot
@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing Feedback!')
    logger.info(f'{bot.user.name} is now enforcing Feedback!')

# Check if the message author is the bot itself, if not, continue to process messages 

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.type == discord.ChannelType.public_thread:
        print(f"Channel name: {message.channel.name}")
        logger.info(f"Channel name: {message.channel.name}")
        print(f"Channel type: {message.channel.type}")
        logger.info(f"Channel type: {message.channel.type}")

    is_forum_channel = (
        message.channel.type == discord.ChannelType.public_thread
        and message.channel.parent
        and message.channel.parent.id in read_channel_ids()[0]
    )

    is_text_channel = (
        message.channel.type == discord.ChannelType.text
        and message.channel.id in read_channel_ids()[1]
    )



    if is_forum_channel:
        
        global enforce_requirements
        if enforce_requirements:
            print("Processing message in forum channel")
            logger.info("Processing message in forum channel")

            thread_id = str(message.channel.id)
            user_id = str(message.author.id)

            # Check if the thread exists in the feedback_points.json file, if not, add it
            if thread_id not in points.get_threads():
                points.add_thread(thread_id)
                print(f'Added thread {thread_id} to feedback_points.json')
                points.save()



            # Check if the user exists in the feedback_points.json file, if not, add it
            async for msg in message.channel.history(oldest_first=True):
                parent_message = msg
                break

                # If it is the initial post, check that it meets the requirements
            is_initial_post = message.created_at == parent_message.created_at
            print(f'Message created: {message.created_at}. Parent message created: {parent_message.created_at}. Is initial post: {is_initial_post}')
            if is_initial_post:

                print("New Feedback Request submitted - Checking user Feedback Point and Post requirements")
                logger.info("New Feedback Request submitted - Checking user Feedback Point and Post requirements")

                # Criteria for a valid Feedback Request
                contains_valid_url = bool(re.search(required_url_pattern, message.content))
                contains_valid_attachment = any(
                    attachment.filename.endswith(tuple(valid_attachments))
                    for attachment in message.attachments
                )

                # Check if the message contains either a valid URL or a valid attachment, if not delete the post
                if not (contains_valid_url or contains_valid_attachment):
                    await message.channel.delete()
                    print(f"User {message.author.id} Feedback Request was deleted due to not containing a valid URL or audio attachment.")
                    logger.info(f"User {message.author.id} Feedback Request was deleted due to not containing a valid URL or audio attachment.")
                    response = (f"{message.author.mention}, your Feedback Request has been removed since it did not meet requirements. To create a Feedback Request, you need to include a valid URL or audio attachment: {valid_attachments}\n\n")
                    dm_channel = await parent_message.author.create_dm()
                    await dm_channel.send(response)
                    return
                # Check if the user has at least the minimum required feedback points in feedback_points.json. 
                # If not, delete the post and send a DM to the user
                user_points = points.get_users().get(user_id, 0)
                if user_points < required_points:
                    await message.channel.delete()
                    print(f"User {message.author.id}'s Feedback Request was deleted due to insufficient Feedback Points.")
                    logger.info(f"User {message.author.id} Feedback Request was deleted due to insufficient Feedback Points.")
                    response = (f"{message.author.mention}, your Feedback Request - {message.channel.name} has been removed. You need at least {required_points} Feedback Points to create a Feedback Request. Your current Feedback Points: {user_points}\n\n To earn Feedback Points, provide some feedback for other users.")
                    dm_channel = await parent_message.author.create_dm()
                    await dm_channel.send(response) 
                    return
                else: 
                    # Allow the Feedback Request, decrease the user's Feedback Points by the required amount
                    points.increment_user_points(user_id, -required_points)
                    updated_user_points = points.get_points(user_id)
                    print(f"User {message.author.id} has sufficient Feedback Points and Post meets requirements..")
                    logger.info(f"User {message.author.id} has sufficient Feedback Points and Post meets requirements..")
                    print(f"User {parent_message.author.mention} has made a new Feedback Request and {required_points} Feedback Points has been deducted from their balance.")
                    logger.info(f"User {parent_message.author.mention} has made a new Feedback Request and {required_points} Feedback Points has been deducted from their balance.")
                    response = (f"{parent_message.author.mention}, you have successfully created a Feedback Request - {message.channel.name}. {required_points} Feedback Points have been deducted from your balance. Your updated Feedback Points: {updated_user_points}\n\n")
                    dm_channel = await parent_message.author.create_dm()
                    await dm_channel.send(response)

            else: 
                print('post is not an initial post')
            # if the message is a reply to the initial forum pos

                print(f'Feedback provided by {message.author} in thread {thread_id} meets requirements. Checking reward status...')
                logger.info(f'Feedback provided by {message.author} in thread {thread_id} meets requirements. Checking reward status...')
                if parent_message.author.id == message.author.id:
                    print(f'User {message.author} is the Feedback Request Author. No points awarded.')
                    return
                
                contains_required_words = any(word in message.content for word in required_words)
                message_length = len(message.content)
                if contains_required_words and message_length >= min_characters:   
                    print(f'Message contains required words and meets minimum character requirements.')
                    logger.info(f'Message contains required words and meets minimum character requirements.')
                    if not points.user_in_thread(thread_id, user_id):
                        points.add_user_to_thread(thread_id, user_id)
                        print(f'Feedback provided by {message.author} in thread {thread_id} meets requirements. Awarding 1 Feedback Point and 1 Karma Point.')
                        logger.info(f'Feedback provided by {message.author} in thread {thread_id} meets requirements. Awarding 1 Feedback Point and 1 Karma Point.')
                        points.increment_user_points(user_id, required_points)
                        points.save()
                        await message.add_reaction('✅')
                        karma.increment_user_karma(user_id, 1)
                        karma.save()
                        await message.add_reaction('✅')
                        # bot message in thread that feedback point has been awarded
                        response = (f"{message.author.mention}, has earned one Feedback Point and increased their Karma!\n\n")
                        await message.channel.send(response)
                    else:
                        print(f'User {message.author} has already provided feedback in thread {thread_id}.')
                        logger.info(f'User {message.author} has already provided feedback in thread {thread_id}.')
                    return
                else: 
                    print('Message did not meet requirements. No points rewarded')
    if is_text_channel:   
        await bot.process_commands(message)

        # Run the bot
bot.run(token)
