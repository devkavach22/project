import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    
    print(f"Testing connection to: {api_base}")
    print(f"Using model: {model}")
    print(f"API Key present: {'Yes' if api_key else 'No'}")

    try:
        llm = ChatOpenAI(
            model=model,
            openai_api_base=api_base,
            openai_api_key=api_key,
            temperature=0,
        )
        response = llm.invoke("Say hello")
        print(f"Success: {response.content}")
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_connection()
