from typing import TypedDict, Dict, Any, Annotated
import json
import re
import os

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openrouter import ChatOpenRouter

from schemas.cv_data_schema import CVSchema as ResumeData


# ============================================================
# 🔥 DEEP MERGE REDUCER
# ============================================================
def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    a = a or {}
    b = b or {}

    result = dict(a)

    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
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


# ============================================================
# LLM
# ============================================================

def get_llm():
    return ChatOpenRouter(
        model="openai/gpt-oss-20b:free",  
        # other good options:
        # "meta-llama/llama-3.1-70b-instruct"
        # "anthropic/claude-3.5-sonnet"
        # "mistralai/mistral-large"

        temperature=0,
        max_tokens=4096,
        max_retries=2,

        api_key=os.getenv("OPENROUTER_API_KEY"),

        # optional but recommended (OpenRouter ranking)
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Resume Parser"
        }
    )

    

# def get_llm():
#     return ChatOllama(
#         model="gpt-oss:20b-cloud",  # or "llama3.1:8b"  or llama3.1:70b or "gpt-oss:20b-cloud"  or "gpt-oss:120b-cloud"
#         temperature=0,
#         num_ctx=8192,
#         base_url=os.getenv("OLLAMA_API_BASE_URL"),  # remove if using local
#     )

# def get_llm():
#     return ChatGroq(
#         model="openai/gpt-oss-120b",  # or "mixtral-8x7b-32768"  # llama3-70b-8192
#         temperature=0,
#         max_tokens=1500,
#         groq_api_key=os.getenv("GROQ_API_KEY"),
#     )

# def get_llm():
#     return ChatOpenAI(
#         model="openai/gpt-4o-mini",
#         temperature=0,
#         max_tokens=1500,
#         api_key=os.getenv("OPENROUTER_API_KEY"),
#         base_url="https://openrouter.ai/api/v1",
#     )


# ============================================================
# JSON PARSER
# ============================================================
def safe_parse(text: str):
    try:
        return json.loads(text)
    except:
        text = re.sub(r'```json|```', '', text).strip()
        try:
            return json.loads(text)
        except:
            print("❌ JSON PARSE FAILED:", text[:300])
            return {}


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

        if any(x in l for x in [
            "experience", "work experience", "professional experience",
            "employment", "career history"
        ]):
            current = "experience"

        elif any(x in l for x in ["education", "qualification"]):
            current = "education"

        elif any(x in l for x in ["skill", "technology"]):
            current = "skills"

        elif any(x in l for x in ["project", "projects", "academic project", "personal project"]):
            current = "projects"

        elif any(x in l for x in ["certification", "certifications", "license", "licenses"]):
            current = "certifications"

        elif any(x in l for x in ["contact", "phone", "email"]):
            current = "contact"

        elif any(x in l for x in ["language", "award", "publication", "patent", "presentation", "portfolio", "social", "activity"]):
            current = "others"

        sections[current] += line + "\n"

    return {"sections": sections}


# ============================================================
# CONTACT NODE
# ============================================================
def contact_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["contact"] + state["raw_text"][:3000]

    prompt = f"""
DO NOT skip any information present in the text.

Return ONLY JSON.

{{
 "contact_info": {{
   "email": "",
   "phone": "",
   "location": "",
   "linkedin": "",
   "github": "",
   "portfolio": "",
   "address": "",
   "alternative_phone": ""
 }}
}}

TEXT:
{section}
"""

    res = llm.invoke(prompt)
    print("CONTACT RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# BASIC INFO NODE
# ============================================================
def basic_info_node(state: ResumeState):
    llm = get_llm()
    text = state["raw_text"][:4000]

    prompt = f"""
You are a resume parser.

DO NOT skip any information present in the text.

Return ONLY valid JSON.

{{
 "full_name": "",
 "gender": "",
 "date_of_birth": "",
 "religion": "",
 "marital_status": "",
 "current_company": "",
 "current_designation": "",
 "total_experience": "",
 "relevant_experience": "",
 "total_companies_worked": null,
 "current_city": "",
 "current_state": "",
 "current_country": "",
 "preferred_country": "",
 "preferred_state": "",
 "preferred_city": "",
 "hometown": "",
 "graduation_degree": "",
 "graduation_specialization": "",
 "graduation_year": "",
 "post_graduation_degree": "",
 "post_graduation_specialization": "",
 "post_graduation_year": "",
 "department": "",
 "role": "",
 "industry": "",
 "reason_for_change": "",
 "is_permanent": null,
 "is_contractual": null,
 "is_full_time": null,
 "is_part_time": null,
 "preferred_shift": "",
 "preferred_work_locations": [],
 "expected_ctc": "",
 "notice_period": "",
 "status": "",
 "remarks": "",
 "summary": ""
}}

TEXT:
{text}
"""

    res = llm.invoke(prompt)
    print("BASIC RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# EXPERIENCE NODE (FIXED)
# ============================================================
def experience_node(state: ResumeState):
    llm = get_llm()

    section = (state["sections"]["experience"] + state["raw_text"])[:5000]

    prompt = f"""
You are a highly accurate resume parser.

DO NOT skip any information present in the text.

STRICT RULES:
- NEVER return empty experience if any work-related text exists
- Extract ALL roles even if formatting is messy
- Infer company, role, and dates
- Split multiple roles properly

Return ONLY JSON.

{{
 "experience": [
   {{
     "company": "",
     "job_title": "",
     "start_date": "",
     "end_date": "",
     "is_current_employment": false,
     "responsibilities": [],
     "technologies": []
   }}
 ]
}}

TEXT:
{section}
"""

    res = llm.invoke(prompt)
    parsed = safe_parse(res.content)

    print("EXP RAW:", parsed)

    # ✅ fallback
    if not parsed.get("experience"):
        print("⚠️ fallback triggered")

        fallback_prompt = f"""
DO NOT skip any information.

Extract ALL experience from this resume.

Return JSON only.

{{
 "experience": [
   {{
     "company": "",
     "job_title": "",
     "start_date": "",
     "end_date": ""
   }}
 ]
}}

TEXT:
{state["raw_text"][:6000]}
"""

        res2 = llm.invoke(fallback_prompt)
        parsed = safe_parse(res2.content)

        print("EXP FALLBACK:", parsed)

    return {"extracted": parsed}


# ============================================================
# EDUCATION NODE
# ============================================================
def education_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["education"]

    prompt = f"""
DO NOT skip any information present in the text.

Return ONLY JSON.

{{
 "education": [
   {{
     "education_level": "",
     "institution": "",
     "field_of_study": "",
     "passing_year": "",
     "gpa": ""
   }}
 ]
}}

TEXT:
{section}
"""

    res = llm.invoke(prompt)
    print("EDU RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# SKILLS NODE
# ============================================================
def skills_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["skills"]

    prompt = f"""
DO NOT skip any information present in the text.

Return ONLY JSON.

{{
 "skills": {{
   "hard_skills": [],
   "soft_skills": []
 }}
}}

TEXT:
{section}
"""

    res = llm.invoke(prompt)
    print("SKILLS RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# PROJECT NODE
# ============================================================
def project_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["projects"] + state["raw_text"]

    prompt = f"""
You are a highly accurate resume parser.

DO NOT skip any information present in the text.

STRICT RULES:
- Extract ALL projects even if poorly formatted
- NEVER return empty if any project exists
- Infer missing fields where possible

Return ONLY JSON.

{{
 "projects": [
   {{
     "title": "",
     "description": "",
     "url": "",
     "technologies": [],
     "start_date": "",
     "end_date": ""
   }}
 ]
}}

TEXT:
{section[:5000]}
"""

    res = llm.invoke(prompt)
    parsed = safe_parse(res.content)

    print("PROJECT RAW:", parsed)

    # ✅ fallback if empty
    if not parsed.get("projects"):
        fallback_prompt = f"""
Extract ALL projects from this resume.

Return JSON only.

{{
 "projects": [
   {{
     "title": "",
     "description": ""
   }}
 ]
}}

TEXT:
{state["raw_text"][:6000]}
"""
        res2 = llm.invoke(fallback_prompt)
        parsed = safe_parse(res2.content)

        print("PROJECT FALLBACK:", parsed)

    return {"extracted": parsed}


# ============================================================
# ertification Node
# ============================================================
def certification_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["certifications"] + state["raw_text"]

    prompt = f"""
You are a highly accurate resume parser.

DO NOT skip any information present in the text.

STRICT RULES:
- Extract ALL certifications even if scattered
- Infer missing fields if possible
- NEVER return empty if certification exists

Return ONLY JSON.

{{
 "certifications": [
   {{
     "name": "",
     "url": "",
     "does_not_expire": false,
     "date_obtained": ""
   }}
 ]
}}

TEXT:
{section[:5000]}
"""

    res = llm.invoke(prompt)
    print("CERT RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# OTHERS NODE (Languages, Awards, Social Media, etc.)
# ============================================================
def others_node(state: ResumeState):
    llm = get_llm()
    section = state["sections"]["others"] + state["raw_text"][:4000]

    prompt = f"""
You are a highly accurate resume parser.

DO NOT skip any information present in the text.
Extract information into the following categories if they exist.

Return ONLY JSON.

{{
 "languages": [
   {{ "language": "" }}
 ],
 "awards": [
   {{ "title": "", "issuer": "", "date": "" }}
 ],
 "social_media": [
   {{ "name": "", "url": "", "description": "" }}
 ],
 "work_samples": [
   {{ "title": "", "url": "", "start_date": "", "duration_month": "", "is_currently_working": false, "total_duration": "" }}
 ],
 "white_papers": [
   {{ "title": "", "url": "", "start_date": "", "duration_month": "", "description": "" }}
 ],
 "presentations": [
   {{ "title": "", "url": "", "description": "" }}
 ],
 "patents": [
   {{ "title": "", "url": "", "is_issued": false, "is_pending": false, "application_number": "", "issue_year": "", "issue_month": "", "description": "" }}
 ]
}}

TEXT:
{section}
"""

    res = llm.invoke(prompt)
    print("OTHERS RAW:", res.content)

    return {"extracted": safe_parse(res.content)}


# ============================================================
# MERGE (NO LLM - PURE PYTHON)
# ============================================================
def merge_node(state: ResumeState):
    data = state["extracted"] or {}

    final = {
        # ===== BASIC =====
        "full_name": data.get("full_name"),
        "gender": data.get("gender"),
        "date_of_birth": data.get("date_of_birth"),
        "religion": data.get("religion"),
        "marital_status": data.get("marital_status"),

        # ===== CURRENT JOB =====
        "current_company": data.get("current_company"),
        "current_designation": data.get("current_designation"),
        "total_experience": data.get("total_experience"),
        "relevant_experience": data.get("relevant_experience"),
        "total_companies_worked": data.get("total_companies_worked"),

        # ===== LOCATION =====
        "current_country": data.get("current_country"),
        "current_state": data.get("current_state"),
        "current_city": data.get("current_city"),

        "preferred_country": data.get("preferred_country"),
        "preferred_state": data.get("preferred_state"),
        "preferred_city": data.get("preferred_city"),
        "hometown": data.get("hometown"),

        # ===== EDUCATION SUMMARY =====
        "graduation_degree": data.get("graduation_degree"),
        "graduation_specialization": data.get("graduation_specialization"),
        "graduation_year": data.get("graduation_year"),

        "post_graduation_degree": data.get("post_graduation_degree"),
        "post_graduation_specialization": data.get("post_graduation_specialization"),
        "post_graduation_year": data.get("post_graduation_year"),

        # ===== PROFESSIONAL =====
        "department": data.get("department"),
        "role": data.get("role"),
        "industry": data.get("industry"),
        "reason_for_change": data.get("reason_for_change"),

        # ===== JOB PREF =====
        "is_permanent": data.get("is_permanent"),
        "is_contractual": data.get("is_contractual"),
        "is_full_time": data.get("is_full_time"),
        "is_part_time": data.get("is_part_time"),

        "preferred_shift": data.get("preferred_shift"),
        "preferred_work_locations": data.get("preferred_work_locations") or [],

        # ===== HR =====
        "expected_ctc": data.get("expected_ctc"),
        "notice_period": data.get("notice_period"),
        "status": data.get("status"),
        "remarks": data.get("remarks"),

        # ===== SUMMARY =====
        "summary": data.get("summary"),

        # ===== CONTACT =====
        "contact_info": data.get("contact_info") or {
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
            "address": None,
            "alternative_phone": None
        },

        # ===== CORE LISTS =====
        "experience": data.get("experience") or [],
        "education": data.get("education") or [],
        "skills": data.get("skills") or {"hard_skills": [], "soft_skills": []},
        "projects": data.get("projects") or [],
        "certifications": data.get("certifications") or [],

        # ===== EXTRA =====
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
        "experience", "education", "projects", "certifications",
        "languages", "awards", "social_media", "work_samples",
        "white_papers", "presentations", "patents",
        "preferred_work_locations"
    ]

    for key in list_fields:
        if key not in data or data[key] is None:
            data[key] = []

    # ✅ ensure nested structure
    if "skills" not in data or data["skills"] is None:
        data["skills"] = {"hard_skills": [], "soft_skills": []}

    return data


# ============================================================
# VALIDATE
# ============================================================
def validate_node(state: ResumeState):
    print("FINAL BEFORE VALIDATION:", state["final"])

    data = sanitize(state["final"])
    validated = ResumeData.model_validate(data)

    return {"final": validated.model_dump()}


# ============================================================
# GRAPH
# ============================================================
builder = StateGraph(ResumeState)

builder.add_node("split", split_node)
builder.add_node("basic", basic_info_node)
builder.add_node("experience", experience_node)
builder.add_node("education", education_node)
builder.add_node("skills", skills_node)
builder.add_node("projects", project_node)
builder.add_node("merge", merge_node)
builder.add_node("validate", validate_node)
builder.add_node("certifications", certification_node)
builder.add_node("contact", contact_node)
builder.add_node("others", others_node)

builder.set_entry_point("split")

builder.add_edge("split", "basic")
builder.add_edge("split", "experience")
builder.add_edge("split", "education")
builder.add_edge("split", "skills")
builder.add_edge("split", "projects")
builder.add_edge("split", "certifications")
builder.add_edge("split", "contact")
builder.add_edge("split", "others")

builder.add_edge("basic", "merge")
builder.add_edge("experience", "merge")
builder.add_edge("education", "merge")
builder.add_edge("skills", "merge")
builder.add_edge("projects", "merge")
builder.add_edge("certifications", "merge")
builder.add_edge("contact", "merge")
builder.add_edge("others", "merge")

builder.add_edge("merge", "validate")
builder.add_edge("validate", END)

graph = builder.compile()


# ============================================================
# MAIN
# ============================================================
def extract_resume_agentic(text: str):
    result = graph.invoke({
        "raw_text": text,
        "sections": {},
        "extracted": {},
        "final": {}
    })

    return result["final"]