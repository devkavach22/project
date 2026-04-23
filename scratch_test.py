import os
from dotenv import load_dotenv

from openrouter import OpenRouter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas.cv_data_schema import CVSchema

load_dotenv()

parser = PydanticOutputParser(pydantic_object=CVSchema)
format_instructions = parser.get_format_instructions()
format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")

prompt = ChatPromptTemplate.from_messages([
    ("system", f"You are a CV parser.\n{format_instructions}"),
    ("user", "CV Text:\n{cv_text}")
])

def map_role(t: str) -> str:
    if t == "human": return "user"
    if t == "ai": return "assistant"
    return t

def test():
    cv_text = "John Doe\nSoftware Engineer"
    msgs = prompt.format_messages(cv_text=cv_text)
    or_msgs = [{"role": map_role(m.type), "content": m.content} for m in msgs]
    
    with OpenRouter(api_key=os.getenv("OPENAI_API_KEY")) as client:
        res = client.chat.send(
            model="openai/gpt-oss-120b:free",
            messages=or_msgs,
            max_tokens=600,
        )
        content = res.choices[0].message.content
        print("Raw content:", content)
        try:
            parsed = parser.parse(content)
            print("Parsed:", parsed.model_dump())
        except Exception as e:
            print("Parse error:", e)

if __name__ == "__main__":
    test()
