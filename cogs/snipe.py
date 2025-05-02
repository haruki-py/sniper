import discord
from discord.ext import commands
from discord import app_commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="snipe", description="View deleted messages in this channel")
    @app_commands.describe(index="Which deleted message to view (1 = most recent)")
    async def snipe(self, ctx, index: int = 1):
        if not ctx.guild:
            return await ctx.send("This command only works in servers.")

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT COUNT(*) FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
            """, (ctx.guild.id, ctx.channel.id))
            total = (await cursor.fetchone())[0]
            
            if total == 0:
                return await ctx.send("No deleted messages here.")
            
            index = max(1, min(index, total))
            
            await cursor.execute("""
                SELECT * FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
                ORDER BY deleted_at DESC
                LIMIT 1 OFFSET ?
            """, (ctx.guild.id, ctx.channel.id, index - 1))
            message = await cursor.fetchone()
            
            await cursor.execute("""
                SELECT * FROM message_attachments
                WHERE message_id = ?
            """, (message[0],))
            attachments = await cursor.fetchall()

        embed = discord.Embed(
            description=message[7] or "*No text content*",
            color=0x5865F2,
            timestamp=message[8]
        )
        
        embed.set_author(
            name=f"{message[4]}#{message[5]}",
            icon_url=message[6] or discord.Embed.Empty
        )
        
        embed.set_footer(text=f"Message {index}/{total}")
        
        if attachments:
            attachment_text = "\n".join(f"[{att[2]}]({att[3]})" for att in attachments)
            embed.add_field(name="Attachments", value=attachment_text, inline=False)

        view = SnipeView(self.bot, ctx.guild.id, ctx.channel.id, index, total)
        await ctx.send(embed=embed, view=view)

class SnipeView(discord.ui.View):
    def __init__(self, bot, guild_id, channel_id, current_index, total):
        super().__init__(timeout=60)
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.current_index = current_index
        self.total = total

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction, button):
        if self.current_index > 1:
            self.current_index -= 1
            await self.update(interaction)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        if self.current_index < self.total:
            self.current_index += 1
            await self.update(interaction)

    async def update(self, interaction):
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM deleted_messages
                WHERE guild_id = ? AND channel_id = ?
                ORDER BY deleted_at DESC
                LIMIT 1 OFFSET ?
            """, (self.guild_id, self.channel_id, self.current_index - 1))
            message = await cursor.fetchone()
            
            await cursor.execute("""
                SELECT * FROM message_attachments
                WHERE message_id = ?
            """, (message[0],))
            attachments = await cursor.fetchall()

        embed = discord.Embed(
            description=message[7] or "*No text content*",
            color=0x5865F2,
            timestamp=message[8]
        )
        
        embed.set_author(
            name=f"{message[4]}#{message[5]}",
            icon_url=message[6] or discord.Embed.Empty
        )
        
        embed.set_footer(text=f"Message {self.current_index}/{self.total}")
        
        if attachments:
            attachment_text = "\n".join(f"[{att[2]}]({att[3]})" for att in attachments)
            embed.add_field(name="Attachments", value=attachment_text, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Snipe(bot))