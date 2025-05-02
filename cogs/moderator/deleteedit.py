import discord
from discord.ext import commands

class DeleteEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="deleteedit", description="[MOD] Delete specific edit record")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(index="Which edit to delete (1=most recent)")
    async def deleteedit(self, ctx, index: int):
        if ctx.guild.id not in self.bot.edits or ctx.channel.id not in self.bot.edits[ctx.guild.id]:
            return await ctx.send("No edit history found", ephemeral=True)
            
        edits = self.bot.edits[ctx.guild.id][ctx.channel.id]
        if index < 1 or index > len(edits):
            return await ctx.send("Invalid edit position", ephemeral=True)
            
        edits.pop(-index)
        await ctx.send(f"Deleted edit record #{index}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeleteEdit(bot))