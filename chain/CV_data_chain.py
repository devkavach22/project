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

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
    # model=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-20b:free"), #openai/gpt-oss-20b:free
    temperature=0,
    max_tokens=4000,
)


# -----------------------------------------------------
# 3️⃣ Create Output Parser
# -----------------------------------------------------
parser = PydanticOutputParser(pydantic_object=CVSchema)
format_instructions = parser.get_format_instructions()
# Escape brackets for LangChain prompt template
format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")


# -----------------------------------------------------
# 4️⃣ Create Prompt Template
# -----------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
You are a highly advanced AI CV parser specialized in converting resumes into precisely structured JSON data.

Your primary goal is to extract **every piece of information** available in the CV and map it to the provided schema.

Rules:
1. **Exhaustive Extraction**: Do not skip any fields. If information can be inferred or is explicitly present, extract it.
2. **Handle Missing Data**: 
   - Use `null` or `""` for missing strings (depending on the schema's requirements).
   - Use `[]` for missing arrays.
   - For Boolean fields, if the information is not present, default to `null`.
3. **Standardize Dates**: Use MM/YYYY or YYYY format. If an end date is missing for a currently held position, use "Present".
4. **Summary**: Provide a concise but comprehensive professional summary based on the CV content.
5. **Skills**: Categorize skills into 'hard_skills' and 'soft_skills' as accurately as possible.
6. **Experience & Education**: Ensure all entries in the work history and educational background are captured in their respective lists.

{format_instructions}
"""
    ),
    ("user", "CV Text to Parse:\n\n{cv_text}")
])



# -----------------------------------------------------
# 5️⃣ Combine Chain
# -----------------------------------------------------
chain = prompt | llm | parser


# -----------------------------------------------------
# 6️⃣ Function to Run the Chain
# -----------------------------------------------------
def get_cv_data_from_openrouter_model(cv_text: str) -> dict: 
    """
    Parses CV text into a structured dictionary matching CVSchema.
    """
    # Truncate very large CVs to avoid context limits
    MAX_CV_CHARS = 100000 
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS]

    try:
        # Invoke the chain
        result = chain.invoke({"cv_text": cv_text})
        
        # result is a CVSchema object (due to parser)
        # Convert to dict for API response
        return result.model_dump()
        
    except Exception as e:
        print(f"Error in CV parsing chain: {e}")
        # Return an empty/minimal schema dict on failure to avoid total crash
        return CVSchema().model_dump()


# -----------------------------------------------------
# 7️⃣ Example Usage
# -----------------------------------------------------
if __name__ == "__main__":
    sample_cv_text = """
    Cv data here

    """

    structured_data = get_cv_data_from_openrouter_model(sample_cv_text)
    print(structured_data)