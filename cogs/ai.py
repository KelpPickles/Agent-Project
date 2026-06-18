from discord.ext import commands
from services.openai_service import generate_response
from memory.memory_manager import MemoryManager

memory = MemoryManager()

class AI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):

    if message.author.bot:
      return

    if self.bot.user not in message.mentions:
      return

    prompt = (
      message.content
      .replace(f"<@{self.bot.user.id}>", "")
      .strip()
    )

    if not prompt:
      return
    
    print(prompt)

    memory.add_message(
      guild_id=message.guild.id,
      channel_id=message.channel.id,
      role="user",
      content=prompt
    )

    print(f"메모리 저장됨 user: {prompt}")

    history = memory.get_history(
      guild_id=message.guild.id,
      channel_id=message.channel.id,
      limit=20
    )

    print(history)

    async with message.channel.typing():
      response = await generate_response(history)

    await message.reply(response[:1900])

    memory.add_message(
      guild_id=message.guild.id,
      channel_id=message.channel.id,
      role="assistant",
      content=response
    )

async def setup(bot):
  await bot.add_cog(AI(bot))