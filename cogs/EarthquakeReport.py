# bot.py
import json
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from datetime import datetime

class EarthquakeReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 讀取配置文件
        with open('configs/eqr.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
    async def fetch_earthquake_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_all_reports(self):
        local_url = self.config['EarthquakeReports']['Local'][0]['Link']
        no_url = self.config['EarthquakeReports']['No'][0]['Link']

        # 獲取兩種地震報告
        local_data = await self.fetch_earthquake_data(local_url)
        no_data = await self.fetch_earthquake_data(no_url)

        all_reports = []
        
        # 處理小區域地震報告
        if local_data and 'records' in local_data:
            for record in local_data['records']['Earthquake']:  # 修改這裡
                try:
                    time = datetime.strptime(record['EarthquakeInfo']['OriginTime'], '%Y-%m-%d %H:%M:%S')
                    report = {
                        'type': '小區域地震',
                        'time': int(time.timestamp()),
                        'ReportContent': record['ReportContent'],
                        'Image': record['ReportImageURI'],
                        'OriginTime': record['EarthquakeInfo']['OriginTime']
                    }
                    all_reports.append(report)
                except (KeyError, IndexError) as e:
                    print(f"處理小區域地震資料時發生錯誤: {e}")
                    continue

        # 處理顯著有感地震報告
        if no_data and 'records' in no_data:
            for record in no_data['records']['Earthquake']:  # 修改這裡
                try:
                    time = datetime.strptime(record['EarthquakeInfo']['OriginTime'], '%Y-%m-%d %H:%M:%S')
                    report = {
                        'type': '顯著有感地震',
                        'time': int(time.timestamp()),
                        'No': record['EarthquakeNo'],
                        'ReportContent': record['ReportContent'],
                        'Image': record['ReportImageURI'],
                        'OriginTime': record['EarthquakeInfo']['OriginTime']
                    }
                    all_reports.append(report)
                except (KeyError, IndexError) as e:
                    print(f"處理顯著有感地震資料時發生錯誤: {e}")
                    continue

        # 依時間排序
        all_reports.sort(key=lambda x: x['time'], reverse=True)
        return all_reports[:6]  # 返回最新的6筆資料

    def create_report_embed(self, report):
        embed = discord.Embed(
            title=f"編號{report['No']}有感地震報告" if report['type'] == '顯著有感地震' else f"小區域有感地震報告",
            description=f"{report['ReportContent']}",
            color=discord.Color.red() if report['type'] == '顯著有感地震' else discord.Color.green()
        )
        embed.set_image(url=f"{report['Image']}")


        
        return embed

    @app_commands.command(name="地震報告", description="查看最新地震報告")
    async def earthquake_report(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            reports = await self.get_all_reports()
            if not reports:
                await interaction.followup.send("目前無法取得地震報告資料。")
                return

            # 準備最新的地震報告
            latest_report = reports[0]
            latest_embed = self.create_report_embed(latest_report)

            # 準備剩餘報告的選項
            remaining_reports = reports[1:]
            if remaining_reports:
                # 建立選項列表
                options = []
                for i, report in enumerate(remaining_reports):
                    label = f"編號{report['No']}有感地震報告" if report['type'] == '顯著有感地震' else f"小區域有感地震報告"
                    description = f"時間: {report['OriginTime']}"
                    options.append(discord.SelectOption(
                        label=label[:100],
                        description=description[:100],
                        value=str(i)
                    ))

                # 建立下拉選單
                select = discord.ui.Select(
                    placeholder="選擇要查看較早的地震報告",
                    options=options
                )

                # 建立自定義視圖類別，包含超時處理
                class TimeoutView(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=120)
                    
                    async def on_timeout(self):
                        for item in self.children:
                            item.disabled = True
                        try:
                            await self.message.edit(content="⚠️ 選單已超時，請重新使用指令查看報告", view=self)
                        except:
                            pass

                # 建立視圖
                view = TimeoutView()
                view.add_item(select)

                # 定義選單回調
                async def select_callback(interaction: discord.Interaction):
                    selected_index = int(interaction.data['values'][0])
                    selected_report = remaining_reports[selected_index]
                    embed = self.create_report_embed(selected_report)
                    await interaction.response.send_message(embed=embed, ephemeral=True)

                select.callback = select_callback

                # 發送包含最新報告和選單的單一訊息
                message = await interaction.followup.send(
                    embed=latest_embed,
                    view=view
                )
                view.message = message

            else:
                # 如果只有最新報告，就只發送最新報告
                await interaction.followup.send(
                    embed=latest_embed
                )

        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{str(e)}")

#https://scweb.cwa.gov.tw/webdata/OLDEQ/202411/2024111217142036_H.png
#https://scweb.cwa.gov.tw/webdata/OLDEQ/202411/2024110919420844491_H.png

async def setup(bot):
    await bot.add_cog(EarthquakeReport(bot))