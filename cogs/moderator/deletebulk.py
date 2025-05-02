import discord
from discord.ext import commands
from discord import app_commands

class DeleteBulkMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="deletebulk", description="[MOD] Delete multiple recent messages from this channel")
    @app_commands.describe(count="Number of recent messages to delete (max 25)")
    @commands.has_permissions(manage_messages=True)
    async def deletebulk(self, ctx, count: int):
        if count < 1:
            return await ctx.send("❌ Count must be at least 1", ephemeral=True)
        if count > 25:
            return await ctx.send("❌ Maximum 25 messages at once", ephemeral=True)

        confirm = discord.ui.View()
        confirm.add_item(discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label=f"DELETE LAST {count} MESSAGES",
            custom_id="confirm_bulk_delete"
        ))

        embed = discord.Embed(
            title="⚠️ BULK DELETE CONFIRMATION",
            description=f"You are about to delete the last **{count}** deleted messages in {ctx.channel.mention}",
            color=0xFFA500
        )
        msg = await ctx.send(embed=embed, view=confirm, ephemeral=True)

        try:
            interaction = await self.bot.wait_for(
                "interaction",
                check=lambda i: i.data.get("custom_id") == "confirm_bulk_delete" and i.user.id == ctx.author.id,
                timeout=30
            )
        except TimeoutError:
            return await msg.edit(content="⌛ Action cancelled", embed=None, view=None)

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
            """, (ctx.guild.id, ctx.channel.id, count))
            deleted = cursor.rowcount
            await self.bot.db_pool.commit()

        await interaction.response.edit_message(
            embed=discord.Embed(
                description=f"✅ Deleted last {deleted} messages from history",
                color=0x55FF55
            ),
            view=None
        )

async def setup(bot):
    await bot.add_cog(DeleteBulkMod(bot))