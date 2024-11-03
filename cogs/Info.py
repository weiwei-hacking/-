import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    資訊 = app_commands.Group(name="資訊", description="資訊相關指令")


    @資訊.command(name="用戶", description="顯示用戶資訊")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user

        joined_at = int(member.joined_at.timestamp()) if member.joined_at else None
        created_at = int(member.created_at.timestamp())
        
        embed = discord.Embed(title="用戶資訊", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="用戶名稱", value=str(member), inline=True)
        embed.add_field(name="用戶ID", value=member.id, inline=True)
        
        embed.add_field(name="帳戶創建時間", value=f"<t:{created_at}:F>", inline=False)
        if joined_at:
            embed.add_field(name="用戶加入時間", value=f"<t:{joined_at}:F>", inline=True)
            
        try:
            req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=member.id))
            banner_id = req["banner"]
            if banner_id:
                banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}?size=1024"
                embed.set_image(url=banner_url)
        except Exception as e:
            return

        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @資訊.command(name="伺服器", description="顯示伺服器資訊")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # 統計資訊
        total_members = guild.member_count
        
        # 創建 Embed
        embed = discord.Embed(title=f"伺服器資訊", color=discord.Color.green())
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # 基本資訊
        embed.add_field(name="伺服器名稱", value=guild.name, inline=True)
        embed.add_field(name="伺服器ID", value=guild.id, inline=True)
        embed.add_field(name="建立時間", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="擁有者", value=guild.owner.mention, inline=True)
        embed.add_field(name="總成員數", value=total_members, inline=True)
        embed.add_field(name="加成等級", value=f"Level {guild.premium_tier}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))