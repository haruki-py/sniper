import discord
from discord.ext import commands
from discord import app_commands

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="prefix", description="Change the bot's prefix for this server")
    @app_commands.describe(new_prefix="The new prefix to use (max 5 characters)")
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, new_prefix: str):
        if len(new_prefix) > 5:
            return await ctx.send("Prefix must be 5 characters or less.")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO guild_prefixes (guild_id, prefix)
                VALUES (?, ?)
            """, (ctx.guild.id, new_prefix))
            await self.bot.db_pool.commit()

        embed = discord.Embed(
            title="Prefix Changed",
            description=f"The prefix has been changed to `{new_prefix}`",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Prefix(bot))