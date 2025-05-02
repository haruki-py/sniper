import discord
from discord.ext import commands
import aiosqlite
import os
from dotenv import load_dotenv

class SnipeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.db_pool = None

    async def setup_hook(self):
        self.db_pool = await aiosqlite.connect('snipe_bot.db')
        await self.init_db()
        await self.load_cogs()
        await self.tree.sync()

    async def init_db(self):
        async with self.db_pool.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_prefixes (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT NOT NULL
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS deleted_messages (
                    message_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    author_name TEXT NOT NULL,
                    author_discriminator TEXT NOT NULL,
                    author_avatar TEXT,
                    content TEXT,
                    created_at TIMESTAMP NOT NULL,
                    deleted_at TIMESTAMP NOT NULL,
                    reference_id INTEGER,
                    is_bot BOOLEAN NOT NULL
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_attachments (
                    attachment_id INTEGER PRIMARY KEY,
                    message_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    url TEXT NOT NULL,
                    proxy_url TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    content_type TEXT,
                    local_path TEXT,
                    FOREIGN KEY (message_id) REFERENCES deleted_messages(message_id)
                )
            """)
            await self.db_pool.commit()

    async def get_prefix(self, message):
        if not message.guild:
            return "!"
        
        async with self.db_pool.cursor() as cursor:
            await cursor.execute(
                "SELECT prefix FROM guild_prefixes WHERE guild_id = ?",
                (message.guild.id,)
            )
            result = await cursor.fetchone()
            
        return result[0] if result else "!"

    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def close(self):
        if self.db_pool:
            await self.db_pool.close()
        await super().close()

bot = SnipeBot()

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Missing DISCORD_TOKEN in environment")