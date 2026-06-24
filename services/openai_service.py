from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from datetime import datetime
from services.tool_manager import TOOLS, TOOLS_SCHEMA
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

SYSTEM_PROMPT = f"""
너는 디스코드 AI 에이전트다.

규칙:
- 함수가 반드시 필요한 경우에만 호출한다.
- 현재 시간을 묻는 질문에만 get_current_time을 사용한다.
- 일반 대화나 자기소개에는 함수를 사용하지 않는다.

web_search 사용 규칙:
- 최신 정보가 필요한 경우 반드시 사용
- 사용자의 질문에 대한 확신이 80% 미만이면 사용
- 뉴스, 가격, API 변경사항, 버전 정보는 사용
- 단순 상식은 사용하지 말 것
- 위 모든 경우가 아님에도 사용자가 검색을 통한 결과를 원한다고 말할 경우 사용
"""

async def generate_response(history) -> str:
    global total_usage

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *history
    ]

    while True:

        response = await client.responses.create(
            model=model,
            input=conversation,
            tools=TOOLS_SCHEMA
        )

        total_usage += calc_usage(
            response.usage.input_tokens,
            response.usage.output_tokens,
            model_price
        )

        # 모델이 생성한 모든 output을 대화에 추가
        conversation.extend(response.output)

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # Tool Call이 없으면 최종 응답
        if not tool_calls:
            print(f"현재까지 사용량 : ${total_usage}")
            return response.output_text

        # Tool 실행
        for tool_call in tool_calls:

            tool_name = tool_call.name

            print("Tool Call:", tool_name)

            try:
                arguments = json.loads(tool_call.arguments)
            except Exception:
                arguments = {}

            print("Arguments:", arguments)

            if tool_name not in TOOLS:

                tool_result = {
                    "error": f"알 수 없는 도구 : {tool_name}"
                }

            else:

                try:
                    tool_result = TOOLS[tool_name](**arguments)
                except Exception as e:
                    tool_result = {
                        "error": str(e)
                    }

            print("Tool Result:", tool_result)

            # Tool 결과를 conversation에 추가
            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        tool_result,
                        ensure_ascii=False
                    )
                }
            )

        print(f"현재까지 사용량 : ${total_usage}")