import discord
from discord.ext import commands

class ClearEditServerOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="forcecleareditserver", description="[OWNER] Wipe all edit history from a server")
    @commands.is_owner()
    @app_commands.describe(guild_id="Server ID to clear")
    async def forcecleareditserver(self, ctx, guild_id: str):
        try:
            guild = self.bot.get_guild(int(guild_id))
            name = guild.name if guild else f"Unknown Server ({guild_id})"
        except ValueError:
            return await ctx.send("❌ Invalid server ID")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("DELETE FROM edited_messages WHERE guild_id = ?", (guild_id,))
            await self.bot.db_pool.commit()

        await ctx.send(f"☢️ Force-wiped all edit history for {name}")

async def setup(bot):
    await bot.add_cog(ClearEditServerOwner(bot))