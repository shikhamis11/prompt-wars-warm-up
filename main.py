import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from google import genai
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable is not set.")
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Cannot initialize Gemini client.")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


# Pydantic model for incoming trip requests
class TripRequest(BaseModel):
    destination: str = Field(..., min_length=1, max_length=100, description="The desired travel destination.")
    duration: str = Field(..., min_length=1, max_length=50, description="The duration of the trip (e.g., '7 days', '2 weeks').")
    preferences: str = Field(default="", max_length=500, description="User's travel preferences (e.g., 'local food', 'hiking').")
    constraints: str = Field(default="", max_length=500, description="Travel constraints or budget (e.g., 'mid-range budget', 'vegetarian friendly').")


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

    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # Use the defined constant for the model and await the coroutine to get the async iterator
            stream_response = await client.aio.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            async for chunk in stream_response:
                if chunk.text:
                    data = json.dumps(chunk.text)
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.01)
        except genai.errors.APIError as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            error_msg = json.dumps(f"ERROR: An issue occurred with the AI service. Please try again later.")
            yield f"data: {error_msg}\n\n"
            raise HTTPException(status_code=500, detail="AI service error") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during trip plan generation.")
            error_msg = json.dumps(f"ERROR: An unexpected server error occurred. Please try again.")
            yield f"data: {error_msg}\n\n"
            raise HTTPException(status_code=500, detail="Internal server error") from e

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )

# Serve static files from the "static" directory - mount at the end to avoid intercepting API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static_files")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    