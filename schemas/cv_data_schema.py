from typing import List, Optional
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City, State, or Country location")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(default=None, description="Personal website or portfolio URL")
    address: Optional[str] = Field(default=None, description="Full residential or mailing address")


class WorkExperience(BaseModel):
    company: Optional[str] = Field(default=None, description="Name of the company")
    job_title: Optional[str] = Field(default=None, description="Job title or role")
    location: Optional[str] = Field(default=None, description="Location of the job")
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="End date or 'Present'")
    responsibilities: List[str] = Field(default_factory=list, description="List of responsibilities or achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies or skills used")

class Education(BaseModel):
    institution: Optional[str] = Field(default=None, description="Name of the university or institution")
    degree: Optional[str] = Field(default=None, description="Degree obtained (e.g., Bachelor of Science)")
    field_of_study: Optional[str] = Field(default=None, description="Major or field of study")
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="End date or expected graduation")
    gpa: Optional[str] = Field(default=None, description="GPA or grade")

class Project(BaseModel):
    name: Optional[str] = Field(default=None, description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    url: Optional[str] = Field(default=None, description="URL to the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in the project")

class Certification(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the certification")
    issuer: Optional[str] = Field(default=None, description="Issuing organization")
    date_obtained: Optional[str] = Field(default=None, description="Date the certification was obtained")

class Language(BaseModel):
    language: Optional[str] = Field(default=None, description="Language name")
    proficiency: Optional[str] = Field(default=None, description="Proficiency level (e.g., Native, Fluent, Beginner)")

class SkillSet(BaseModel):
    hard_skills: List[str] = Field(default_factory=list, description="Technical or hard skills")
    soft_skills: List[str] = Field(default_factory=list, description="Interpersonal or soft skills")

class Award(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the award or honor")
    issuer: Optional[str] = Field(default=None, description="Organization that issued the award")
    date: Optional[str] = Field(default=None, description="Date received")

class CVSchema(BaseModel):
    first_name: Optional[str] = Field(default=None, description="First name of the candidate")
    last_name: Optional[str] = Field(default=None, description="Last name of the candidate")
    gender: Optional[str] = Field(default=None, description="Gender of the candidate")
    dob: Optional[str] = Field(default=None, description="Date of birth of the candidate")
    religion: Optional[str] = Field(default=None, description="Religion of the candidate")
    marital_status: Optional[str] = Field(default=None, description="Marital status of the candidate")

    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    contact_info: Optional[ContactInfo] = Field(default=None, description="Contact details")
    experience: List[WorkExperience] = Field(default_factory=list, description="Work experience history")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    skills: Optional[SkillSet] = Field(default=None, description="Candidate skills")
    projects: List[Project] = Field(default_factory=list, description="Personal or professional projects")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications obtained")
    languages: List[Language] = Field(default_factory=list, description="Languages spoken")
    awards: List[Award] = Field(default_factory=list, description="Awards and honors")
