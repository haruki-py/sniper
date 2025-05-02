import discord
from discord.ext import commands
from discord import app_commands

class DeleteMessageMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="deletemessage", description="[MOD] Delete a specific message from snipe history")
    @app_commands.describe(position="Which message to delete (1 = most recent)")
    @commands.has_permissions(manage_messages=True)
    async def deletemessage(self, ctx, position: int):
        if position < 1:
            return await ctx.send("Position must be at least 1", ephemeral=True)

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT message_id FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
                ORDER BY deleted_at DESC
                LIMIT 1 OFFSET ?
            """, (ctx.guild.id, ctx.channel.id, position-1))
            message = await cursor.fetchone()

            if not message:
                return await ctx.send("No message found at that position", ephemeral=True)

            await cursor.execute("""
                DELETE FROM deleted_messages
                WHERE message_id = ?
            """, (message[0],))
            await self.bot.db_pool.commit()

        await ctx.send(f"Deleted message at position {position}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeleteMessageMod(bot))