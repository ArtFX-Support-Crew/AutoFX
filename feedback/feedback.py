import discord 
import random
from redbot.core import commands
from redbot.core import Config

class Feedback(commands.Cog):
    """Track Feedback Management Cog. Recognize track feedback requests, and reward members for providing meaningful feedback."""

    def __init__(self, bot):
        self.config = Config.get_conf(self, 2938473984732, force_registration=True)
        self.bot = bot

        default_guild = {
                    "feedback_min_length": 148, #minimum length to qualify as feedback
                    "react_to_award": True, #admin reacts to award
                    "word_to_award": False, #admin writes to award
                    "channels": ['feedback'], #channels where feedback will be listening
                    "feedback_reward": 1
                    } #number of tokens to award 

        default_global = {
                    "feedback_enabled": True #enable feedback by default
                    }
        default_user = {"tokens": 0, "feedbackreceived": 0, "feedbackgiven": 0}
        self.config.register_guild(**default_guild)
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

    @commands.command()
    async def feedback_admin(self, ctx):
        """Admin functions for Feedback."""
        # Reward tokens or adjust module settings
        await ctx.send("Feedback Admin options")

    @commands.command()
    async def award_token(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """Award Tokens for Feedback."""
        # Awards default token reward amount to the user config
        if user:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg = [
                    (
                        " You cannot award tokens to the bot."
                    )
                ]
                await ctx.send(f"{ctx.author.mention}{random.choice(bot_msg)}")
            else:

                user_data = await self.config.user(member).all()
                if not member:
                    member = ctx.author
                user_data["tokens"] + ["feedback_reward"]
                await ctx.send(user.mention +"has been awarded a Token for giving Feedback!")
                score = await self.config.user(member).score()
                await ctx.send(user.mention +f"now has {score} tokens!")

    @commands.command()
    async def token_balance(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """Returns the number of tokens owned by the user."""
        # Awards default token reward amount to the user config
        if user:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg = [
                    (
                        " I do not give feedback, therefore I do not need tokens."
                    ),
                    (
                        " The token_balance must belong to a user, not a bot."
                    )
                ]
                await ctx.send(f"{ctx.author.mention}{random.choice(bot_msg)}")
            else:
                user_data = await self.config.user(member).all()
                if not member:
                    member = ctx.author
                tokens = user_data["tokens"]
                await ctx.send(user.mention(f"has {tokens} feedback tokens remaining."))