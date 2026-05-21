from typing import TypedDict, Dict, Any, Annotated, List
import os
import operator

from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openrouter import ChatOpenRouter

from schemas.cv_data_schema import (
    CVSchema as ResumeData,
    WorkExperience,
    Project,
    Education,
    SkillSet,
    Certification,
    Language,
    Award,
    SocialMedia,
    WorkSample,
    WhitePaper,
    Presentation,
    Patent
)


# ============================================================
# 🔥 DEEP MERGE REDUCER
# ============================================================
def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:

    a = a or {}
    b = b or {}

    result = dict(a)

    for k, v in b.items():

        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = merge_dicts(result[k], v)

        else:
            result[k] = v

    return result


# ============================================================
# STATE
# ============================================================
class ResumeState(TypedDict):
    raw_text: str
    sections: Dict[str, str]
    extracted: Annotated[Dict[str, Any], merge_dicts]
    final: Dict[str, Any]
    llm_call_count: Annotated[int, operator.add]


# ============================================================
# LLM
# ============================================================
def get_llm():

    provider = os.getenv("LLM_PROVIDER_NAME", "ollama").lower()

    if provider == "openrouter":

        return ChatOpenAI(
            model="openai/gpt-4o-mini",
            temperature=0,
            max_tokens=4096,
            max_retries=2,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    elif provider == "groq":

        return ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            max_tokens=1500,
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )

    elif provider == "openai":

        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=1500,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    else:

        return ChatOllama(
            model="gpt-oss:20b-cloud",
            temperature=0,
            num_ctx=8192,
            base_url=os.getenv("OLLAMA_API_BASE_URL"),
        )


LLM = get_llm()


# ============================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================
class ExperienceProjectSchema(BaseModel):
    experience: List[WorkExperience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)


class EducationSkillsSchema(BaseModel):
    education: List[Education] = Field(default_factory=list)
    skills: SkillSet = Field(default_factory=SkillSet)


class CertificationOthersSchema(BaseModel):
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    awards: List[Award] = Field(default_factory=list)
    social_media: List[SocialMedia] = Field(default_factory=list)
    work_samples: List[WorkSample] = Field(default_factory=list)
    white_papers: List[WhitePaper] = Field(default_factory=list)
    presentations: List[Presentation] = Field(default_factory=list)
    patents: List[Patent] = Field(default_factory=list)


# ============================================================
# SPLIT NODE
# ============================================================
def split_node(state: ResumeState):

    text = state["raw_text"]

    sections = {
        "contact": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "others": ""
    }

    current = "others"

    for line in text.split("\n"):

        l = line.lower()

        if any(x in l for x in [ "experience","work experience", "professional experience", "employment", "career history" ]):
            current = "experience"

        elif any(x in l for x in [ "education", "qualification" ]):
            current = "education"

        elif any(x in l for x in [ "skill", "technology" ]):
            current = "skills"

        elif any(x in l for x in ["project","projects","academic project","personal project"]):
            current = "projects"

        elif any(x in l for x in ["certification","certifications","license","licenses"]):
            current = "certifications"

        elif any(x in l for x in ["contact","phone","email"]):
            current = "contact"

        elif any(x in l for x in ["language","award","publication","patent","presentation","portfolio","social","activity"]):
            current = "others"

        sections[current] += line + "\n"

    return {"sections": sections}


# ============================================================
# BASIC & CONTACT INFO NODE
# ============================================================
async def basic_info_node(state: ResumeState):

    text = (
        state["sections"]["contact"]
        + state["raw_text"]
    )[:6000]

    prompt = f"""
You are an expert resume parser. Extract candidate basic information and contact details into the provided JSON schema.

STRICT INSTRUCTIONS:
- DO NOT skip any information present in the text.
- Follow the Field Definitions strictly to avoid mixing up data.

FIELD DEFINITIONS:
- "full_name": Candidate's complete name.
- "gender": Male, Female, Other, etc.
- "date_of_birth": Also look for "DOB", "birth date", "born", etc.
- "religion": Candidate's religion if mentioned.
- "marital_status": Single, Married, etc.
- "current_company": The most recent or current employer.
- "current_designation": Job title at the current/latest company.
- "total_experience": Total years/months of work experience.
- "relevant_experience": Experience specifically relevant to their primary field.
- "total_companies_worked": Integer count of total distinct employers.
- "current_city", "current_state", "current_country": Where the candidate currently resides.
- "preferred_city", "preferred_state", "preferred_country": Where the candidate wants to work.
- "hometown": Candidate's native place or hometown.
- "graduation_degree": Undergraduate/Bachelor's degrees (e.g., B.Tech, B.Sc, B.A, B.Com, BBA, BCA, BE).
- "graduation_specialization": Major/Branch for graduation (e.g., Computer Science).
- "graduation_year": Year of passing graduation.
- "post_graduation_degree": Master's/Postgraduate degrees (e.g., M.Tech, M.Sc, M.A, M.Com, MBA, MCA, ME).
- "post_graduation_specialization": Major/Branch for post-graduation.
- "post_graduation_year": Year of passing post-graduation.
- "department": The department the candidate belongs to or wants to join.
- "role": The primary job role the candidate is seeking.
- "industry": The industry sector (e.g., IT, Finance, Healthcare).
- "reason_for_change": Why the candidate is looking for a new job.
- "is_permanent", "is_contractual", "is_full_time", "is_part_time": Booleans (true/false) indicating job type preference.
- "preferred_shift": E.g., Day, Night, Flexible.
- "preferred_work_locations": List of strings for desired work locations.
- "expected_ctc": Expected salary.
- "notice_period": E.g., "30 days", "Immediate".
- "status": Job search status if mentioned.
- "remarks": Any other notable information.
- "summary": The professional summary, objective, or profile summary section.
- "keywords": Important resume keywords, technologies, roles,
  tools, skills, frameworks, domains, certifications,
  and business terms present in the resume.
  Return as array of strings.
- "contact_info": Candidate's contact details, including:
  - "email": Email address.
  - "phone": Phone number.
  - "location": City, State, or Country.
  - "linkedin": LinkedIn profile URL.
  - "github": GitHub profile URL.
  - "portfolio": Personal website or portfolio URL.
  - "address": Full residential or mailing address.
  - "alternative_phone": Alternative contact number.

TEXT:
{text}
"""

    structured_llm = LLM.with_structured_output(
        ResumeData
    )

    res = await structured_llm.ainvoke(prompt)

    print("BASIC & CONTACT RAW:", res)

    return {
        "extracted": res.model_dump(),
        "llm_call_count": 1
    }


# ============================================================
# EXPERIENCE & PROJECT NODE
# ============================================================
async def experience_project_node(state: ResumeState):

    section = (
        state["sections"]["experience"]
        + "\n"
        + state["sections"]["projects"]
        + state["raw_text"]
    )[:6000]

    prompt = f"""
You are an expert resume parser. Extract candidate experience and projects information into the provided JSON schema.

STRICT INSTRUCTIONS:
- DO NOT skip any information present in the text.
- NEVER return empty experience if any work-related text exists.
- Extract ALL roles and projects even if formatting is messy.
- Infer company, role, project title, and dates.
- Split multiple roles and projects properly.

TEXT:
{section}
"""

    structured_llm = LLM.with_structured_output(
        ExperienceProjectSchema
    )

    calls = 1

    try:

        res = await structured_llm.ainvoke(prompt)

        parsed = res.model_dump()

        print("EXP & PROJ RAW:", parsed)

    except Exception as e:

        print("EXP & PROJ ERROR:", str(e))

        parsed = {
            "experience": [],
            "projects": []
        }

    return {
        "extracted": parsed,
        "llm_call_count": calls
    }


# ============================================================
# EDUCATION & SKILLS NODE
# ============================================================
async def education_skills_node(state: ResumeState):

    section = (
        state["sections"]["education"]
        + "\n"
        + state["sections"]["skills"]
        + state["raw_text"][:2000]
    )

    prompt = f"""
You are an expert resume parser. Extract candidate education and skills into the provided JSON schema.

STRICT INSTRUCTIONS:
- DO NOT skip any information present in the text.

TEXT:
{section}
"""

    structured_llm = LLM.with_structured_output(
        EducationSkillsSchema
    )

    res = await structured_llm.ainvoke(prompt)

    print("EDU_SKILLS RAW:", res)

    return {
        "extracted": res.model_dump(),
        "llm_call_count": 1
    }


# ============================================================
# CERTIFICATION & OTHERS NODE
# ============================================================
async def certification_others_node(state: ResumeState):

    section = (
        state["sections"]["certifications"]
        + "\n"
        + state["sections"]["others"]
        + "\n"
        + state["raw_text"]
    )[:6000]

    prompt = f"""
You are an expert resume parser.

Extract candidate certifications and other information into the provided JSON schema.

STRICT INSTRUCTIONS:
- DO NOT skip any information present in the text.
- Extract ALL certifications even if scattered.
- Extract all available additional information.
- Infer missing fields if possible.
- NEVER return empty arrays if related information exists.

TEXT:
{section}
"""

    structured_llm = LLM.with_structured_output(
        CertificationOthersSchema
    )

    res = await structured_llm.ainvoke(prompt)

    print("CERTIFICATION_OTHERS RAW:", res)

    return {
        "extracted": res.model_dump(),
        "llm_call_count": 1
    }


# ============================================================
# MERGE (NO LLM - PURE PYTHON)
# ============================================================
def merge_node(state: ResumeState):

    data = state["extracted"] or {}

    final = {
        "full_name": data.get("full_name"),
        "gender": data.get("gender"),
        "date_of_birth": data.get("date_of_birth"),
        "religion": data.get("religion"),
        "marital_status": data.get("marital_status"),

        "current_company": data.get("current_company"),
        "current_designation": data.get("current_designation"),
        "total_experience": data.get("total_experience"),
        "relevant_experience": data.get("relevant_experience"),
        "total_companies_worked": data.get("total_companies_worked"),

        "current_country": data.get("current_country"),
        "current_state": data.get("current_state"),
        "current_city": data.get("current_city"),

        "preferred_country": data.get("preferred_country"),
        "preferred_state": data.get("preferred_state"),
        "preferred_city": data.get("preferred_city"),
        "hometown": data.get("hometown"),

        "graduation_degree": data.get("graduation_degree"),
        "graduation_specialization": data.get("graduation_specialization"),
        "graduation_year": data.get("graduation_year"),

        "post_graduation_degree": data.get("post_graduation_degree"),
        "post_graduation_specialization": data.get("post_graduation_specialization"),
        "post_graduation_year": data.get("post_graduation_year"),

        "department": data.get("department"),
        "role": data.get("role"),
        "industry": data.get("industry"),
        "reason_for_change": data.get("reason_for_change"),

        "is_permanent": data.get("is_permanent"),
        "is_contractual": data.get("is_contractual"),
        "is_full_time": data.get("is_full_time"),
        "is_part_time": data.get("is_part_time"),

        "preferred_shift": data.get("preferred_shift"),
        "preferred_work_locations": data.get("preferred_work_locations") or [],

        "expected_ctc": data.get("expected_ctc"),
        "notice_period": data.get("notice_period"),
        "status": data.get("status"),
        "remarks": data.get("remarks"),

        "summary": data.get("summary"),

        "keywords": data.get("keywords") or [],

        "contact_info": data.get("contact_info"),

        "experience": data.get("experience") or [],
        "education": data.get("education") or [],
        "skills": data.get("skills"),
        "projects": data.get("projects") or [],
        "certifications": data.get("certifications") or [],

        "languages": data.get("languages") or [],
        "awards": data.get("awards") or [],
        "social_media": data.get("social_media") or [],
        "work_samples": data.get("work_samples") or [],
        "white_papers": data.get("white_papers") or [],
        "presentations": data.get("presentations") or [],
        "patents": data.get("patents") or []
    }

    return {"final": final}


# ============================================================
# SANITIZE
# ============================================================
def sanitize(data: dict):

    if not data:
        return {}

    list_fields = [
        "experience",
        "education",
        "projects",
        "certifications",
        "languages",
        "awards",
        "social_media",
        "work_samples",
        "white_papers",
        "presentations",
        "patents",
        "preferred_work_locations",
        "keywords"
    ]

    for key in list_fields:

        if key not in data or data[key] is None:
            data[key] = []

    if "skills" not in data or data["skills"] is None:

        data["skills"] = {
            "hard_skills": [],
            "soft_skills": []
        }

    return data


# ============================================================
# VALIDATE
# ============================================================
def validate_node(state: ResumeState):

    print("FINAL BEFORE VALIDATION:", state["final"])

    data = sanitize(state["final"])

    validated = ResumeData.model_validate(data)

    return {
        "final": validated.model_dump()
    }


# ============================================================
# GRAPH
# ============================================================
builder = StateGraph(ResumeState)

builder.add_node("split", split_node)
builder.add_node("basic", basic_info_node)
builder.add_node("experience_project", experience_project_node)
builder.add_node("education_skills", education_skills_node)
builder.add_node("certification_others", certification_others_node)
builder.add_node("merge", merge_node)
builder.add_node("validate", validate_node)

builder.set_entry_point("split")

builder.add_edge("split", "basic")
builder.add_edge("split", "experience_project")
builder.add_edge("split", "education_skills")
builder.add_edge("split", "certification_others")

builder.add_edge("basic", "merge")
builder.add_edge("experience_project", "merge")
builder.add_edge("education_skills", "merge")
builder.add_edge("certification_others", "merge")

builder.add_edge("merge", "validate")
builder.add_edge("validate", END)

graph = builder.compile()


# ============================================================
# MAIN
# ============================================================
async def extract_resume_agentic(text: str):

    result = await graph.ainvoke({
        "raw_text": text,
        "sections": {},
        "extracted": {},
        "final": {},
        "llm_call_count": 0
    })

    print(
        f"🔥 TOTAL LLM CALLS MADE BY AGENT: "
        f"{result.get('llm_call_count', 0)} 🔥"
    )

    return result["final"]