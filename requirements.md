
# Dynamic Trip Planner Application Plan

## 1. Objective
Create a lightweight, web-based application that dynamically plans trips based on user preferences and constraints. The application will stream the generated plan in real-time to the user interface and will be packaged for deployment on Google Cloud Run.

## 2. Architecture & Tech Stack
*   **Backend:** Python with FastAPI. It's lightweight, supports asynchronous operations out-of-the-box, and is ideal for API development.
*   **AI Engine:** Google GenAI SDK (`google-genai`) using `GOOGLE_GENAI_MODEL` (defaults to `gemini-2.0-flash`) for fast, dynamic generation of trip plans.
*   **Real-time Updates:** Server-Sent Events (SSE) will be used to stream the model's response back to the client in real-time, providing immediate feedback.
*   **Frontend:** A single `index.html` file using Vanilla HTML/JS/CSS to keep the application as lightweight as possible without requiring a build step (like React or Vue).
*   **Deployment:** Docker to containerize the application, and Google Cloud Run for serverless deployment.

## 3. Implementation Steps

### Phase 1: Project Setup & Frontend
1.  Create the project structure:
    *   `main.py` (FastAPI application)
    *   `static/index.html` (Frontend UI)
    *   `requirements.txt` (Python dependencies)
    *   `Dockerfile` (Container configuration)
2.  Implement the frontend (`index.html`):
    *   Create a simple form to collect user inputs: Destination, Duration, Preferences (e.g., adventure, relaxation, food), and Constraints (e.g., budget, accessibility).
    *   Implement JavaScript to handle form submission, establish an `EventSource` connection for SSE, and dynamically update the DOM with the streamed response chunks.

### Phase 2: Backend & AI Integration
1.  Set up FastAPI in `main.py` to serve the static `index.html` file.
2.  Create an API endpoint (e.g., `/api/plan-trip`) that accepts the user parameters.
3.  Integrate the `google-genai` SDK. Construct a prompt incorporating the user's preferences and constraints.
4.  Utilize the model's streaming capabilities (`generate_content_stream`) to yield text chunks as they are generated.
5.  Format the yielded chunks as Server-Sent Events using `fastapi.responses.StreamingResponse`.

### Phase 3: Containerization & Deployment
1.  Write a `Dockerfile` that uses a lightweight Python base image (e.g., `python:3.11-slim`), installs dependencies, and runs the FastAPI application using Uvicorn.
2.  Provide the commands required to deploy the container to Google Cloud Run (the user will need to execute these or provide the necessary GCP credentials/project ID for the agent to execute them).

## 4. Verification
*   Locally run the application and verify that the frontend loads.
*   Submit a trip request and verify that the plan streams in real-time.
*   Verify that the plan adheres to the specified preferences and constraints.

## 5. Deployment Commands (For Execution Phase)
The following commands will be used to deploy the application:
```bash
gcloud config set project <YOUR_PROJECT_ID>
gcloud run deploy trip-planner --source . --region us-central1 --allow-unauthenticated
```
