import discord
from discord.ext import commands

class ClearEditChannelOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcecleareditchannel", description="[OWNER] Wipe edit history from any channel")
    @commands.is_owner()
    @app_commands.describe(channel="Channel to clear")
    async def forcecleareditchannel(self, ctx, channel: discord.TextChannel):
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM edited_messages
                WHERE guild_id = ? AND channel_id = ?
            """, (channel.guild.id, channel.id))
            await self.bot.db_pool.commit()

        await ctx.send(f"🧹 Force-cleared edit history in {channel.mention}")

async def setup(bot):
    await bot.add_cog(ClearEditChannelOwner(bot))