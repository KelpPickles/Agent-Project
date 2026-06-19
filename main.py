import discord
from discord.ext import commands
import asyncio
from services.openai_service import get_model

from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료")
    try:
        result = get_model()
        await bot.change_presence(
            activity=discord.Game(name=f"{result['model_name']} 사용 중 {result['model_price']}")
        )
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