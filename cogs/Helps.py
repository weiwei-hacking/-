import discord
from discord import app_commands
from discord.ext import commands

class Helps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="幫助", description="顯示機器人資訊")
    async def help(self, interaction: discord.Interaction):

        await interaction.response.send_message("機器人指令列表 <https://github.com/weiwei-hacking/EssentialBot/blob/main/%E6%8C%87%E4%BB%A4%E5%88%97%E8%A1%A8>\n機器人開源地址 <https://github.com/weiwei-hacking/EssentialBot>\n需要幫助? https://discord.gg/dG258KRXUX", ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Helps(bot))