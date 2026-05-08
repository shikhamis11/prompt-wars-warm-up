import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from pydantic import BaseModel

app = FastAPI()

# Initialize the Gemini client
# Make sure to set GOOGLE_API_KEY in your environment variables
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class TripRequest(BaseModel):
    destination: str
    duration: str
    preferences: str
    constraints: str

@app.post("/api/plan-trip")
async def plan_trip(request: TripRequest):
    prompt = f"""
    Plan a trip to {request.destination} for {request.duration}.
    User Preferences: {request.preferences}
    Constraints and Budget: {request.constraints}
    
    Provide a detailed day-by-day itinerary with suggestions for activities, 
    dining, and travel tips. Format the output using Markdown.
    """

    async def generate_stream():
        try:
            # Using gemini-2.0-flash for high-speed streaming generation
            response = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            for chunk in response:
                if chunk.text:
                    # SSE format: data: <content>\n\n
                    yield f"data: {chunk.text}\n\n"
                await asyncio.sleep(0.01) # Small delay to ensure smooth streaming
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

# Serve static files (index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)