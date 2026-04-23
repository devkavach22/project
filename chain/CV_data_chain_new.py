import os
import time
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from schemas.cv_data_schema import CVSchema

load_dotenv()

# -----------------------------------------------------
# 🔹 1. Token Utilities
# -----------------------------------------------------
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def get_safe_max_tokens(cv_text: str, max_limit=4000):
    input_tokens = estimate_tokens(cv_text)
    buffer = 500
    remaining = max_limit - input_tokens - buffer
    return max(300, min(800, remaining))


# -----------------------------------------------------
# 🔹 2. Create LLM
# -----------------------------------------------------
def create_llm(cv_text: str, max_tokens_override=None):
    max_tokens = max_tokens_override or get_safe_max_tokens(cv_text)

    return ChatOpenAI(
        model="openai/gpt-oss-120b:free",
        temperature=0,
        max_tokens=max_tokens,
        timeout=60,
        api_key=os.getenv("OPENAI_API_KEY"),  # ✅ use env, not hardcoded
        base_url="https://openrouter.ai/api/v1",
    )


# -----------------------------------------------------
# 🔹 3. Output Parser
# -----------------------------------------------------
parser = PydanticOutputParser(pydantic_object=CVSchema)

format_instructions = parser.get_format_instructions()
format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")


# -----------------------------------------------------
# 🔹 4. Prompt (FIXED)
# -----------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
You are a CV parser. Extract all relevant data into structured JSON.

Rules:
- Fill missing fields with null or []
- Keep output strictly in JSON
- Follow schema exactly

{format_instructions}
"""
    ),
    ("user", "CV Text:\n{cv_text}")
])


# -----------------------------------------------------
# 🔹 5. Main Function (Retry + Safe)
# -----------------------------------------------------
def get_cv_data_from_openrouter_model(cv_text: str) -> dict:

    MAX_CV_CHARS = 20000
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS]

    retries = [800, 600, 400, 250]

    for attempt, tokens in enumerate(retries):
        try:
            print(f"[Attempt {attempt+1}] max_tokens={tokens}")

            llm = create_llm(cv_text, max_tokens_override=tokens)

            # ✅ create chain here AFTER prompt exists
            chain = prompt | llm | parser

            result = chain.invoke({"cv_text": cv_text})

            return result.model_dump()

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")

            if "402" in error_msg or "max_tokens" in error_msg:
                print("⚠️ Token issue → retrying...")
                time.sleep(1)
                continue
            else:
                raise e

    raise Exception("❌ Failed after retries (token/credit issue)")


# -----------------------------------------------------
# 🔹 6. Test Run
# -----------------------------------------------------
if __name__ == "__main__":
    sample_cv = """
    John Doe
    Software Engineer
    Skills: Python, FastAPI, React
    Experience: 3 years at ABC Company
    """

    data = get_cv_data_from_openrouter_model(sample_cv)
    print(data)