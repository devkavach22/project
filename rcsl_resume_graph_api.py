#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import json
import logging
import re
from typing import List, Optional, TypedDict

from pydantic import BaseModel, Field, field_validator

# LangGraph
from langgraph.graph import StateGraph, END

# LangChain Groq
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Your schema
from schemas.cv_data_schema import CVSchema as ResumeData

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# ============================================================
# CONFIG
# ============================================================

CHUNK_SIZE = 6000   # safe limit for Groq
MODEL = "llama-3.3-70b-versatile"

# ============================================================
# STATE
# ============================================================

class ResumeState(TypedDict):
    text: str
    chunks: List[str]
    partial_results: List[dict]
    final_json: dict


# ============================================================
# HELPERS
# ============================================================

def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def _repair_json(text: str) -> str:
    # Remove markdown fences if present
    text = re.sub(r"```(?:json)?", "", text)
    text = text.strip().strip("`").strip()
    
    text = re.sub(r'\bNone\b', 'null', text)
    text = re.sub(r'\bTrue\b', 'true', text)
    text = re.sub(r'\bFalse\b', 'false', text)
    text = re.sub(r',\s*([\]}])', r'\1', text)
    
    # Try to close truncated JSON
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    text += ']' * max(open_brackets, 0)
    text += '}' * max(open_braces, 0)
    
    return text


def parse_json_safe(content: str) -> dict:
    # 1. Clean markdown
    cleaned = re.sub(r"```(?:json)?", "", content).strip().strip("`").strip()
    try:
        return json.loads(cleaned)
    except:
        try:
            return json.loads(_repair_json(cleaned))
        except:
            # Try regex to find first {
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(_repair_json(match.group()))
                except:
                    pass
            _logger.error("Failed to parse JSON content: %s", content[:200])
            return {}


def merge_dicts(base: dict, new: dict) -> dict:
    """
    Deep merge for resume fields
    """
    for k, v in new.items():
        if not v:
            continue

        if k not in base or base[k] in (None, [], {}):
            base[k] = v
        else:
            if isinstance(v, list):
                base[k].extend(v)
            elif isinstance(v, dict):
                base[k] = merge_dicts(base.get(k, {}), v)
            else:
                base[k] = v

    return base


# ============================================================
# PROMPT
# ============================================================

EXTRACTION_PROMPT = """
Extract every possible field from the resume text below and return a single JSON object.
STRICT RULES:
- Return ONLY valid JSON
- Use null for missing scalar fields
- Use [] for missing array fields
- No explanation or markdown fences

FIELDS TO EXTRACT:
full_name, gender, dob, religion, marital_status,
current_company, current_designation,
total_experience, relevant_experience, total_companies_worked,
current_country, current_state, current_city,
preferred_country, preferred_state, preferred_city, hometown,
graduation_degree, graduation_specialization, graduation_year,
post_graduation_degree, post_graduation_specialization, post_graduation_year,
department, role, industry, reason_for_change,
is_permanent, is_contractual, is_full_time, is_part_time,
preferred_shift, preferred_work_locations: [],
expected_ctc, notice_period, status, remarks, summary,

contact_info: {email, phone, location, linkedin, github, portfolio, address, alternative_phone},
experience: [{company, job_title, location, start_date, end_date, duration, responsibilities: [], technologies: []}],
education: [{education_level, institution, field_of_study, course_type, passing_year, gpa}],
skills: {hard_skills: [], soft_skills: []},
projects: [{title, description, url, technologies, start_date, end_date}],
certifications: [{name, issuer, date_obtained}],
languages: [{language}],
awards: [{title, issuer, date}],
social_media: [{name, url, description}],
work_samples: [{title, url, start_date}],
white_papers: [{title, url, description}],
presentations: [{title, url, description}],
patents: [{title, url, application_number}]

RESUME TEXT:
{resume_text}
"""

# ============================================================
# LLM NODE
# ============================================================

def process_chunks(state: ResumeState) -> ResumeState:
    # Explicitly set max_tokens to a safe value (e.g. 4000)
    # Prompt (~1000) + Max Tokens (4000) = 5000, well within 12000 limit.
    llm = ChatGroq(
        model=MODEL,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=4000
    )

    results = []

    for chunk in state["chunks"]:
        _logger.info("Processing chunk...")
        
        # Basic text cleaning to save tokens
        clean_chunk = re.sub(r'\s+', ' ', chunk).strip()

        response = llm.invoke([
            HumanMessage(content=EXTRACTION_PROMPT.format(resume_text=clean_chunk))
        ])

        parsed = parse_json_safe(response.content)
        results.append(parsed)

    return {**state, "partial_results": results}


# ============================================================
# MERGE NODE
# ============================================================

def merge_results(state: ResumeState) -> ResumeState:
    merged = {}

    for part in state["partial_results"]:
        merged = merge_dicts(merged, part)

    return {**state, "final_json": merged}


# ============================================================
# VALIDATION NODE
# ============================================================

def validate_schema(state: ResumeState) -> ResumeState:
    cleaned = state["final_json"]

    # sanitize minimal
    for exp in cleaned.get("experience", []):
        exp.setdefault("responsibilities", [])
        exp.setdefault("technologies", [])

    resume = ResumeData.model_validate(cleaned)

    return {**state, "final_json": resume.model_dump()}


# ============================================================
# GRAPH BUILD
# ============================================================

def build_graph():
    builder = StateGraph(ResumeState)

    builder.add_node("split", lambda s: {**s, "chunks": split_text(s["text"])})
    builder.add_node("process", process_chunks)
    builder.add_node("merge", merge_results)
    builder.add_node("validate", validate_schema)

    builder.set_entry_point("split")

    builder.add_edge("split", "process")
    builder.add_edge("process", "merge")
    builder.add_edge("merge", "validate")
    builder.add_edge("validate", END)

    return builder.compile()


graph = build_graph()


# ============================================================
# MAIN FUNCTION (IMPORTANT SAME NAME)
# ============================================================

def extract_resume_from_text(
    text: str,
    api_key: str,
    model_id: str = MODEL
) -> ResumeData:

    if not text.strip():
        raise ValueError("Empty text")

    os.environ["GROQ_API_KEY"] = api_key

    state = {
        "text": text,
        "chunks": [],
        "partial_results": [],
        "final_json": {}
    }

    result = graph.invoke(state)

    return ResumeData.model_validate(result["final_json"])