import discord
from discord import app_commands
from discord.ext import commands

class OtherAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="重建", description="重建當前頻道")
    @app_commands.default_permissions(manage_channels=True)
    async def recreate_channel(self, interaction: discord.Interaction):
        # 保存原始頻道的設置
        original_channel = interaction.channel
        category = original_channel.category
        position = original_channel.position
        permissions = original_channel.overwrites
        name = original_channel.name
        topic = getattr(original_channel, 'topic', None)
        slowmode_delay = getattr(original_channel, 'slowmode_delay', 0)
        nsfw = getattr(original_channel, 'nsfw', False)
        
        # 先回應交互
        await interaction.response.send_message("正在重建頻道...", ephemeral=True)
        
        # 刪除原始頻道
        await original_channel.delete()
        
        # 創建新頻道
        new_channel = await interaction.guild.create_text_channel(
            name=name,
            category=category,
            position=position,
            topic=topic,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            overwrites=permissions,
        )
        
        await new_channel.send(f"已成功重建頻道")
async def setup(bot):
    await bot.add_cog(OtherAdminCommands(bot))