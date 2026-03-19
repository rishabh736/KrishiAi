import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize the FastAPI app
app = FastAPI(title="Baranaja AI Backend")

# Setup CORS to allow your HTML/JS frontend to communicate with this backend
# For the hackathon, we allow all origins ("*"). In production, put your frontend URL here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected data structure from your frontend
class FarmLocation(BaseModel):
    latitude: float
    longitude: float

# A sample endpoint to test the connection and return data
@app.post("/api/predict-yield")
async def predict_yield(location: FarmLocation):
    try:
        # Since Earth Engine is removed, we will use mock data for now.
        # You can add your standard Machine Learning model prediction logic here later.
        mock_elevation = 1200 
        
        # Return the data to your frontend
        return {
            "status": "success",
            "coordinates": {"lat": location.latitude, "lon": location.longitude},
            "elevation_meters": mock_elevation,
            "message": "Connected to backend successfully! Ready for your ML model."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# A simple health check endpoint
@app.get("/")
def read_root():
    return {"message": "Baranaja AI API is up and running!"}