import discord
from discord.ext import commands
from discord import app_commands

class DeleteMessageOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcedeletemessage", description="[OWNER] Force delete messages from any channel")
    @app_commands.describe(
        position="Which message to delete (1 = most recent)",
        channel="Channel to delete from (defaults to current)"
    )
    @commands.is_owner()
    async def forcedeletemessage(self, ctx, position: int, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT message_id FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
                ORDER BY deleted_at DESC
                LIMIT 1 OFFSET ?
            """, (target_channel.guild.id, target_channel.id, position-1))
            message = await cursor.fetchone()

            if not message:
                return await ctx.send(f"No message found at position {position} in {target_channel.mention}")

            await cursor.execute("""
                DELETE FROM deleted_messages
                WHERE message_id = ?
            """, (message[0],))
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            description=f"☢️ Force-deleted message at position {position} in {target_channel.mention}",
            color=0xDD5F53
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DeleteMessageOwner(bot))