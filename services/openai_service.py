from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from datetime import datetime
from services.tool_manager import TOOLS
import json

client = AsyncOpenAI(
  api_key=OPENAI_API_KEY
)

# MODEL LOAD
model = None
model_price = None
json_name = 'models.json'
model_json = None
with open(json_name, 'r', encoding='utf-8') as f:
  model_json = json.load(f)

if model_json is None:
  raise RuntimeError(f"{json_name}을 불러올 수 없습니다.")

model_names = model_json['models']
for name in model_names:
  if model_json['models'][name]['is_primary']:
    model = name
    model_price = model_json['models'][name]['model_price']

print(f"현재 선택된 모델 : {model} ({model_price})")

def get_model():
  return {'model_name': model,
          "model_price": model_price}

def get_model_list():
  return list(model_names.keys())

def change_model(model_name):
  global model, model_price
  if model_name in model_names:
    model = model_name
    model_price = model_json['models'][model_name]['model_price']

    return {'status': True,
            'model_name': model_name,
            'model_price': model_price}
  else:
    return {'status': False}

total_usage = 0

def calc_usage(prompt_tokens, completion_tokens, model_price):
  return (prompt_tokens / 1_000_000) * model_price[0] + (completion_tokens / 1_000_000) * model_price[1]

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
  global total_usage
  messages = [
    {
      "role": "system",
      "content": SYSTEM_PROMPT
    },
    *history
  ]

  response = await client.responses.create(
    model=model,
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
    total_usage += calc_usage(response.usage.input_tokens, response.usage.output_tokens, model_price)
    print(f"현재까지 사용량 : ${total_usage}")
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
    model=model,
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

  total_usage += (calc_usage(response.usage.input_tokens, response.usage.output_tokens, model_price) 
                 + calc_usage(final_response.usage.input_tokens, final_response.usage.output_tokens, model_price))
  print(f"현재까지 사용량 : ${total_usage}")

  return final_response.output_text