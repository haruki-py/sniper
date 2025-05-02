import discord
from discord.ext import commands

class DeleteEditBulk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="deleteeditbulk", description="[MOD] Delete multiple edit records")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(count="Number of edits to delete")
    async def deleteeditbulk(self, ctx, count: int):
        if ctx.guild.id not in self.bot.edits or ctx.channel.id not in self.bot.edits[ctx.guild.id]:
            return await ctx.send("No edit history found", ephemeral=True)
            
        edits = self.bot.edits[ctx.guild.id][ctx.channel.id]
        deleted = min(count, len(edits))
        self.bot.edits[ctx.guild.id][ctx.channel.id] = edits[:-deleted] if deleted < len(edits) else []
        
        await ctx.send(f"Deleted last {deleted} edit records", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeleteEditBulk(bot))