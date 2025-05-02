import discord
from discord.ext import commands

class ClearEditServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="cleareditserver", description="[MOD] Clear all edit history for this server")
    @commands.has_permissions(administrator=True)
    async def cleareditserver(self, ctx):
        if ctx.guild.id in self.bot.edits:
            self.bot.edits.pop(ctx.guild.id)
            await ctx.send("✅ Cleared all edit history for this server", ephemeral=True)
        else:
            await ctx.send("No edit history found for this server", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearEditServer(bot))