import discord
from discord.ext import commands

class DeleteEditBulkOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcedeleteeditbulk", description="[OWNER] Mass delete edits from any channel")
    @commands.is_owner()
    @app_commands.describe(
        count="Number of recent edits to delete",
        channel="Channel to target"
    )
    async def forcedeleteeditbulk(self, ctx, count: int, channel: discord.TextChannel = None):
        target = channel or ctx.channel
        
        if count < 1:
            return await ctx.send("❌ Count must be at least 1")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM edited_messages
                WHERE rowid IN (
                    SELECT rowid FROM edited_messages
                    WHERE guild_id = ? AND channel_id = ?
                    ORDER BY edited_at DESC
                    LIMIT ?
                )
            """, (target.guild.id, target.id, count))
            
            deleted = cursor.rowcount
            await self.bot.db_pool.commit()

        await ctx.send(f"☢️ Force-deleted last {deleted} edits from {target.mention}")

async def setup(bot):
    await bot.add_cog(DeleteEditBulkOwner(bot))