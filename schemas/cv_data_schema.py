from typing import List, Optional
from pydantic import BaseModel, Field,field_validator

class ContactInfo(BaseModel):
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City, State, or Country location")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(default=None, description="Personal website or portfolio URL")
    address: Optional[str] = Field(default=None, description="Full residential or mailing address")
    alternative_phone: Optional[str] = Field(default=None, description="Alternative contact number")

    @field_validator("phone", "alternative_phone", mode="before")
    @classmethod
    def fix_phone(cls, v):
        if isinstance(v, list):
            return ", ".join(map(str, v))
        return v


class WorkExperience(BaseModel):
    company: Optional[str] = Field(default=None, description="Name of the company")
    job_title: Optional[str] = Field(default=None, description="Job title or role")
    location: Optional[str] = Field(default=None, description="Location of the job")
    start_date: Optional[str] = Field(default=None, description="Start date (e.g., 01/2018 or 2018)")
    end_date: Optional[str] = Field(default=None, description="End date or 'Present'")
    duration: Optional[str] = Field(default=None, description="Duration of employment (e.g., '2 years 3 months')")
    is_current_employment: Optional[bool] = Field(default=None, description="Whether this is the current employment")
    employment_type: Optional[str] = Field(default=None, description="Type of employment (e.g., Full-time, Contract)")
    salary: Optional[str] = Field(default=None, description="Salary or compensation")
    responsibilities: List[str] = Field(default_factory=list, description="List of responsibilities or achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies or skills used")
   
        # ✅ ADD THIS VALIDATOR HERE
    @field_validator("responsibilities", "technologies", mode="before")
    @classmethod
    def fix_list(cls, v):
        if v is None:
            return []
        return v


class Education(BaseModel):
    education_level: Optional[str] = Field(default=None, description="Education level (e.g., 10th, 12th, Graduation)")
    institution: Optional[str] = Field(default=None, description="Name of the university or institution")
    field_of_study: Optional[str] = Field(default=None, description="Major, field of study or specialization")
    course_type: Optional[str] = Field(default=None, description="Type of course (e.g., Full-time, Part-time, Distance)")
    passing_year: Optional[str] = Field(default=None, description="Year of passing")
    gpa: Optional[str] = Field(default=None, description="GPA or grade")
   
       # ✅ ADD THIS VALIDATOR HERE
    @field_validator("passing_year", mode="before")
    @classmethod
    def fix_year(cls, v):
        if isinstance(v, int):
            return str(v)
        return v

class Project(BaseModel):
    title: Optional[str] = Field(default=None, description="Project name")  # ✅ FIX
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @field_validator("technologies", mode="before")
    @classmethod
    def fix_list(cls, v):
        return v or []

class Certification(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the certification")
    issuer: Optional[str] = Field(default=None, description="Issuing organization")
    completion_id: Optional[str] = Field(default=None, description="Certification completion ID")
    url: Optional[str] = Field(default=None, description="URL to the certification")
    start_month: Optional[str] = Field(default=None, description="Month of certification start")
    start_year: Optional[str] = Field(default=None, description="Year of certification start")
    end_month: Optional[str] = Field(default=None, description="Month of certification completion")
    end_year: Optional[str] = Field(default=None, description="Year of certification completion")
    does_not_expire: Optional[bool] = Field(default=None, description="Whether this certification does not expire")
    date_obtained: Optional[str] = Field(default=None, description="Date the certification was obtained")

class Language(BaseModel):
    language: Optional[str] = Field(default=None, description="Language name")

class SkillSet(BaseModel):
    hard_skills: List[str] = Field(default_factory=list, description="Technical or hard skills")
    soft_skills: List[str] = Field(default_factory=list, description="Interpersonal or soft skills")

class Award(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the award or honor")
    issuer: Optional[str] = Field(default=None, description="Organization that issued the award")
    date: Optional[str] = Field(default=None, description="Date received")

class SocialMedia(BaseModel):
    name: Optional[str] = Field(default=None, description="Social media platform name")
    url: Optional[str] = Field(default=None, description="Profile URL")
    description: Optional[str] = Field(default=None, description="Profile description or bio")

class WorkSample(BaseModel):
    title: Optional[str] = Field(default=None, description="Work title")
    url: Optional[str] = Field(default=None, description="Link to the work sample")
    start_date: Optional[str] = Field(default=None, description="Duration from")
    duration_month: Optional[str] = Field(default=None, description="Duration in months")
    is_currently_working: Optional[bool] = Field(default=None, description="Whether currently working on this")
    total_duration: Optional[str] = Field(default=None, description="Work sample total duration")

class WhitePaper(BaseModel):
    title: Optional[str] = Field(default=None, description="White paper title")
    url: Optional[str] = Field(default=None, description="URL to the white paper")
    start_date: Optional[str] = Field(default=None, description="Duration from date")
    duration_month: Optional[str] = Field(default=None, description="Duration in months")
    description: Optional[str] = Field(default=None, description="Description of the white paper")

class Presentation(BaseModel):
    title: Optional[str] = Field(default=None, description="Presentation title")
    url: Optional[str] = Field(default=None, description="Presentation URL")
    description: Optional[str] = Field(default=None, description="Presentation description")

class Patent(BaseModel):
    title: Optional[str] = Field(default=None, description="Patent title")
    url: Optional[str] = Field(default=None, description="Patent URL")
    is_issued: Optional[bool] = Field(default=None, description="Whether the patent is issued")
    is_pending: Optional[bool] = Field(default=None, description="Whether the patent is pending")
    application_number: Optional[str] = Field(default=None, description="Patent application number")
    issue_year: Optional[str] = Field(default=None, description="Year of issue")
    issue_month: Optional[str] = Field(default=None, description="Month of issue")
    description: Optional[str] = Field(default=None, description="Patent description")


class CVSchema(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Full name of the candidate")
    gender: Optional[str] = Field(default=None, description="Gender of the candidate")
    dob: Optional[str] = Field(default=None, description="Date of birth of the candidate")
    religion: Optional[str] = Field(default=None, description="Religion of the candidate")
    marital_status: Optional[str] = Field(default=None, description="Marital status of the candidate")
    
    # Current Employment & Stats
    current_company: Optional[str] = Field(default=None, description="Current employer")
    current_designation: Optional[str] = Field(default=None, description="Current job title/designation")
    total_experience: Optional[str] = Field(default=None, description="Total work experience")
    relevant_experience: Optional[str] = Field(default=None, description="Relevant work experience")
    total_companies_worked: Optional[int] = Field(default=None, description="Number of companies worked for")
    
    # Location & Preferences
    current_country: Optional[str] = Field(default=None, description="Current country of residence")
    current_state: Optional[str] = Field(default=None, description="Current state of residence")
    current_city: Optional[str] = Field(default=None, description="Current city of residence")
    preferred_country: Optional[str] = Field(default=None, description="Preferred country for work")
    preferred_state: Optional[str] = Field(default=None, description="Preferred state for work")
    preferred_city: Optional[str] = Field(default=None, description="Preferred city for work")
    hometown: Optional[str] = Field(default=None, description="Hometown of the candidate")
    
    # Education Specifics
    graduation_degree: Optional[str] = Field(default=None, description="Graduation degree name")
    graduation_specialization: Optional[str] = Field(default=None, description="Graduation specialization")
    graduation_year: Optional[str] = Field(default=None, description="Year of passing graduation")
    post_graduation_degree: Optional[str] = Field(default=None, description="Post graduation degree name")
    post_graduation_specialization: Optional[str] = Field(default=None, description="Post graduation specialization")
    post_graduation_year: Optional[str] = Field(default=None, description="Year of passing post graduation")
    
    # Professional details
    department: Optional[str] = Field(default=None, description="Department of interest or current department")
    role: Optional[str] = Field(default=None, description="Primary role or target role")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    reason_for_change: Optional[str] = Field(default=None, description="Reason for seeking a job change")
    
    # Career Profile & Employment details
    is_permanent: Optional[bool] = Field(default=None, description="Interested in permanent jobs")
    is_contractual: Optional[bool] = Field(default=None, description="Interested in contractual jobs")
    is_full_time: Optional[bool] = Field(default=None, description="Interested in full-time employment")
    is_part_time: Optional[bool] = Field(default=None, description="Interested in part-time employment")
    preferred_shift: Optional[str] = Field(default=None, description="Preferred work shift (e.g., Day, Night)")
    preferred_work_locations: List[str] = Field(default_factory=list, description="List of preferred work locations")
    expected_ctc: Optional[str] = Field(default=None, description="Expected CTC")
    notice_period: Optional[str] = Field(default=None, description="Notice period in current company")
    status: Optional[str] = Field(default=None, description="Current status (e.g., Active, Inactive, Shortlisted)")
    remarks: Optional[str] = Field(default=None, description="Additional remarks or notes")

    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    contact_info: Optional[ContactInfo] = Field(default=None, description="Contact details")
    experience: List[WorkExperience] = Field(default_factory=list, description="Work experience history")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    skills: Optional[SkillSet] = Field(default=None, description="Candidate skills")
    projects: List[Project] = Field(default_factory=list, description="Personal or professional projects")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications obtained")
    languages: List[Language] = Field(default_factory=list, description="Languages spoken")
    awards: List[Award] = Field(default_factory=list, description="Awards and honors")
    social_media: List[SocialMedia] = Field(default_factory=list, description="Social media profiles")
    work_samples: List[WorkSample] = Field(default_factory=list, description="Work samples and portfolio items")
    white_papers: List[WhitePaper] = Field(default_factory=list, description="White papers authored")
    presentations: List[Presentation] = Field(default_factory=list, description="Presentations and talks")
    patents: List[Patent] = Field(default_factory=list, description="Patents applied or issued")

        # ✅ ADD THIS VALIDATOR HERE
    @field_validator("graduation_year", "post_graduation_year", mode="before")
    @classmethod
    def fix_years(cls, v):
        if isinstance(v, int):
            return str(v)
        return v

    @field_validator("industry", mode="before")
    @classmethod
    def fix_industry(cls, v):
        if isinstance(v, list):
            return ", ".join(map(str, v))
        return v

    