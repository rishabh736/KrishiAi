import os
import json
import httpx
import datetime
import gspread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai

app = FastAPI()

# 1. CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SAFE CONFIGURATION LOADER ---
# This prevents the app from crashing if keys are missing
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SHEETS_JSON = os.environ.get("GOOGLE_SHEETS_JSON")

# 2. Init Gemini
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("⚠️ WARNING: GEMINI_API_KEY missing!")

# 3. Init Google Sheets
db_sheet = None
if SHEETS_JSON:
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(SHEETS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Ensure the sheet name matches EXACTLY what is in Google Drive
        db_sheet = client.open("Krishi-Ai-Logs").sheet1
    except Exception as e:
        print(f"⚠️ Google Sheets Error: {e}")

# --- API ENDPOINTS ---

@app.get("/")
def health_check():
    return {
        "status": "Online",
        "ai_ready": model is not None,
        "db_ready": db_sheet is not None
    }

@app.get("/dashboard-data")
async def get_data(lat: float = 19.07, lon: float = 72.87):
    # Fetch Weather
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    async with httpx.AsyncClient() as client:
        w_res = await client.get(weather_url)
        weather = w_res.json().get("current_weather", {})

    # Generate AI Advice
    advice = "Weather data received. AI analysis pending..."
    if model:
        try:
            prompt = f"Short farming advice for {weather.get('temperature')}°C."
            res = model.generate_content(prompt)
            advice = res.text.strip()
        except:
            advice = "AI busy. Check back in a moment."

    # Log to Sheets
    if db_sheet:
        try:
            db_sheet.append_row([str(datetime.datetime.now()), lat, lon, weather.get('temperature'), advice])
        except:
            print("Failed to write to sheet")

    return {
        "weather": weather,
        "ai_advice": advice,
        "location": {"lat": lat, "lon": lon}
    }
