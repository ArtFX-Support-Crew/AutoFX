import discord
from discord.ext import commands
from config import token
from terms import terms
import re
import datetime
from feedback_points import Points 
from feedback_points import required_points
from karma import Karma 
import logging

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
point_requirements = True
valid_attachments = [".wav", ".mp3", ".flac"]

# Create list of required words for posting 

required_words = []
for term in terms: 
    required_words.append(term.lower())

# Some filtering configuration values for the module

min_characters = 280
required_url_pattern = r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be|soundcloud\.com|(?:www\.)?dropbox\.com|(?:www\.)?drive\.google\.com|clyp\.it)/'

# Message Logging 

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}"
    logging.info(log_entry)

    log_file = "feedback_log.txt"
    with open(log_file, 'a') as f:
        f.write(log_entry + "\n")

# If the user lacks permissions to use a bot command, or the command doesnt exist -
# inform the user

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send("An error occurred while processing your command.")

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

@bot.command(name="get_log", help="Get the Feeback Bot Log.")
@commands.has_permissions(manage_messages=True)
async def get_log(ctx):
    try:
        with open("feedback_log.txt", "rb") as f:
            await ctx.send("Sending bot log file...", file=discord.File(f, "feedback_log.txt"))
            log_message(f"{ctx.author} requested the bot log file.")
    except FileNotFoundError:
        await ctx.send("The Feedback log file does not exist.")
        log_message("The Feedback log file was not found.")

@bot.command(name="grant", help="Grant a specific number of Feedback Points to a user.")
@commands.has_permissions(manage_messages=True)
async def grant_points(ctx, user: discord.User, points_to_grant: int):
    if user is None or points_to_grant is None:
        await ctx.send("Please mention a user and provide the number of points to grant.")
        return

    user_id = str(user.id)
    points.grant_points(user_id, points_to_grant)
    new_points = points.get_users().get(user_id, 0)

    await ctx.send(f"{user.mention} has been granted {points_to_grant} Feedback Points! Their new balance is {new_points}.")
    log_message(f"{ctx.author} granted {points_to_grant} Feedback Points to {user.mention}.")

@bot.command(name="requiredpoints", help="Set the required number of Feedback Points for a user to initiate a new Feedback Request.")
@commands.has_permissions(manage_messages=True)
async def requiredpoints(ctx, new_required_points: int):
    global required_points
    if new_required_points is None: 
        await ctx.send("The required points value must be a valid number.")
        return
    if new_required_points < 0:
        await ctx.send("The required points value must be at least 0.")
    else:
        required_points = new_required_points
        await ctx.send(f"Required points value has been set to {required_points}.")


# Admin / Moderator command: Change the number of required characters
# required in a feedback post reply, to qualify for Feedback Point reward

@bot.command()
@commands.has_permissions(manage_messages=True)
async def minchars(ctx, chars: int):
    global min_characters
    if chars is None: 
        await ctx.send("Please enter a valid number of characters")
        return 
    try: 
        min_characters = int(chars)
        await ctx.send(f"The number feedback reply characters to qualify for Feedback Points reward has been set to {min_characters}.")
        log_message(f"Minimum characters set to {min_characters}.")
    except ValueError: 
        await ctx.send("Please enter a valid integer for number of characters")


# Retrieve the Feedback points from feedback_points.json for a given user.

@bot.command()
async def getpoints(ctx, user: discord.User = None):
    if user is None:
        await ctx.send("Please mention a user to check their Feedback Points.")
        return
    user_id = str(user.id)
    user_points = points.get_users().get(user_id, 0)
    await ctx.send(f"{user.mention} has {user_points} Feedback Points!")
    log_message(f"Feedback Points balance was retrieved via bot command for {user.mention}")

# Admin / Moderator command: 
# Command for setting allowed file types which are required to initiate a Feedback Request.

@bot.command(name="extension", help="Add/Remove an extension from the allowed extensions list.")
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
            log_message(f"{ctx.author} has added {filetype} to the whitelist")
        else:
            await ctx.send(f"{filetype} is already in the whitelist.")
    elif action == "remove":
        if filetype in valid_attachments:
            valid_attachments.remove(filetype)
            await ctx.send(f"{filetype} has been removed from the list of allowed extensions.")
            log_message(f"{ctx.author} has removed {filetype} from the whitelist")
        else:
            await ctx.send(f"{filetype} is not on the whitelist.")
    else:
        await ctx.send("Invalid action. Usage: /extension <add/remove> <filetype>")


# Admin / Moderator command: Toggle the enforcement for initial post requirements. Setting to Enabled
# will enforce a check that a user has minimum feedback points to post a new request. Subsequently, if a Feedback
# Request is made, Feedback points are deducted from their balance tracked in feedback_points.json

@bot.command(name="enforce", help="Enable or Disable Feedback Enforcement")
@commands.has_permissions(manage_messages=True)
async def enforce(ctx, status: str):
    """Enable or Disable Feedback Enforcement

    Args:
        status (str): enable / disable
    """
    global enforce_requirements
    status = status.lower()
    if status is None or (status != "enable" and status != "disable"):
        await ctx.send(f"Please enter a valid enforcement status.")
        return
    if status == 'enable':
        if not enforce_requirements:
            enforce_requirements = True
            await ctx.send("Feedback Request enforcement enabled.")
        else:
            await ctx.send("Feedback Request enforcement is already enabled.")
    elif status == 'disable':
        if enforce_requirements:
            enforce_requirements = False
            await ctx.send("Feedback Request enforcement disabled.")
        else:
            await ctx.send("Feedback Request enforcement is already disabled.")
    else:
        await ctx.send("Invalid argument. Usage: /enforce <enable/disable>")


@bot.command(name="keywords", help="Add or remove a required keyword from the Feedback word filter.")
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
            log_message(f"{ctx.author} added {word} to Feedback word filter.")
        else:
            await ctx.send(f"{word} is already in the Feedback word filter.")
    elif action == 'remove':
        if word.lower() in required_words:
            required_words.remove(word.lower())
            await ctx.send(f"{word} has been removed from the Feedback word filter.")
            log_message(f"{ctx.author} removed {word} from Feedback word filter.")
        else:
            await ctx.send(f"{word} is not in the Feedback word filter.")
    else:
        await ctx.send("Invalid action. Usage: !keyword <add/remove> <word>")

# Ready the bot
@bot.event
async def on_ready():
    print(f'{bot.user.name} is now enforcing Feedback!')
    log_message(f'{bot.user.name} is now enforcing Feedback!')

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

    is_forum_channel = (
        message.channel.type == discord.ChannelType.public_thread
        and message.channel.parent
        and message.channel.parent.id == 1046847054024020029
    )

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

            if thread_id not in points.get_threads():
                points.add_thread(thread_id)

            if not points.user_in_thread(thread_id, user_id):
                async for msg in message.channel.history(oldest_first=True):
                    parent_message = msg
                    break

                is_initial_post = message.created_at == parent_message.created_at

                if is_initial_post:
                    print("New Feedback Request submitted - Checking user Feedback Point and Post requirements")
                    log_message("New Feedback Request submitted - Checking user Feedback Point and Post requirements")

                    # Check if the message contains a valid URL or a valid attachment
                    contains_valid_url = bool(re.search(required_url_pattern, message.content))
                    contains_valid_attachment = any([attachment.filename.endswith(tuple(valid_attachments)) for attachment in message.attachments])

                    # If the initial post does not contain a valid URL or attachment, delete the channel and inform the user
                    if not (contains_valid_url or contains_valid_attachment):
                        await message.channel.delete()
                        log_message(f"User {message.author.id} Feedback Request was deleted due to not containing a valid URL or audio attachment.")
                        response = (
                            f"{message.author.mention}, your post has been removed. To create a Feedback Request, you need to include a valid URL or audio attachment: {valid_attachments}\n\n"
                        )
                        dm_channel = await parent_message.author.create_dm()
                        await dm_channel.send(response)
                        return

                    if point_requirements:
                        user_points = points.get_users().get(str(message.author.id), 0)
                        if user_points < required_points:
                            await message.channel.delete()
                            log_message(f"User {message.author.id} Feedback Request was deleted due to insufficient Feedback Points.")
                            response = (
                                f"{message.author.mention}, your Feedback Request has been removed. You need at least {required_points} Feedback Points to create a Feedback Request. Your current Feedback Points: {user_points}\n\n"
                                "To earn Feedback Points, provide some feedback for other users."
                            )
                            dm_channel = await parent_message.author.create_dm()
                            await dm_channel.send(response)
                        else:
                            log_message(f"User {message.author.id} Has sufficient Feedback Points and Post meets requirements..")
                            points.increment_user_points(str(message.author.id), -1)
                            updated_user_points = points.get_users().get(str(message.author.id), 0)
                            log_message(f"User {parent_message.author.mention} has made a new Feedback Request and {required_points} Feedback Points has been deducted from their balance.")
                            response = (
                                f"{message.author.mention}, you have successfully created a Feedback Request. {required_points} Feedback Points have been deducted from your balance. Your updated Feedback Points: {updated_user_points}\n\n"
                            )
                            dm_channel = await parent_message.author.create_dm()
                            await dm_channel.send(response)
                        return
                    if not is_initial_post:
                        log_message(f"Processing Feedback given by {parent_message.author.mention} for Feedback Request {message.channel.name}")
                        if message.author != parent_message.author:  
                            log_message(f"Message author is not the Feedback requestor. Continue Processing Message.")
                            if any(word in message.content.lower() for word in required_words):
                                print("Message contains required words - Feedback Points will be awarded")
                                log_message("Message contains required words - Feedback Points will be awarded")
                            else:
                                print("Message does not contain required words - Feedback Points will not be awarded")
                                log_message("Message does not contain required words - Feedback Points will not be awarded")
                                return

                        # Award Feedback Points
                        if len(message.content) < min_characters:
                            log_message("Message does not contain enough characters to be eligible for Feedback Points.")
                            return
                        points.add_user_to_thread(thread_id, user_id)
                        if points.user_exists(user_id):
                            points.increment_user_points(user_id)
                            karma.increment_user_karma(user_id, 1)
                        else:
                            points.add_user(user_id)

                        points.save()
                        await message.add_reaction('✅')
                        await message.channel.send(f"{message.author.mention} has earned 1 Feedback Point!")
                        log_message(f"{message.author.mention} has earned 1 Feedback Point!")
        
    
    # In Text channels (Restricted by Channel ID) process bot commands  

    if is_text_channel:   
            await bot.process_commands(message)

# Run the bot

bot.run(token)