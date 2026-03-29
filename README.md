# JD Skills Extractor

An intelligent job description parser that extracts structured skills, experience levels, and role information using Google's Gemini AI model and the Google ADK (Agent Development Kit).

## Features

- **Automatic Skill Extraction**: Identifies required and nice-to-have skills from job descriptions
- **Structured Output**: Returns data in JSON format along with human-readable analysis
- **Role Analysis**: Extracts role type, experience level, and industry domain
- **Candidate Insights**: Provides actionable tips for candidates applying to roles
- **RESTful API**: ADK api_server-based HTTP endpoint for easy integration
- **Cloud Ready**: Docker support for deployment on Google Cloud Run

## Prerequisites

- **Python 3.12+**
- **Google Cloud Account** with billing enabled
- **Vertex AI API** enabled on your project
- **Google ADK Python SDK**
- **Docker** (for containerized deployment)

## Project Structure

```
jd_skills_extractor/
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container configuration
├── README.md                         # This file
└── jd_skills_extractor_app/
    ├── __init__.py
    └── agent.py                      # Agent definition and prompt
```

## Local Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd jd_skills_extractor
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside `jd_skills_extractor_app/`:

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### 5. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud config set project your-project-id
```

## Running Locally

### Option 1 — CLI (Interactive)

```bash
cd jd_skills_extractor
adk run jd_skills_extractor_app
```

Paste a job description at the prompt and press Enter to get the extracted output.

### Option 2 — Web UI

```bash
cd jd_skills_extractor
adk web .
```

Open Cloud Shell Web Preview on port 8000. Select `jd_skills_extractor_app` from the dropdown, start a new session, and paste your job description.

### Option 3 — HTTP API Server

**Terminal 1 — Start the server:**
```bash
cd jd_skills_extractor
adk api_server . --port 8080
```

**Terminal 2 — Create a session:**
```bash
SESSION_ID=$(curl -s -X POST http://127.0.0.1:8080/apps/jd_skills_extractor_app/users/user1/sessions \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Session ID: $SESSION_ID"
```

**Terminal 2 — Send a job description:**
```bash
curl -X POST http://127.0.0.1:8080/run \
  -H "Content-Type: application/json" \
  -d "{
    \"app_name\": \"jd_skills_extractor_app\",
    \"user_id\": \"user1\",
    \"session_id\": \"$SESSION_ID\",
    \"new_message\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"We are looking for a Senior Backend Engineer with 5+ years in Python and FastAPI. Must know PostgreSQL and Redis. Docker and Kubernetes is a plus. Fintech domain.\"}]
    }
  }"
```

## Sample Output

```
## 📋 Role Overview
- **Role Type:** Senior Backend Engineer
- **Experience Level:** Senior (5+ years)
- **Domain/Industry:** Fintech

## ✅ Required Skills
- **Python** – Core language for backend development
- **FastAPI** – Framework for building high-performance APIs
- **PostgreSQL** – Primary relational database
- **Redis** – Used for caching and session management
- **REST API design** – Essential for service communication

## 💡 Nice to Have Skills
- **Docker** – Containerization for deployment
- **Kubernetes** – Container orchestration at scale

## 🧠 Structured Data
{
  "role_type": "Senior Backend Engineer",
  "experience_level": "Senior 5+ years",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "REST API design"],
  "nice_to_have_skills": ["Docker", "Kubernetes"],
  "domain": "Fintech"
}

## 📝 Summary
This is a senior backend engineering role focused on building payment infrastructure
in a Fintech environment. The team is looking for someone with deep Python and API
design experience. Knowledge of containerization tools like Docker and Kubernetes
would be an advantage.

## 🎯 Candidate Fit Tips
- Highlight any experience with payment systems or financial APIs
- Showcase PostgreSQL and Redis projects in your portfolio
- Mention Docker/Kubernetes even if limited — it's a plus, not required
```

## Agent Architecture

The JD Skills Extractor is built on Google's Agent Development Kit (ADK).

### Components

1. **ADK API Server**
   - Provides the HTTP REST endpoint via `adk api_server`
   - Handles session creation and message routing
   - Returns structured JSON responses

2. **Agent** (`jd_skills_extractor_app/agent.py`)
   - `root_agent` powered by `gemini-2.5-flash` via Vertex AI
   - Configured with a structured `EXTRACTION_PROMPT`
   - Processes job descriptions and returns formatted analysis

3. **Session Service** (`InMemorySessionService`)
   - Manages user sessions
   - Maintains conversation context per request

### Request/Response Flow

![Sequence Diagram](https://github.com/thatengineerguy21/jd-skills-extractor/blob/main/images/sequence.png)

## Cloud Deployment (Google Cloud Run)

### IAM Setup

Before deploying, grant the required permissions to your service accounts:

```bash
export PROJECT_ID=your-project-id
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
export CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  --project=$PROJECT_ID

# Grant permissions to compute service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.reader"

# Grant permissions to Cloud Build service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/storage.admin"
```

### Option 1: Deploy to Cloud Run as REST API

Deploying the custom main.py application as a backend API:

```bash
gcloud run deploy jd-skills-extractor \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=your-project-id,GOOGLE_CLOUD_LOCATION=us-central1 \
  --project your-project-id
```

#### Test the Cloud Run Endpoint

Once deployed, Cloud Run provides a URL like:
```
https://jd-skills-extractor-xxxx-uc.a.run.app
```

**Create a session:**
```bash
SESSION_ID=$(curl -s -X POST https://your-cloud-run-url/apps/jd_skills_extractor_app/users/user1/sessions \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

**Send a job description:**
```bash
curl -X POST https://your-cloud-run-url/run \
  -H "Content-Type: application/json" \
  -d "{
    \"app_name\": \"jd_skills_extractor_app\",
    \"user_id\": \"user1\",
    \"session_id\": \"$SESSION_ID\",
    \"new_message\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"Your job description here\"}]
    }
  }"
```

### Option 2: Deploy the ADK Chat UI (Automated Web Interface)

Alternatively, if you want a ready-to-use, interactive web chat interface instead of a raw HTTP API, you can use the ADK's native deployment command. This wraps your agent in a UI automatically.

**1. Ensure the ADK CLI is installed in your terminal:**

If you receive an adk: command not found error in Cloud Shell, ensure your virtual environment is active and dependencies are installed so the CLI tool is available:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

**2. Run the ADK Deploy Command:**

Note: We target the jd_skills_extractor_app folder specifically so the ADK can correctly locate the agent.py file, rather than targeting the root . directory.

  ```bash
  adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=jd-skills-extractor-chat-ui \
  --with_ui \
  jd_skills_extractor_app \
  -- \
  --service-account=$SERVICE_ACCOUNT
  ```

  Once the deployment finishes, Cloud Run will provide a new URL that opens directly to an interactive chat application where you can paste job descriptions and chat directly with the AI.

### View Logs

```bash
gcloud run logs read jd-skills-extractor --project=your-project-id
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI backend | Yes |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | Yes |
| `GOOGLE_CLOUD_LOCATION` | GCP region (e.g. `us-central1`) | Yes |

## Customizing the Agent

The agent's behavior is defined in `jd_skills_extractor_app/agent.py`.

### Modify the Extraction Prompt

Edit the `EXTRACTION_PROMPT` variable in `agent.py` to customize output format, extracted fields, or response structure.

### Change the AI Model

```python
root_agent = Agent(
    name="job_skills_extractor_agent",
    model="gemini-2.5-flash",  # Change to gemini-2.5-pro for more complex analysis
    ...
)
```

## Troubleshooting

### 403 PERMISSION_DENIED — Vertex AI
Enable the Vertex AI API and ensure billing is active:
```bash
gcloud services enable aiplatform.googleapis.com --project=your-project-id
```

### 403 BILLING_DISABLED
Enable billing at:
```
https://console.developers.google.com/billing/enable?project=your-project-id
```

### Session not found
Always create a session before calling `/run`. Sessions are in-memory and are lost when the server restarts.

### Cloud Run deployment — storage permission error
```bash
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"
```

### ADK Deploy "ValueError: No root_agent found"

If the ADK deploy command fails to find your agent, ensure you are pointing the command to the directory containing your agent.py file (e.g., jd_skills_extractor_app), rather than the root directory.

## Dependencies

- `google-adk` — Google Agent Development Kit
- `toolbox-core` — MCP Toolbox client (if using external tools)

See `requirements.txt` for the complete list.
