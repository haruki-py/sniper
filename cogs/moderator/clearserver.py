import discord
from discord.ext import commands
from discord import app_commands

class ClearServerMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clearserver", description="[ADMIN] Wipe ALL snipe data for this server")
    @commands.has_permissions(administrator=True)
    async def clearserver(self, ctx):
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.confirmed = False

            @discord.ui.button(label="CONFIRM WIPE", style=discord.ButtonStyle.danger)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("Only the command author can confirm!", ephemeral=True)
                self.confirmed = True
                self.stop()

        view = ConfirmView()
        
        embed = discord.Embed(
            title="⚠️ SERVER DATA WIPE",
            description="This will permanently delete **ALL** snipe data for:\n"
                      f"**{ctx.guild.name}**\n\n"
                      "This action cannot be undone!",
            color=0xFF5555
        )
        embed.set_footer(text="You have 30 seconds to confirm")
        
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        
        if not view.confirmed:
            return await msg.edit(content="❌ Wipe cancelled", embed=None, view=None)

        async with self.bot.db_pool.cursor() as cursor:
            await cursor.execute("DELETE FROM deleted_messages WHERE guild_id = ?", (ctx.guild.id,))
            await self.bot.db_pool.commit()

        await msg.edit(
            embed=discord.Embed(
                description=f"✅ Successfully wiped ALL snipe data for {ctx.guild.name}",
                color=0x55FF55
            ),
            view=None
        )

async def setup(bot):
    await bot.add_cog(ClearServerMod(bot))