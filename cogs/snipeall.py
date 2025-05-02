import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime
import aiofiles

class SnipeAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="snipeall", description="Export all deleted messages as a JSON file")
    @commands.guild_only()
    async def snipeall(self, ctx):
        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM deleted_messages
                WHERE guild_id = ?
                ORDER BY deleted_at DESC
            """, (ctx.guild.id,))
            messages = await cursor.fetchall()

            if not messages:
                return await ctx.send("No deleted messages to export.")

            export_data = []
            for msg in messages:
                await cursor.execute("""
                    SELECT * FROM message_attachments
                    WHERE message_id = ?
                """, (msg[0],))
                attachments = await cursor.fetchall()

                export_data.append({
                    "id": msg[0],
                    "channel_id": msg[2],
                    "author": {
                        "id": msg[3],
                        "name": msg[4],
                        "discriminator": msg[5],
                        "avatar": msg[6]
                    },
                    "content": msg[7],
                    "created_at": msg[8].isoformat(),
                    "deleted_at": msg[9].isoformat(),
                    "attachments": [
                        {
                            "filename": att[2],
                            "url": att[3],
                            "size": att[5],
                            "type": att[6]
                        } for att in attachments
                    ]
                })

        filename = f"snipe_export_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(export_data, indent=2))

        await ctx.send(file=discord.File(filename))
        
        import os
        os.remove(filename)

async def setup(bot):
    await bot.add_cog(SnipeAll(bot))