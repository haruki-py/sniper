import discord
from discord.ext import commands

class DeleteEditOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcedeleteedit", description="[OWNER] Delete specific edit from any channel")
    @commands.is_owner()
    @app_commands.describe(
        edit_id="Edit ID to delete",
        channel="Channel to target"
    )
    async def forcedeleteedit(self, ctx, edit_id: int, channel: discord.TextChannel = None):
        target = channel or ctx.channel

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM edited_messages
                WHERE edit_id = ? AND guild_id = ? AND channel_id = ?
            """, (edit_id, target.guild.id, target.id))
            
            if cursor.rowcount == 0:
                return await ctx.send("❌ No edit found with that ID")
            
            await self.bot.db_pool.commit()

        await ctx.send(f"🗑️ Force-deleted edit #{edit_id} from {target.mention}")

async def setup(bot):
    await bot.add_cog(DeleteEditOwner(bot))