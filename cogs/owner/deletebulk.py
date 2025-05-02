import discord
from discord.ext import commands
from discord import app_commands

class DeleteBulkOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcedeletebulk", description="[OWNER] Force delete messages from any channel")
    @app_commands.describe(
        count="Number of messages to delete",
        channel="Target channel (defaults to current)"
    )
    @commands.is_owner()
    async def forcedeletebulk(self, ctx, count: int, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        
        if count < 1:
            return await ctx.send("❌ Count must be at least 1")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                WITH targets AS (
                    SELECT message_id FROM deleted_messages
                    WHERE guild_id = ? AND channel_id = ?
                    ORDER BY deleted_at DESC
                    LIMIT ?
                )
                DELETE FROM deleted_messages
                WHERE message_id IN (SELECT message_id FROM targets)
            """, (target_channel.guild.id, target_channel.id, count))
            deleted = cursor.rowcount
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            title="☢️ BULK FORCE DELETE",
            description=f"Deleted last **{deleted}** messages in {target_channel.mention}",
            color=0xDD5F53
        )
        embed.set_footer(text=f"Executed by {ctx.author}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DeleteBulkOwner(bot))