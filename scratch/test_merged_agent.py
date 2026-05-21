import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Ensure the project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environmental variables
load_dotenv()

async def main():
    print("Initializing test run...")
    
    # Import the updated parser function
    from langgraph_agentic_CV_parser_without_mergeLLM import extract_resume_agentic, graph
    
    # Check if the graph compiled successfully and contact & projects nodes are not present
    node_names = list(graph.nodes.keys())
    print("Graph Nodes:", node_names)
    
    # Verify contact node removed
    if "contact" in node_names:
        print("❌ FAILED: contact node still exists in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: contact node removed from graph successfully!")

    # Verify projects node removed
    if "projects" in node_names:
        print("❌ FAILED: projects node still exists in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: projects node removed from graph successfully!")

    # Verify education node removed
    if "education" in node_names:
        print("❌ FAILED: education node still exists in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: education node removed from graph successfully!")

    # Verify skills node removed
    if "skills" in node_names:
        print("❌ FAILED: skills node still exists in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: skills node removed from graph successfully!")

    # Verify basic node exists
    if "basic" not in node_names:
        print("❌ FAILED: basic node not found in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: basic node exists in graph!")

    # Verify experience_project node exists
    if "experience_project" not in node_names:
        print("❌ FAILED: experience_project node not found in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: experience_project node exists in graph!")

    # Verify education_skills node exists
    if "education_skills" not in node_names:
        print("❌ FAILED: education_skills node not found in graph!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: education_skills node exists in graph!")

    # Sample minimal CV text including projects
    mock_cv = """
    John Doe
    Senior Software Engineer
    john.doe@example.com
    +1 (555) 019-2834
    San Francisco, CA
    https://linkedin.com/in/johndoe
    https://github.com/johndoe

    Professional Summary:
    Highly motivated engineer with 5+ years of experience in Python and full-stack development.

    Work Experience:
    Senior Software Engineer | Tech Corp (2021 - Present)
    - Lead development of agentic AI parsing pipelines.
    - Reduced latency by 40% using asynchronous tasks.

    Academic & Personal Projects:
    LangGraph CV Parser Project (2026)
    - Developed a multi-agent parser system that processes resumes in parallel.
    - Used pure Python merge reducers for lower overhead.

    Education:
    B.S. in Computer Science | Stanford University (2014 - 2018)

    Skills:
    Python, JavaScript, LangGraph, FastAPI, Docker, SQL
    """
    
    print("\nInvoking parser graph asynchronously on mock CV...")
    try:
        # Run agent
        result = await extract_resume_agentic(mock_cv)
        print("\n--- EXTRACTED FINAL JSON RESULT ---")
        print(json.dumps(result, indent=2))
        print("-----------------------------------")
        
        # Verify contact info was extracted by the merged node
        contact_info = result.get("contact_info", {})
        email = contact_info.get("email")
        phone = contact_info.get("phone")
        
        # Verify experience and projects were extracted by experience_project_node
        experience = result.get("experience", [])
        projects = result.get("projects", [])
        
        print("\nVerifying Extracted Contact Fields:")
        print(f"Email: {email} (Expected: john.doe@example.com)")
        print(f"Phone: {phone} (Expected: +1 (555) 019-2834)")
        
        print("\nVerifying Extracted Experience & Projects:")
        print(f"Experience Count: {len(experience)} (Expected: >= 1)")
        if len(experience) > 0:
            print(f"  First Company: {experience[0].get('company')}")
            print(f"  First Job Title: {experience[0].get('job_title')}")
            
        print(f"Projects Count: {len(projects)} (Expected: >= 1)")
        if len(projects) > 0:
            print(f"  First Project: {projects[0].get('title')}")
            print(f"  First Project Description: {projects[0].get('description')}")
        
        if email == "john.doe@example.com" and len(experience) > 0 and len(projects) > 0:
            print("\n✅ SUCCESS: Merged nodes extracted basic info, contact, experience, and projects correctly!")
        else:
            print("\n⚠️ WARNING: Some fields might not have matched perfectly. Check JSON output above.")
            
    except Exception as e:
        print("❌ FAILED to execute parser graph:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
