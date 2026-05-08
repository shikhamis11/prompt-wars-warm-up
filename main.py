import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


class TripRequest(BaseModel):
    destination: str
    duration: str
    preferences: str
    constraints: str


@app.post("/api/plan-trip")
async def plan_trip(request: TripRequest):

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
            # Updated supported model
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            for chunk in response:

                if hasattr(chunk, "text") and chunk.text:
                    # Safely encode streamed text
                    data = json.dumps(chunk.text)
                    yield f"data: {data}\n\n"

                await asyncio.sleep(0.01)

        except Exception as e:
            error_msg = json.dumps(f"ERROR: {str(e)}")
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


# Serve static frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )