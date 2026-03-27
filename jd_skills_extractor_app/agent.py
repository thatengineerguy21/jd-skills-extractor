from google.adk.agents import Agent

EXTRACTION_PROMPT = """
You are an expert HR analyst and job description parser.

When given a job description, extract and return the following in valid JSON format:
{
  "role_type": "string (e.g. Backend Engineer, Data Scientist, Product Manager)",
  "experience_level": "string (e.g. Junior 0-2 years, Mid-level 3-5 years, Senior 5+ years)",
  "required_skills": ["list", "of", "must-have", "skills"],
  "nice_to_have_skills": ["list", "of", "optional", "skills"],
  "domain": "string (e.g. Fintech, Healthcare, E-commerce, General)",
  "summary": "2-3 sentence plain English summary of the role and what they are looking for"
}

Rules:
- If experience level is not explicitly mentioned, infer it from context clues like seniority title or years mentioned.
- If nice-to-have skills are not mentioned, return an empty list.
- Keep required_skills and nice_to_have_skills as short skill names, not full sentences.
- Always return valid JSON. No markdown, no explanation outside the JSON.
"""

root_agent = Agent(
    name="job_skills_extractor_agent",
    model="gemini-2.5-flash",
    description="Extracts structured skills, experience level, and role type from job descriptions.",
    instruction=EXTRACTION_PROMPT,
)