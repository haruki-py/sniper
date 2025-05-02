import discord
from discord.ext import commands
import os
from datetime import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return
        
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO deleted_messages (
                    message_id, guild_id, channel_id, author_id, author_name,
                    author_discriminator, author_avatar, content, created_at,
                    deleted_at, reference_id, is_bot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.id, message.guild.id, message.channel.id, message.author.id,
                message.author.name, message.author.discriminator,
                str(message.author.avatar.url) if message.author.avatar else None,
                message.content, message.created_at, datetime.now(),
                message.reference.message_id if message.reference else None,
                message.author.bot
            ))
            
            for attachment in message.attachments:
                attachment_dir = f"attachments/{message.guild.id}/{message.channel.id}"
                os.makedirs(attachment_dir, exist_ok=True)
                local_path = f"{attachment_dir}/{attachment.id}_{attachment.filename}"
                await attachment.save(local_path)
                
                await cursor.execute("""
                    INSERT INTO message_attachments (
                        message_id, filename, url, proxy_url, size,
                        content_type, local_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id, attachment.filename, attachment.url,
                    attachment.proxy_url, attachment.size,
                    attachment.content_type, local_path
                ))
            
            await self.bot.db_pool.commit()

async def setup(bot):
    await bot.add_cog(Events(bot))