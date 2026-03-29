import os
import json
import re
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # <-- FIXED: Added this import
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from jd_skills_extractor_app import agent

app = FastAPI()

# Add CORS middleware so your HTML UI can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

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
    
    unique_session_id = f"session_{uuid.uuid4().hex[:8]}"

    session = await session_service.create_session(
        app_name="jd_skills_extractor",
        user_id="user_1",
        session_id=unique_session_id
    )

    message = Content(parts=[Part(text=job_description)])
    response_text = ""

    async for event in runner.run_async(
        user_id="user_1",
        session_id=unique_session_id,
        new_message=message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    # Default Fallback
    structured = {"raw_response": response_text}

    try:
        # Workaround: Use a variable for backticks so it doesn't break Markdown UI parsers
        bt = "```"
        pattern = rf'{bt}(?i:json)?\n(.*?)\n{bt}'
        json_match = re.search(pattern, response_text, re.DOTALL)
        
        if json_match:
            extracted_json_string = json_match.group(1).strip()
            structured_data = json.loads(extracted_json_string)
            structured = {
                "parsed_data": structured_data,
                "full_markdown": response_text 
            }
        else:
            # Fallback if no markdown block
            structured = {
                "parsed_data": json.loads(response_text),
                "full_markdown": response_text
            }
    except Exception as e:
        print(f"Parsing error: {e}")
        structured = {"raw_response": response_text}

    return JSONResponse(content=structured)

@app.get("/health")
def health():
    return {"status": "ok"}