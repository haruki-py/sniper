import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Show all available commands")
    async def help(self, ctx):
        prefix = await self.bot.get_prefix(ctx.message) if ctx.prefix else "/"
        
        embed = discord.Embed(
            title="Message Sniper Bot Help",
            description="Track and recover deleted messages",
            color=0x5865F2
        )
        
        commands_list = [
            f"`{prefix}prefix <new_prefix>` - Change bot prefix",
            f"`{prefix}snipe [index]` - View deleted messages",
            f"`{prefix}snipeall` - Export all deleted messages",
            f"`{prefix}help` - Show this message"
        ]
        
        embed.add_field(
            name="Available Commands", 
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.set_footer(text=f"Use {prefix}command or /command")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))