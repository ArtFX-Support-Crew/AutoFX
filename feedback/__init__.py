from .feedback import Feedback

async def setup(bot):
    bot.add_cog(Feedback(bot))