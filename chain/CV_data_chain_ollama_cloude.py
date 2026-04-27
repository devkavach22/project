import os
import time
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from schemas.cv_data_schema import CVSchema

load_dotenv()


# -----------------------------------------------------
# 🔹 1. Token Utilities
# -----------------------------------------------------
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def get_safe_max_tokens(cv_text: str, max_limit: int = 8000) -> int:
    input_tokens = estimate_tokens(cv_text)
    buffer = 500
    remaining = max_limit - input_tokens - buffer
    return max(1000, min(4000, remaining))


# -----------------------------------------------------
# 🔹 2. Create LLM (SYNC)
# -----------------------------------------------------
def create_llm(max_tokens: int) -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_output_tokens=max_tokens,
        google_api_key=api_key,
    )


# -----------------------------------------------------
# 🔹 3. Output Parser
# -----------------------------------------------------
parser = PydanticOutputParser(pydantic_object=CVSchema)
format_instructions = parser.get_format_instructions()


# -----------------------------------------------------
# 🔹 4. Prompt
# -----------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an expert CV/Resume parser. Extract ALL relevant information "
            "from the CV text and return it ONLY as a valid JSON object.\n\n"
            "Rules:\n"
            "- Return ONLY raw JSON. No markdown, no ```json fences, no extra text.\n"
            "- Fill missing fields with null or [] as appropriate.\n"
            "- Follow the schema exactly.\n"
            "- For skills: separate hard/technical skills from soft/interpersonal skills.\n"
            "- For experience: extract all responsibilities and technologies used.\n"
            "- For dates: use format MM/YYYY where possible.\n\n"
            "{format_instructions}"
        ),
    ),
    ("user", "Parse this CV and extract all information:\n\n{cv_text}"),
])


# -----------------------------------------------------
# 🔹 5. Main Sync Function with Retry
# -----------------------------------------------------
def get_cv_data_from_gemini(cv_text: str) -> dict:
    MAX_CV_CHARS = 20000
    if len(cv_text) > MAX_CV_CHARS:
        cv_text = cv_text[:MAX_CV_CHARS]

    # Your schema is large — use higher token limits
    retry_tokens = [4000, 3000, 2000, 1500]

    last_error = None

    for attempt, tokens in enumerate(retry_tokens):
        try:
            print(f"[Attempt {attempt + 1}] max_tokens={tokens}")

            llm = create_llm(max_tokens=tokens)
            chain = prompt | llm | parser

            result = chain.invoke({
                "cv_text": cv_text,
                "format_instructions": format_instructions,
            })

            print(f"[Attempt {attempt + 1}] ✅ Success")
            return result.model_dump()

        except Exception as e:
            last_error = e
            error_msg = str(e)
            print(f"[Attempt {attempt + 1}] ❌ Error: {error_msg}")

            # Don't retry on auth/key errors
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise

            time.sleep(1.5)

    raise Exception(f"❌ All retry attempts failed. Last error: {last_error}")


# -----------------------------------------------------
# 🔹 6. Test Run
# -----------------------------------------------------
if __name__ == "__main__":
    sample_cv = """
    Rahul Sharma
    rahul.sharma@email.com | +91-9876543210 | Mumbai, Maharashtra
    linkedin.com/in/rahulsharma | github.com/rahulsharma
    DOB: 15/03/1995 | Male | Single

    Professional Summary:
    Full Stack Developer with 5+ years of experience building scalable web applications.
    Currently open to senior roles in fintech or SaaS companies.

    Skills:
    Technical: Python, FastAPI, React, Node.js, PostgreSQL, Redis, Docker, AWS, Git
    Soft Skills: Leadership, Communication, Problem Solving, Team Collaboration

    Work Experience:

    Senior Software Engineer — ABC Fintech Pvt Ltd, Mumbai (Jan 2022 – Present)
    - Built microservices handling 2M+ daily transactions
    - Led a team of 5 engineers
    - Reduced API latency by 40% using Redis caching
    Technologies: Python, FastAPI, Redis, PostgreSQL, Docker

    Software Developer — XYZ Tech, Pune (Jun 2019 – Dec 2021)
    - Developed REST APIs for a B2B SaaS platform
    - Migrated legacy codebase from PHP to Python
    Technologies: Python, Django, MySQL, React

    Education:
    B.Tech in Computer Engineering — University of Mumbai (2015 – 2019), GPA: 8.5/10
    12th — St. Xavier's College, Mumbai (2015), 88%
    10th — Don Bosco High School, Mumbai (2013), 92%

    Projects:
    - PayFlow: Real-time payment gateway using FastAPI + Stripe. Live at payflow.io
    - TrackIt: Task management app built with React + Firebase

    Certifications:
    - AWS Certified Developer – Associate | Amazon Web Services | 2022
    - Google Cloud Professional | Google | 2021

    Languages: English (Fluent), Hindi (Native), Marathi (Native)

    Awards:
    - Best Employee Q3 2023 — ABC Fintech Pvt Ltd
    - Hackathon Winner — TechFest Mumbai 2019

    Notice Period: 30 days
    Expected CTC: 25 LPA
    Preferred Locations: Mumbai, Bengaluru, Remote
    """

    data = get_cv_data_from_gemini(sample_cv)
    print(json.dumps(data, indent=2, default=str))
