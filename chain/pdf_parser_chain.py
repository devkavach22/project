import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from schemas.SpaceFix_Schema import SpaceFixSchema
from llm.base import get_llm


# -----------------------------------------------------
# 1️⃣ Initialize LLM
# -----------------------------------------------------


llm = get_llm()

# llm = ChatOpenAI(
#     model=os.getenv("OPENROUTER_MODEL"),
#     temperature=0,
#     max_tokens=4096,
#     base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

# -----------------------------------------------------
# 2️⃣ Output Parser (STRICT FORMAT)
# -----------------------------------------------------

parser = PydanticOutputParser(pydantic_object=SpaceFixSchema)


# -----------------------------------------------------
# 3️⃣ Schema Safe Injection
# -----------------------------------------------------

schema_json_safe = json.dumps(
    SpaceFixSchema.model_json_schema(),
    indent=2
)

# escape braces for prompt template
schema_json_safe = schema_json_safe.replace("{", "{{").replace("}", "}}")


# -----------------------------------------------------
# 4️⃣ Prompt Template
# -----------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
You are an intelligent telecom CAF form extraction AI.

Extract structured data STRICTLY following this schema:

{schema_json_safe}

-------------------------
EXTRACTION RULES
-------------------------

1. ALWAYS return ALL fields from schema.
2. Never remove or rename keys.
3. Missing values → use "":
   - strings → ""
   - lists → []
4. Output MUST be valid JSON only.
5. No markdown, no explanation.
6. Extract maximum possible information.
7. Normalize dates to DD/MM/YYYY or YYYY.
8. Addresses must be split into components properly.
9. If text unclear → keep best possible guess.
10. Photos should contain detected image references or [].

Return ONLY JSON.
"""
    ),
    ("user", "{document_text}")
])


# -----------------------------------------------------
# 5️⃣ Chain
# -----------------------------------------------------

chain = prompt | llm | parser


# -----------------------------------------------------
# 6️⃣ Extraction Function
# -----------------------------------------------------

def get_spacefix_data(document_text: str) -> dict:
    result: SpaceFixSchema = chain.invoke(
        {"document_text": document_text}
    )

    return result.model_dump()


# -----------------------------------------------------
# 7️⃣ Example
# -----------------------------------------------------

if __name__ == "__main__":

    sample_text = """
    CAF No: 12345678
    Service Type: Prepaid
    Customer Name: Ravina Akashkumar Soni
    Father Name: Akashkumar Soni
    DOB: 12/03/1998
    Gender: Female
    Mobile Allocated: 9876543210
    Address: Flat 101, Shree Apartment, Satellite, Ahmedabad, Gujarat 380015
    """

    data = get_spacefix_data(sample_text)

    print(json.dumps(data, indent=2))