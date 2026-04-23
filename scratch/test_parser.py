import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chain.CV_data_chain import get_cv_data_from_openrouter_model

def test_long_cv(char_count):
    print(f"Testing CV with {char_count} characters...")
    # Generate a mock CV text
    header = "John Doe\nSoftware Engineer\njohn@example.com\n123-456-7890\n\nSummary:\nExperienced engineer.\n\nExperience:\n- Senior Dev at ABC Corp (2020 - Present)\n- Junior Dev at XYZ Inc (2018 - 2020)\n\nEducation:\n- BS Computer Science (2014 - 2018)\n\nSkills:\nPython, JavaScript, SQL\n\n"
    filler = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    
    cv_text = header
    while len(cv_text) < char_count:
        cv_text += filler
    cv_text = cv_text[:char_count]
    
    try:
        res = get_cv_data_from_openrouter_model(cv_text)
        print("Success! Extracted keys:", list(res.keys()))
    except Exception as e:
        print(f"Failed for {char_count} chars.")
        traceback.print_exc()

if __name__ == "__main__":
    test_long_cv(5531)
    test_long_cv(6063)
