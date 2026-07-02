import discord
from discord.ext import commands
from services.openai_service import generate_response, change_model, get_model_list, get_usage, edit_usage
from services.file_service import save_attachment
from memory.memory_manager import MemoryManager
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback

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

  @commands.command(name="토큰사용량")
  async def token_usage(self, ctx):
    await ctx.reply(f"현재까지 토큰 사용량은 ${get_usage()} 입니다.")

  @commands.command(name="사용량수정")
  async def edit_total_usage(self, ctx, usage):
    res = edit_usage(usage)
    await ctx.reply(res)

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

    uploaded_files = []

    for attachment in message.attachments:
        try:
            path = await save_attachment(attachment)
            uploaded_files.append(path)
            print(f"Saved attachment: {path}")
        except Exception:
            traceback.print_exc()

    # 모델에게 업로드된 파일명을 알려준다.
    if uploaded_files:
        prompt += "\n\n업로드된 파일 목록입니다.\n"
        prompt += "필요하면 read_file 도구를 사용하여 내용을 읽으세요.\n\n"

        for path in uploaded_files:
            prompt += f"- {path.name}\n"

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
        try:
            result = await generate_response(history)
        except Exception:
            traceback.print_exc()
            await message.reply("응답 생성 중 오류가 발생했습니다.")
            return

    try:
        files = []

        for path in result["files"]:
            files.append(discord.File(path))

        await message.reply(
            result["message"][:1900],
            files=files if files else None
        )

    except Exception:
        traceback.print_exc()

    memory.add_message(
        guild_id=message.guild.id,
        channel_id=message.channel.id,
        role="assistant",
        content=result["message"]
    )

    channel = self.bot.get_channel(1521059636751368322)

    if channel is not None:
        now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

        await channel.send(
            f"**지금까지 사용한 비용은 ${get_usage()}입니다.**\n"
            f"응답시간: `{now}`"
        )

async def setup(bot):
  await bot.add_cog(AI(bot))