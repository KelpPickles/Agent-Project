import discord
from discord.ext import commands
from services.openai_service import generate_response, change_model, get_model_list
from memory.memory_manager import MemoryManager

memory = MemoryManager()

class AI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="모델변경")
  async def change_model(self, ctx, model_name: str):
    result = change_model(model_name)

    if result['status']:
      await ctx.reply(f"✅ 모델이 {result['model_name']}으로 변경되었습니다.")
      await self.bot.change_presence(
        activity=discord.Game(name=f"{result['model_name']} 사용 중 {result['model_price']}")
      )
    else:
      await ctx.reply(f"❌ 모델 {result['model_name']}을(를) 찾을 수 없습니다.")
  
  @commands.command(name="모델목록")
  async def list_model(self, ctx):
    await ctx.reply(get_model_list())

  @commands.command(name="기록삭제")
  async def clear_memory(self, ctx):
    memory.clear_channel(ctx.guild.id, ctx.channel.id)
    await ctx.reply(f"({ctx.guild.id}, {ctx.channel.id})에 대한 기록 삭제를 요청했어요!")

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