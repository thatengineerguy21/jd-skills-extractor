import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from jd_skills_extractor_app import agent

app = FastAPI()

session_service = InMemorySessionService()
runner = Runner(
    agent=agent.root_agent,
    app_name="jd_skills_extractor",
    session_service=session_service
)

@app.post("/extract")
async def extract_skills(request: Request):
    body = await request.json()
    job_description = body.get("job_description", "")

    if not job_description:
        return JSONResponse(
            status_code=400,
            content={"error": "job_description field is required"}
        )

    session = await session_service.create_session(
        app_name="jd_skills_extractor",
        user_id="user_1",
        session_id="session_1"
    )

    message = Content(parts=[Part(text=job_description)])

    response_text = ""
    async for event in runner.run_async(
        user_id="user_1",
        session_id="session_1",
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    try:
        # Look for the content specifically between ```json and ```
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        
        if json_match:
            # If found, parse just that extracted JSON string
            extracted_json_string = json_match.group(1)
            structured_data = json.loads(extracted_json_string)
            
            # You can return both the parsed data AND the full markdown 
            structured = {
                "parsed_data": structured_data,
                "full_markdown": response_text 
            }
        else:
            # Fallback if the agent didn't format it right
            structured = {"raw_response": response_text}
            
    except json.JSONDecodeError:
        structured = {"raw_response": response_text}

    return JSONResponse(content=structured)

@app.get("/health")
def health():
    return {"status": "ok"}