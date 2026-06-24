import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
from services.openai_service import get_model

from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

STARTUP = False
DEVELOP_MODE = True

@bot.event
async def on_ready():
    global STARTUP
    print(f"{bot.user} 로그인 완료.")
    try:
        result = get_model()
        await bot.change_presence(
            activity=discord.Game(name=f"{result['model_name']} 사용 중 {result['model_price']}")
        )

        if STARTUP: 
            return
    
        STARTUP = True
        
        channel = bot.get_channel(1518148680098648184)

        if DEVELOP_MODE:
            now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            await channel.send(f"@everyone\n"
                            f"**{bot.user}가 배포되었으나 개발모드입니다.**\n"
                            f"배포 시간: `{now}`",
                            allowed_mentions=discord.AllowedMentions(everyone=True))
            await bot.close()
            return

        if channel is not None:
            now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            await channel.send(f"@everyone\n"
                            f"**{bot.user}가 정상적으로 시작되었습니다.**\n"
                            f"배포 시간: `{now}`",
                            allowed_mentions=discord.AllowedMentions(everyone=True))

    except Exception as e:
        print(e)

async def load_cogs():
    await bot.load_extension("cogs.ping")
    await bot.load_extension("cogs.ai")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


asyncio.run(main())