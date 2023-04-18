import discord
from discord.ext import commands
from config import token
from terms import terms
import re
import datetime
from karma import Karma 
import logging

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
karma = Karma()
enforce_requirements = True
point_requirements = False
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
async def set_minchars(ctx, minchars: int):
    if minchars is None: 
        await ctx.send("Please enter a valid number of characters")
        return 
    try: 
        int(minchars)
        await ctx.send(f"The number feedback reply characters to qualify for karma reward has been set to {minchars}.")
        log_message(f"Minimum characters set to {minchars}.")
    except ValueError: 
        await ctx.send("Please enter a valid integer for number of characters")


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
    log_message(f"{ctx.author} retrieved their own Karma balance")

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
        log_message(f"{ctx.author} has added {filetype} to the whitelist")
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
        log_message(f"{ctx.author} has removed {filetype} from the whitelist")
    else:
        await ctx.send(f"{filetype} is not on the whitelist.")

# Get leaderboard for Karma points

@bot.command()
async def feedback_lb(ctx):
    users = karma.get_users()

    if not users:
        await ctx.send("No users found!")
        return

    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)

    leaderboard_text = "Leaderboard:\n\n"

    for i, (user_id, karma_points) in enumerate(sorted_users[:10], start=1):
        user = await bot.fetch_user(user_id)
        leaderboard_text += f"{i}. {user.name}#{user.discriminator}: {karma_points} points\n"

    embed = discord.Embed(title="Feedback Karma Leaderboard", description=leaderboard_text, color=0x00ff00)
    await ctx.send(embed=embed)
    log_message(f"{ctx.author} retrieved the Feedback Leaderboard")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def feedback_commands(ctx):

    commands_text = "Commands:\n\n"

    commands_text += "**!clear_log**: Clear the feedback bot log. \n"
    commands_text += "**!get_log**: Get the feedback bot log. \n"
    commands_text += "**!set_minchars** *<int>*: Set the minimum number of characters in a reply to make it eligible for karma rewards. \n"
    commands_text += "**!get_karma** *<user>*: Retrieve the Karma point balance for a specific user. \n"
    commands_text += "**!my_karma**: Retrieve the Karma point balance for user sending the command. \n"
    commands_text += "**!add_extension** *<extension>*: Add an extension to the list of allowed extensions in initial feedback posts. \n"
    commands_text += "**!remove_extension** *<extension>*: Remove an extension from the list of allowed extensions in initial feedback posts. \n"
    commands_text += "**!add_required_word** *<word>*: Add a word to the feedback filter. \n"
    commands_text += "**!remove_required_word** *<word>*: Remove a word from the feedback filter. \n"
    commands_text += "**!feedback_lb**: Show a leaderboard of Feedback Karma points. \n"
    commands_text += "**!start_enforce**: Start Enforcing feedback requirements and awarding Karma. \n"
    commands_text += "**!stop_enforce**: Stop Enforcing feedback requirements and awarding Karma. \n"
    commands_text += "**!toggle_point_requirements**: Toggle enforcement of initial feedback request Karma requirements. \n"
    
    embed = discord.Embed(title="Feedback Bot Commands", description=commands_text, color=0x00ff00)
    await ctx.send(embed=embed)
    log_message(f"{ctx.author} retrieved the Feedback Command list")

# Admin / Moderator command: These are two Discord bot commands that start and stop 
# the enforcement of feedback requirements for URL or audio attachment in initial posts

@bot.command(name="start_enforce", help="Starts feedback post enforcement for attachment and URL standards.")
@commands.has_permissions(manage_messages=True)
async def start_enforce(ctx):
    global enforce_requirements
    enforce_requirements = True
    await ctx.send("Feedback requirements enforcement started!")
    log_message(f"Feedback requirements enforcement started by {ctx.author}.")

@bot.command(name="stop_enforce", help="Stops feedback post enforcement for attachment and URL standards.")
@commands.has_permissions(manage_messages=True)
async def stop_enforce(ctx):
    global enforce_requirements
    enforce_requirements = False
    await ctx.send("Feedback requirements enforcement stopped!")
    log_message(f"Feedback requirements enforcement stopped by {ctx.author}.")

# Admin / Moderator command: Toggle the requirement for initial feedback post karma requirements. Setting to Enabled
# will enforce a check that a user has minimum feedback points to post a new request. Subsequently, if a feedback
# post is made, 1 Karma point is deducted from their balance tracked in karma.json

@bot.command(name="toggle_point_requirements", help="Toggles the feedback point requirement for creating new feedback requests.")
@commands.has_permissions(manage_channels=True)
async def toggle_point_requirements(ctx):
    global point_requirements
    point_requirements = not point_requirements
    status = "enabled" if point_requirements else "disabled"
    await ctx.send(f"Feedback point requirement is now {status}.")

# Admin / Moderator command: Add or remove required words from the filter list. 

@bot.command(name="add_required_word", help="Add a required word to the feedback word filter.")
@commands.has_permissions(manage_messages=True)
async def add_required_word(ctx, word: str):
    if word is None:
        await ctx.send("Please enter a word to add to the feedback word filter.")
        return

    if word.lower() not in required_words:
        required_words.append(word.lower())
        await ctx.send(f"{word} has been added to the feedback word filter.")
        log_message(f"{ctx.author} added {word} to feedback word filter.")
    else:
        await ctx.send(f"{word} is already in the feedback word filter.")

@bot.command(name="remove_required_word", help="Remove a required word from the feedback word filter.")
@commands.has_permissions(manage_messages=True)
async def remove_required_word(ctx, word: str):
    if word is None:
        await ctx.send("Please enter a word to remove from the feedback word filter.")
        return

    if word.lower() in required_words:
        required_words.remove(word.lower())
        await ctx.send(f"{word} has been removed from the feedback word filter.")
        log_message(f"{ctx.author} removed {word} from the feedback word filter.")
    else:
        await ctx.send(f"{word} is not in the feedback word filter.")


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

                url_match = re.search(required_url_pattern, parent_message.content, re.IGNORECASE)
                if url_match is not None:
                    log_message(f"Message has a valid url! Found URL: {url_match.group(0)}")
                elif any(att.filename.lower().endswith(tuple(valid_attachments)) for att in parent_message.attachments):
                    log_message(f"Message has a valid attachment! {parent_message.attachments}")
                else:
                    print(f"Initial post by {parent_message.author.mention} does not contain a valid URL or audio file attachment")
                    log_message(f"Initial post by {parent_message.author.mention} does not contain a valid URL or audio file attachment")
                    # Delete the thread
                    await message.channel.delete()
                    log_message(f"Feedback post by {parent_message.author.mention} has been deleted.")
                    # Send a DM to the user
                    dm_channel = await parent_message.author.create_dm()
                    await dm_channel.send(f"{parent_message.author.mention}, your post in the thread did not meet the requirements (URL or audio file attachment). The thread has been deleted.")
                    log_message(f"User {parent_message.author.mention} has been informed via DM that their post did not meet the requirements.")
                    return


                # Point Requirements: Check if the author of the current message is the same as the author of the
                # initial post in a public thread. If the authors are the same, it means that the current message was
                # posted by the same user who created the thread, and therefore no karma should be awarded.


                if message.author == parent_message.author:
                    print("Message author is the initial poster - no reward")
                    log_message("Message author is the initial poster - no reward")

                    if point_requirements:
                        user_karma = karma.get_users().get(str(message.author.id), 0)
                        if user_karma < 1:
                            await message.delete()
                            log_message(f"User {message.author.id} Feedback request was deleted due to insufficient Karma points.")
                            response = (
                                f"{message.author.mention}, your post has been removed. You need at least 1 karma points to create a feedback request. Your current karma points: {user_karma}\n\n"
                                "If you believe this was an error, please contact a moderator."
                            )
                            dm_channel = await parent_message.author.create_dm()
                            await dm_channel.send(response)
                        else:
                            # Deduct one karma point if user_karma is sufficient
                            karma.increment_user_karma(str(message.author.id), -1)
                            updated_user_karma = karma.get_users().get(str(message.author.id), 0)
                            log_message(f"User {parent_message.author.mention} has made a new Feedback request and 1 karma point has been deducted from their balance.")
                            response = (
                                f"{message.author.mention}, you have successfully created a feedback request. One karma point has been deducted from your balance. Your updated karma points: {updated_user_karma}\n\n"
                            )
                            dm_channel = await parent_message.author.create_dm()
                            await dm_channel.send(response)
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
        
    
    # In Text channels (Restricted by Channel ID) process bot commands  

    if is_text_channel:   
            await bot.process_commands(message)

# Run the bot

bot.run(token)