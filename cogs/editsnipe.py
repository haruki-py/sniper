import discord
from discord.ext import commands
from discord import app_commands
import datetime

class EditSnipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.edits = {}

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot:
            return
        
        guild_id = before.guild.id
        channel_id = before.channel.id
        
        if guild_id not in self.edits:
            self.edits[guild_id] = {}
        if channel_id not in self.edits[guild_id]:
            self.edits[guild_id][channel_id] = []
            
        self.edits[guild_id][channel_id].append({
            "before": before.content,
            "after": after.content,
            "author": before.author,
            "edited_at": datetime.datetime.now(),
            "jump_url": after.jump_url
        })
        
        if len(self.edits[guild_id][channel_id]) > 100:
            self.edits[guild_id][channel_id].pop(0)

    @commands.hybrid_command(name="editsnipe", description="View recent message edits in this channel")
    @app_commands.describe(index="Which edit to view (1 = most recent)")
    async def editsnipe(self, ctx, index: int = 1):
        if not ctx.guild:
            return await ctx.send("This only works in servers", ephemeral=True)
            
        edits = self.edits.get(ctx.guild.id, {}).get(ctx.channel.id, [])
        
        if not edits:
            return await ctx.send("No edited messages found here", ephemeral=True)
            
        index = max(1, min(index, len(edits)))
        edit = edits[-index]
        
        embed = discord.Embed(
            title=f"Message Edit #{index}",
            description=f"[Jump to Message]({edit['jump_url']})",
            color=0xF5A623,
            timestamp=edit['edited_at']
        )
        embed.add_field(name="Before", value=edit['before'] or "*No content*", inline=False)
        embed.add_field(name="After", value=edit['after'] or "*No content*", inline=False)
        embed.set_author(
            name=f"{edit['author'].name}#{edit['author'].discriminator}",
            icon_url=edit['author'].avatar.url if edit['author'].avatar else None
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EditSnipe(bot))