import discord
from discord.ext import commands
from discord import app_commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="snipestats", description="Show statistics about deleted messages")
    async def snipestats(self, ctx):
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT COUNT(*) FROM deleted_messages
                WHERE guild_id = ?
            """, (ctx.guild.id,))
            total_messages = (await cursor.fetchone())[0]

            await cursor.execute("""
                SELECT COUNT(DISTINCT channel_id) FROM deleted_messages
                WHERE guild_id = ?
            """, (ctx.guild.id,))
            channel_count = (await cursor.fetchone())[0]

            await cursor.execute("""
                SELECT author_name, COUNT(*) as count 
                FROM deleted_messages
                WHERE guild_id = ?
                GROUP BY author_id
                ORDER BY count DESC
                LIMIT 5
            """, (ctx.guild.id,))
            top_deleters = await cursor.fetchall()

        embed = discord.Embed(
            title="Snipe Statistics",
            description="Statistics about deleted messages in this server",
            color=0x5865F2
        )
        embed.add_field(name="Total Deleted Messages", value=str(total_messages), inline=True)
        embed.add_field(name="Channels Tracked", value=str(channel_count), inline=True)
        
        if top_deleters:
            deleters_text = "\n".join(f"▸ {name}: {count} messages" for name, count in top_deleters)
            embed.add_field(name="Top Deleters", value=deleters_text, inline=False)

        embed.set_footer(text="These stats are server-wide")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))