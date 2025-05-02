import discord
from discord.ext import commands
from discord import app_commands

class ClearServerOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clearserver", description="[OWNER] Wipe ALL data for any server")
    @commands.is_owner()
    @app_commands.describe(guild_id="Target server ID")
    async def clearserver(self, ctx, guild_id: str):
        try:
            guild = self.bot.get_guild(int(guild_id))
            guild_name = guild.name if guild else f"UNKNOWN_SERVER ({guild_id})"
        except ValueError:
            return await ctx.send("❌ Invalid server ID format")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("DELETE FROM deleted_messages WHERE guild_id = ?", (guild_id,))
            await cursor.execute("DELETE FROM guild_prefixes WHERE guild_id = ?", (guild_id,))
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            title="☢️ OWNER DATA WIPE",
            description=f"Force-wiped ALL data for:\n**{guild_name}**",
            color=0xFF5555
        )
        embed.set_footer(text=f"Executed by {ctx.author}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ClearServerOwner(bot))