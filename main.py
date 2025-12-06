from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

# ---------------------------
# FastAPI App
# ---------------------------
app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------
# File Paths (Free-tier Safe)
# ---------------------------
CLICKS_FILE = "clicks.json"     # saved inside project folder
RESUME_FILE = "Resume.pdf"      # your resume file

# Ensure clicks.json exists
if not os.path.exists(CLICKS_FILE):
    with open(CLICKS_FILE, "w") as f:
        json.dump({}, f, indent=4)


# ---------------------------
# Helper Functions
# ---------------------------
def load_clicks():
    try:
        return json.load(open(CLICKS_FILE, "r"))
    except:
        return {}


def save_clicks(data):
    with open(CLICKS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------
# Resume Page + Tracking
# ---------------------------
@app.get("/resume", response_class=HTMLResponse)
async def resume(id: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    data = load_clicks()
    data.setdefault(id, []).append(ts)
    save_clicks(data)

    html = f"""
    <html>
    <head>
        <title>Resume - Rahmat Ali</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 30px;
                text-align: center;
            }}
            .card {{
                background: white;
                max-width: 600px;
                margin: auto;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 18px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }}
            a:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Resume for: {id}</h2>
            <p>Thank you for viewing my resume.</p>
            <a href="/download_resume?id={id}">
                Download Resume (PDF)
            </a>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


# ---------------------------
# Download Resume
# ---------------------------
@app.get("/download_resume")
async def download_resume(id: str):
    if not os.path.exists(RESUME_FILE):
        return JSONResponse({"error": "Resume.pdf NOT found"}, status_code=404)

    return FileResponse(
        RESUME_FILE,
        media_type="application/pdf",
        filename="Rahmat_Ali_Resume.pdf"
    )


# ---------------------------
# Stats Endpoint (Dashboard uses this)
# ---------------------------
@app.get("/stats")
async def stats():
    data = load_clicks()
    total_clicks = sum(len(v) for v in data.values())

    return {
        "status": "running",
        "total_clicks": total_clicks,
        "unique_users": len(data),
        "entries": data
    }


# ---------------------------
# Home Endpoint
# ---------------------------
@app.get("/")
async def home():
    return {
        "status": "online",
        "message": "Resume Tracker running on Render FREE Tier"
    }
