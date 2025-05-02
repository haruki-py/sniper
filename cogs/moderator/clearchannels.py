import discord
from discord.ext import commands
from discord import app_commands

class ClearChannelMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clearchannel", description="[MOD] Clear snipe data for this channel")
    @commands.has_permissions(manage_messages=True)
    async def clearchannel(self, ctx):
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
            """, (ctx.guild.id, ctx.channel.id))
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            description=f"🧹 Cleared snipe data for {ctx.channel.mention}",
            color=0x5865F2
        )
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearChannelMod(bot))