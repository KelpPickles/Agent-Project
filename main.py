import discord
from discord.ext import commands
import asyncio

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


async def load_cogs():
    await bot.load_extension("cogs.ping")
    await bot.load_extension("cogs.ai")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


asyncio.run(main())