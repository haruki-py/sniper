import discord
from discord.ext import commands
from discord import app_commands

class ClearChannelOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forceclearchannel", description="[OWNER] Force clear channel data")
    @commands.is_owner()
    async def forceclearchannel(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
            """, (target_channel.guild.id, target_channel.id))
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            description=f"☢️ Force-cleared snipe data for {target_channel.mention}",
            color=0xDD5F53
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ClearChannelOwner(bot))