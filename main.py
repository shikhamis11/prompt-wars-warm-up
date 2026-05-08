import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY environment variable is not set. Please set it before running the application.")
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Cannot initialize Gemini client.")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


class TripRequest(BaseModel):
    destination: str
    duration: str
    preferences: str
    constraints: str


# Define constants
GEMINI_MODEL = "gemini-2.5-flash"

@app.post("/api/plan-trip")
async def plan_trip(request: TripRequest):
    """Generates a dynamic trip plan using Gemini with real-time streaming."""
    prompt = f"""
    Plan a trip to {request.destination} for {request.duration}.

    User Preferences:
    {request.preferences}

    Constraints and Budget:
    {request.constraints}

    Provide:
    - Day-by-day itinerary
    - Food recommendations
    - Travel tips
    - Estimated costs

    Format everything in Markdown.
    """

    async def generate_stream():
        try:
            # Use the defined constant for the model
            async for chunk in await client.aio.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt,
            ):
                if chunk.text:
                    data = json.dumps(chunk.text)
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.01)
        except genai.errors.APIError as e:
            logging.error(f"Gemini API error: {e}")
            error_msg = json.dumps(f"ERROR: An issue occurred with the AI service. Please try again later.")
            yield f"data: {error_msg}\n\n"
        except Exception as e:
            logging.exception("An unexpected error occurred during trip plan generation.")
            error_msg = json.dumps(f"ERROR: An unexpected server error occurred. Please try again.")
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


# Serve static files from the "static" directory
app.mount("/", StaticFiles(directory="static", html=True), name="static_files")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    