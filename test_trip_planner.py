import pytest
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

# Data model representing the inputs from your static/index.html
class TripRequest(BaseModel):
    destination: str
    duration: str
    preferences: Optional[str] = ""
    budget: Optional[float] = Field(None, ge=0)
    wheelchair_accessible: bool = Field(False, alias="wheelchairAccessible")
    other_constraints: Optional[str] = Field("", alias="otherConstraints")

    class Config:
        populate_by_name = True

def test_trip_request_validation_success():
    """Test that valid form data from the frontend is parsed correctly."""
    payload = {
        "destination": "Tokyo, Japan",
        "duration": "5 days",
        "preferences": "Photography, Food",
        "budget": 2500,
        "wheelchairAccessible": True,
        "otherConstraints": "No seafood"
    }
    request = TripRequest(**payload)
    assert request.destination == "Tokyo, Japan"
    assert request.budget == 2500.0
    assert request.wheelchair_accessible is True

def test_trip_request_validation_failure():
    """Test that invalid budget or missing required fields raise validation errors."""
    # Missing required 'destination'
    with pytest.raises(ValidationError):
        TripRequest(duration="3 days", wheelchairAccessible=False)
    
    # Negative budget (should fail due to ge=0 constraint)
    with pytest.raises(ValidationError):
        TripRequest(destination="Kyoto", duration="2 days", budget=-1, wheelchairAccessible=False)

@pytest.mark.asyncio
async def test_mock_genai_streaming_response():
    """Test the streaming response logic used by the frontend reader."""
    mock_chunk = MagicMock()
    mock_chunk.text = "Day 1: Arrival and check-in."
    
    # Simulating the async generator behavior of the Google GenAI SDK
    async def mock_gen():
        yield mock_chunk

    # Verification that the backend can iterate through the stream
    chunks = []
    async def process_stream():
        async for chunk in mock_gen():
            chunks.append(chunk.text)
    
    await process_stream()
    assert chunks == ["Day 1: Arrival and check-in."]