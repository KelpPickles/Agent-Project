from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from datetime import datetime
from services.tool_manager import TOOLS
import json

client = AsyncOpenAI(
  api_key=OPENAI_API_KEY
)

TOOLS_SCHEMA = [
  {
    "type": "function",
    "name": "get_current_time",
    "description": "사용자가 현재 시간, 날짜, 오늘이 몇 일인지 물어볼 때 사용한다."
  }
]

SYSTEM_PROMPT = f"""
너는 디스코드 AI 에이전트다.

규칙:
- 함수가 반드시 필요한 경우에만 호출한다.
- 현재 시간을 묻는 질문에만 get_current_time을 사용한다.
- 일반 대화나 자기소개에는 함수를 사용하지 않는다.
"""

async def generate_response(history) -> str:
  messages = [
    {
      "role": "system",
      "content": SYSTEM_PROMPT
    },
    *history
  ]

  response = await client.responses.create(
    model="gpt-4o-mini",
    input=messages,
    tools=TOOLS_SCHEMA
  )

  function_call = None

  for item in response.output:
    print(item)

    if item.type == "function_call":
      function_call = item
      break
  
  if function_call is None:
    return response.output_text
  
  tool_name = function_call.name

  if tool_name not in TOOLS:
    return f"알 수 없는 도구 : {tool_name}"
  
  try:
    arguments = json.loads(function_call.arguments)
  except Exception:
    arguments = {}

  print("Tool Call:", tool_name)
  print("Arguments:", arguments)

  tool_result = TOOLS[tool_name](**arguments)

  print("Tool Result:", tool_result)

  final_response = await client.responses.create(
    model="gpt-4o-mini",
    input=[
      *messages,
      {
        "type": "function_call",
        "call_id": function_call.call_id,
        "name": tool_name,
        "arguments": function_call.arguments
      },

      {
        "type": "function_call_output",
        "call_id": function_call.call_id,
        "output": json.dumps(
            tool_result,
            ensure_ascii=False
        )
      }
    ]
  )

  return final_response.output_text