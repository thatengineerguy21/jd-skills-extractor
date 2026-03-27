from google.adk.agents import Agent

EXTRACTION_PROMPT = """
You are an expert HR analyst. When given a job description, extract and return ONLY a valid JSON object with this exact structure:
{
  "role_type": "string (e.g. Frontend Engineer, Data Scientist)",
  "experience_level": "string (Entry/Mid/Senior/Lead/Manager)",
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "domain": "string (e.g. FinTech, HealthTech, E-commerce)"
}
Do not include any explanation or markdown. Return only the JSON.
"""

root_agent = Agent(
    name="jd_skills_extractor_agent",
    model="gemini-2.5-flash",
    description="Extracts structured skills and role info from job descriptions.",
    instruction=EXTRACTION_PROMPT,
)