from tools.time_tool import get_current_time
from tools.tavily_tool import web_search
from tools.long_memory_tool import save_long_memory, get_long_memories, delete_long_memory, update_long_memory

TOOLS = {
  "get_current_time": get_current_time,
  "web_search": web_search,
  "save_long_memory": save_long_memory,
  "get_long_memories": get_long_memories,
  "delete_long_memory": delete_long_memory,
  "update_long_memory": update_long_memory
}

TOOLS_SCHEMA = [
  {
    "type": "function",
    "name": "get_current_time",
    "description": "사용자가 현재 시간, 날짜, 오늘이 몇 일인지 물어볼 때 사용한다.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
  },
  {
    "type": "function",
    "name": "web_search",
    "description": """
    현재 정보가 필요하거나, 최신 뉴스, 실시간 정보, 모르는 개념을 조사해야 할 때 사용한다.
    """,
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "검색할 문장"
        }
      },
      "required": ["query"],
      "additionalProperties": False
    }
  },
  {
    "type": "function",
    "name": "save_long_memory",
    "description": """
    Save a single long-term memory for the current user.

    Use this tool ONLY when ALL of the following conditions are satisfied:
    1. The information is expected to remain useful for several months or longer.
    2. Remembering it will improve future conversations.
    3. It represents a stable preference, recurring project, persistent fact, or long-term goal.
    4. The information is unlikely to change frequently.

    Examples:
    - User prefers Python over Java.
    - User is building a Discord AI agent.
    - User likes concise answers.
    - User mainly uses Windows 11.

    Do NOT save:
    - Temporary tasks
    - Current bugs or errors
    - Today's events or schedules
    - One-time questions
    - Temporary opinions or situations
    - Information already stored

    Each memory must contain exactly ONE concise fact.
    Never store personally sensitive information unless the user explicitly asks you to remember it.
    Avoid storing passwords, tokens, private keys, financial information, addresses, phone numbers, or authentication data.
    """,
    "parameters": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string",
          "description": "One concise long-term memory."
        }
      },
      "required": ["content"],
      "additionalProperties": False
    }
  },
  {
    "type": "function",
    "name": "get_long_memories",
    "description": """
    Retrieve all long-term memories for the current user.

    Use this tool whenever previous user preferences, ongoing projects,
    persistent facts, or long-term goals may help generate a better response.

    Call this tool before answering if there is any reasonable possibility
    that stored memories could improve personalization or accuracy.

    Do NOT call this tool for simple factual questions that do not depend
    on the user's history.
    """,
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
  },
  {
    "type": "function",
    "name": "delete_long_memory",
    "description": """
    Delete an existing long-term memory.

    Use this tool when:
    - The user explicitly asks to forget something.
    - A stored memory is obsolete and no longer useful.
    - A memory is incorrect or duplicated.

    Do NOT delete memories unless there is a clear reason.

    Prefer updating a memory instead of deleting it when the same fact
    has simply changed over time.
    """,
    "parameters": {
        "type": "object",
        "properties": {
          "memory_id": {
            "type": "integer",
            "description": "The unique identifier of the memory to delete."
          }
        },
        "required": ["memory_id"],
        "additionalProperties": False
    }
  },
  {
    "type": "function",
    "name": "update_long_memory",
    "description": """
    Update an existing long-term memory.

    Use this tool when a stored memory is no longer accurate and should be
    replaced with new information instead of creating a duplicate.

    Examples:
    - "I now prefer Rust instead of Python."
    - "I switched from Windows to Ubuntu."

    Do NOT use this tool to add new information.
    Use it only to modify an existing memory that represents the same fact.

    The updated content must contain exactly ONE concise long-term fact.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "memory_id": {
              "type": "integer",
              "description": "The unique identifier of the memory to update."
            },
            "content": {
              "type": "string",
              "description": "The updated long-term memory."
            }
        },
        "required": ["memory_id", "content"],
        "additionalProperties": False
    }
  },  
]