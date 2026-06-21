from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(query: str) -> str:
    try:
        result = tavily.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=True
        )

        answer = result.get("answer", "")
        sources = []

        for item in result.get("results", []):
            sources.append(
                f"- {item['title']}\n{item['url']}"
            )

        return f"""
        검색 결과 :
        
        {answer}
        
        출처:
        {chr(10).join(sources)}
        """
    except Exception as e:
        return f"검색 실패: {e}"