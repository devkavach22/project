import os
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    env = os.getenv("ENV_MODE", "production").lower()

    if env == "production":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "glm-5.1:cloud"),
            base_url="http://localhost:11434",
            temperature=0,
            api_key=os.getenv("OLLAMA_API_KEY", ""),
        )

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL"),
        temperature=0,
        max_tokens=1500, # Set a limit to stay within your credit budget
        base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )


llm = get_llm()