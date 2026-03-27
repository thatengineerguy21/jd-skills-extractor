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
        structured = json.loads(response_text)
    except json.JSONDecodeError:
        structured = {"raw_response": response_text}

    return JSONResponse(content=structured)

@app.get("/health")
def health():
    return {"status": "ok"}