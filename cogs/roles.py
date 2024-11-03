import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from typing import List, Tuple, Optional

class RoleManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    def create_progress_embed(self, 
                            last_5_logs: List[Tuple[str, bool]], 
                            total_members: int,
                            success_count: int,
                            fail_count: int,
                            skip_count: int = 0) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.green())
        
        if last_5_logs:
            log_text = "```ansi\n"
            for user_name, success in last_5_logs:
                if success is None:
                    log_text += f"[1;2m[1;33m {user_name} 已跳過[0m[0m\n"
                elif success:
                    log_text += f"[1;2m[1;34m {user_name} 執行成功[0m[0m\n"
                else:
                    log_text += f"[1;2m[1;31m[1;31m {user_name} 執行失敗[0m[1;31m[0m[0m\n"
            log_text += "```"
            embed.add_field(name="執行記錄", value=log_text, inline=False)
        
        embed.add_field(name="運行成功數", value=f"```{success_count}/{total_members}```", inline=True)
        embed.add_field(name="失敗成功數", value=f"```{fail_count}/{total_members}```", inline=True)
        if skip_count > 0:
            embed.add_field(name="跳過數量", value=f"```{skip_count}/{total_members}```", inline=True)

        return embed

    def should_skip_member(self, 
                          member: discord.Member, 
                          exception_roles: List[discord.Role],
                          exclude_bots: bool) -> bool:
        """檢查是否應該跳過該成員"""
        # 檢查是否為機器人且需要排除機器人
        if exclude_bots and member.bot:
            return True
            
        # 檢查是否擁有例外身分組
        if any(role in member.roles for role in exception_roles):
            return True
            
        return False

    身分組 = app_commands.Group(name="身分組", description="身分組管理相關指令")

    @身分組.command(name="新增全部", description="為所有成員添加指定身分組")
    @app_commands.default_permissions(administrator=True)
    async def add_all(self, 
                     interaction: discord.Interaction, 
                     role: discord.Role,
                     例外身分組: Optional[discord.Role] = None,
                     例外機器人: Optional[bool] = False):
        await interaction.response.defer()
        
        # 收集所有非None的例外身分組
        例外身分組 = [role for role in [例外身分組] if role is not None]
        
        last_5_logs: List[Tuple[str, bool]] = []
        success_count = 0
        fail_count = 0
        skip_count = 0
        total_members = len(interaction.guild.members)
        
        progress_message = await interaction.followup.send(
            embed=self.create_progress_embed(last_5_logs, total_members, success_count, fail_count, skip_count)
        )
        
        for member in interaction.guild.members:
            # 檢查是否需要跳過該成員
            if self.should_skip_member(member, 例外身分組, 例外機器人):
                skip_count += 1
                last_5_logs.append((str(member), None))  # None 表示跳過
                continue

            try:
                if role not in member.roles:
                    await member.add_roles(role)
                    success_count += 1
                    last_5_logs.append((str(member), True))
                else:
                    continue
            except discord.HTTPException:
                fail_count += 1
                last_5_logs.append((str(member), False))
            
            if len(last_5_logs) > 5:
                last_5_logs.pop(0)
            
            try:
                await progress_message.edit(
                    embed=self.create_progress_embed(
                        last_5_logs, total_members, success_count, fail_count, skip_count
                    )
                )
            except discord.HTTPException:
                await asyncio.sleep(1)
        
        final_embed = self.create_progress_embed(
            last_5_logs, total_members, success_count, fail_count, skip_count
        )
        
        # 構建例外訊息
        exception_msg = ""
        if 例外身分組:
            exception_msg += f"\n已排除的身分組: {', '.join(role.mention for role in 例外身分組)}"
        if 例外機器人:
            exception_msg += "\n已排除機器人"
            
        final_embed.add_field(
            name="指令執行結束", 
            value=f"已將身分組 {role.mention} 添加至 {success_count} 個用戶!{exception_msg}", 
            inline=False
        )
        await progress_message.edit(embed=final_embed)

    @身分組.command(name="移除全部", description="移除所有成員的指定身分組")
    @app_commands.default_permissions(administrator=True)
    async def remove_all(self, 
                        interaction: discord.Interaction, 
                        role: discord.Role,
                        例外身分組: Optional[discord.Role] = None,
                        例外機器人: Optional[bool] = False):
        await interaction.response.defer()
        
        # 收集所有非None的例外身分組
        例外身分組 = [role for role in [例外身分組] if role is not None]
        
        last_5_logs: List[Tuple[str, bool]] = []
        success_count = 0
        fail_count = 0
        skip_count = 0
        total_members = len(interaction.guild.members)
        
        progress_message = await interaction.followup.send(
            embed=self.create_progress_embed(last_5_logs, total_members, success_count, fail_count, skip_count)
        )
        
        for member in interaction.guild.members:
            # 檢查是否需要跳過該成員
            if self.should_skip_member(member, 例外身分組, 例外機器人):
                skip_count += 1
                last_5_logs.append((str(member), None))  # None 表示跳過
                continue

            try:
                if role in member.roles:
                    await member.remove_roles(role)
                    success_count += 1
                    last_5_logs.append((str(member), True))
                else:
                    continue
            except discord.HTTPException:
                fail_count += 1
                last_5_logs.append((str(member), False))
            
            if len(last_5_logs) > 5:
                last_5_logs.pop(0)
            
            try:
                await progress_message.edit(
                    embed=self.create_progress_embed(
                        last_5_logs, total_members, success_count, fail_count, skip_count
                    )
                )
            except discord.HTTPException:
                await asyncio.sleep(1)
        
        final_embed = self.create_progress_embed(
            last_5_logs, total_members, success_count, fail_count, skip_count
        )
        
        # 構建例外訊息
        exception_msg = ""
        if 例外身分組:
            exception_msg += f"\n已排除的身分組: {', '.join(role.mention for role in 例外身分組)}"
        if 例外機器人:
            exception_msg += "\n已排除機器人"
            
        final_embed.add_field(
            name="指令執行結束", 
            value=f"已將身分組 {role.mention} 移除至 {success_count} 個用戶!{exception_msg}", 
            inline=False
        )
        await progress_message.edit(embed=final_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleManager(bot))
