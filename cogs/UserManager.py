import discord
from discord import app_commands
from discord.ext import commands
import datetime

class UserManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="踢出", description="踢出指定用戶")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await member.kick
        await interaction.response.send_message(f"已成功踢出 {member.mention} ", ephemeral=True)

    @app_commands.command(name="停權", description="停權指定用戶")
    @app_commands.default_permissions(kick_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await member.ban
        await interaction.response.send_message(f"已成功停權 {member.mention}", ephemeral=True)


    @app_commands.command(name="禁言", description="禁言指定成員")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, 秒數: int):
        # 轉換秒數為時間差物件
        timeout_duration = datetime.timedelta(seconds=秒數)
        
        # 檢查時間限制 (Discord 最長禁言時間為 28 天)
        max_seconds = 28 * 24 * 60 * 60  # 28天的秒數
        if 秒數 > max_seconds:
            await interaction.response.send_message(
                f"禁言時間不能超過 28 天 ({max_seconds} 秒)",ephemeral=True)
            return
            
        # 執行禁言
        await member.timeout(timeout_duration)
        
        # 計算解除時間
        end_time = int((datetime.datetime.now() + timeout_duration).timestamp())

        await interaction.response.send_message(f"已成功禁言 {member.mention} 至 <t:{end_time}:F>", ephemeral=True)

    @app_commands.command(name="解除停權", description="解除停權指定用戶")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"已成功解除 {user.mention} 停權", ephemeral=True)

    @app_commands.command(name="解除禁言", description="解除禁言指定用戶")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)  # 設置為 None 來解除禁言
        await interaction.response.send_message(f"已成功解除 {member.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserManager(bot))