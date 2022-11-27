import discord 
from redbot.core import commands
from redbot.core import Config, config, checks 
import random
import time
from typing import Literal
import asyncio
from redbot.core.utils.chat_formatting import (bold, box, humanize_list, humanize_number, pagify)
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.predicates import MessagePredicate

class Feedback(commands.Cog):
    """Track Feedback Management Cog. Recognize track feedback requests, and reward members for providing meaningful feedback."""

    def __init__(self, bot):
        """Function that initializes the cog.
        """
        self.bot = bot
        self.config = Config.get_conf(self, 234256122784481002, force_registration=True)
        

        # Registering the default values for the server bot
        default_guild = {
                    "feedback_min_length": 148, #minimum length to qualify as feedback
                    "react_to_award": True, #admin reacts to award
                    "word_to_award": True, #admin writes to award
                    "channels": [], #channels where feedback will be listening
                    "feedback_reward": True #Turn feedback rewards on or off
                    } 

        default_global = {
                    "feedback_enabled": True #enable feedback by default
                    }
# Registering the default values for the config.
        default_user = {"tokens": 0}
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

    @commands.guild_only()
    @commands.group()
    async def feedback(self, ctx):
        """Admin functions for Feedback."""
        # Reward tokens or adjust module settings
        if ctx.invoked_subcommand is None:
            guild_data = await self.config.guild(ctx.guild).all()
        if not guild_data["channels"]:
            channel_names = ["No channels set."]
        else:
            channel_names = []
            for channel_id in guild_data["channels"]:
                channel_obj = self.bot.get_channel(channel_id)
                if channel_obj:
                    channel_names.append(channel_obj.name)

        feedback_mode_react = "React" if guild_data["react_to_award"] else "Off"
        feedback_mode_words = "Words" if guild_data["word_to_award"] else "Off"
        feedback_reward = "On" if guild_data["feedback_reward"] else "Off"
        feedback_min_length = guild_data["feedback_min_length"]

        msg = f"[Feedback Active in]:                 {humanize_list(channel_names)}\n"
        msg += f"[Feedback Rewards]:               {guild_data['feedback_reward']}\n"
        msg += f"[Feedback Mode React]:      {guild_data['react_to_award']}\n"
        msg += f"[Feedback Mode Words]:      {guild_data['word_to_award']}\n"

        for page in pagify(msg, delims=["\n"]):
            await ctx.send(box(page, lang="ini"))


    @feedback.command()
    async def get_tokens(self, ctx: commands.Context, member: discord.Member = None):
        """Get Balance of Feedback Tokens for a Member."""
        if member:
            if member.id == self.bot.user.id:
                member = ctx.message.author
                bot_msg = [
                    (
                        " The bot doesn't operate with Tokens."
                    ),]
                await ctx.send(f"{ctx.author.mention}{random.choice(bot_msg)}")
            else: 
                user_data = await self.config.user(member).all()
                score = await self.config.user(member).tokens()
                await ctx.send(member.mention +f" has {score} Feedback Tokens.")

    @feedback.command()
    async def award_token(self, ctx: commands.Context, member: discord.Member = None):
        """Award Tokens for Feedback."""
        # Awards default token reward amount to the user config
        # This is checking if the member is the bot. If it is, it will send a message to the user.
        if member:
            if member.id == self.bot.user.id:
                member = ctx.message.author
                bot_msg = [
                    (
                        " You cannot award Tokens to the bot."
                    ),]

                await ctx.send(f"{ctx.author.mention}{random.choice(bot_msg)}")
            else:
                # Adding a token to the user's token count.
                user_data = await self.config.user(member).all()
                user_data["tokens"] += 1
                await self.config.user(member).set_raw(value=user_data)
                await ctx.send(member.mention +"has been awarded a Token for giving Feedback!")
                score = await self.config.user(member).tokens()
                await ctx.send(member.mention +f"now has {score} Tokens.")
                
        else:
            await ctx.send(f'Tokens must be awarded to a user.')
    @checks.mod_or_permissions(manage_guild=True)
    @feedback.command()
    async def start(self, ctx, channel: discord.TextChannel = None):
        """Start AutoFX Feedback"""
        if not channel:
            channel = ctx.channel

        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await ctx.send(bold("I can't send messages in that channel!"))

        channel_list = await self.config.guild(ctx.guild).channels()
        if channel.id in channel_list:
            message = f"AutoFX Feedback already started in {channel.mention}!"
        else:
            channel_list.append(channel.id)
            message = f"AutoFX Feedback started in {channel.mention}. Post your tracks to get feedback!"
            await self.config.guild(ctx.guild).channels.set(channel_list)

        await ctx.send(bold(message))

    @checks.mod_or_permissions(manage_guild=True)
    @feedback.command()
    async def stop(self, ctx, channel: discord.TextChannel = None):
        """Stop AutoFX Feedback."""
        if not channel:
            channel = ctx.channel
        channel_list = await self.config.guild(ctx.guild).channels()

        if channel.id not in channel_list:
            message = f"AutoFX Feedback Disabled in {channel.mention}!"
        else:
            channel_list.remove(channel.id)
            message = f"AutoFX Feedback has been stopped in {channel.mention}."
            await self.config.guild(ctx.guild).channels.set(channel_list)

        await ctx.send(bold(message))

