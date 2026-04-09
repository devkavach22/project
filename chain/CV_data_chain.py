import json
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

from schemas.cv_data_schema import CVSchema

# -----------------------------------------------------
# 1️⃣ Define Pydantic Models
# -----------------------------------------------------

# -----------------------------------------------------
# 2️⃣ Initialize OpenAI or vLLM API
# -----------------------------------------------------
# os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
# os.environ["OPENAI_API_KEY"] = "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"
# api_key = os.getenv("OPENAI_API_KEY")

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key = os.getenv("OPENAI_API_KEY"),
# )

# print("✅ Using OpenRouter API Base:", OPENAI_API_BASE)
# print("✅ Using OpenRouter API Key:", OPENAI_API_KEY)
# print("✅ Using OpenRouter API Key:", os.getenv("DEBUG"))


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-20b:free"), #openai/gpt-oss-20b:free
    temperature=0,
    max_tokens=1500,
)


# -----------------------------------------------------
# 3️⃣ Create Output Parser
# -----------------------------------------------------
parser = PydanticOutputParser(pydantic_object=CVSchema)
format_instructions = parser.get_format_instructions()
format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")


# -----------------------------------------------------
# 4️⃣ Create Prompt Template
# -----------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
You are an intelligent AI CV parser. 

Extract maximum information from the CV and return structured JSON.

Rules:
- Always return valid JSON
- Never omit fields
- Use "" for missing strings
- Use [] for missing arrays
- Standardize dates as MM/YYYY or YYYY
- Missing end_date = "present"

{format_instructions}
"""
    ),
    ("user", "{cv_text}")
])



# -----------------------------------------------------
# 5️⃣ Combine Chain
# -----------------------------------------------------
chain = prompt | llm | parser


# -----------------------------------------------------
# 6️⃣ Function to Run the Chain
# -----------------------------------------------------
def get_cv_data_from_openrouter_model(cv_text: str) -> CVSchema: 
    # Truncate very large CVs to avoid context limits
    MAX_CV_CHARS = 50000
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS]

    result = chain.invoke({"cv_text": cv_text})

    # print(" Result -> ",result)
    
    #convert restult into dict/json
    result_dict = result.model_dump()
    
    # print("converted to dict -1",result_dict)
    # print("�� Converted to dict/json:", type(result_dict))

    return result_dict


# -----------------------------------------------------
# 7️⃣ Example Usage
# -----------------------------------------------------
if __name__ == "__main__":
    sample_cv_text = """
    Cv data here

    """

    structured_data = get_cv_data_from_openrouter_model(sample_cv_text)
    # print(structured_data)
    
    converted_dict_1 = structured_data.model_dump()
    
    # print(" testing -->> ",CVSchema(**converted_dict_1))
    
    # print("converted to dict -1",type(converted_dict_1))
    # print("--------------------------------")
    # print("converted data ->",converted_dict_1) 
    