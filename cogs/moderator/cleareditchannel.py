import discord
from discord.ext import commands

class ClearEditChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="cleareditchannel", description="[MOD] Clear edit history for this channel")
    @commands.has_permissions(manage_messages=True)
    async def cleareditchannel(self, ctx):
        if ctx.guild.id in self.bot.edits and ctx.channel.id in self.bot.edits[ctx.guild.id]:
            self.bot.edits[ctx.guild.id].pop(ctx.channel.id)
            await ctx.send("✅ Cleared edit history for this channel", ephemeral=True)
        else:
            await ctx.send("No edit history found for this channel", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearEditChannel(bot))