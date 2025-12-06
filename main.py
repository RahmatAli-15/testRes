from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Persistent disk path on Render
DATA_DIR = "/data"
CLICKS_FILE = os.path.join(DATA_DIR, "clicks.json")
RESUME_FILE = "Resume.pdf"

# Ensure persistent data folder exists
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

# Ensure click log file exists
if not os.path.exists(CLICKS_FILE):
    with open(CLICKS_FILE, "w") as f:
        json.dump({}, f, indent=4)


def load_clicks():
    try:
        return json.load(open(CLICKS_FILE))
    except:
        return {}


def save_clicks(data):
    json.dump(data, open(CLICKS_FILE, "w"), indent=4)


@app.get("/resume", response_class=HTMLResponse)
async def resume_page(request: Request, id: str):
    """Track resume views + show HTML page"""

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


@app.get("/download_resume")
async def download_resume(id: str):
    """Serve PDF resume"""

    if not os.path.exists(RESUME_FILE):
        return {"error": "Resume.pdf not found"}

    return FileResponse(
        RESUME_FILE,
        media_type="application/pdf",
        filename="Rahmat_Ali_Resume.pdf"
    )


@app.get("/stats")
async def stats():
    """Return click tracking stats for dashboard"""

    data = load_clicks()
    total_clicks = sum(len(v) for v in data.values())

    return {
        "status": "running",
        "total_clicks": total_clicks,
        "unique_users": len(data),
        "entries": data
    }


@app.get("/")
async def home():
    return {"status": "online", "message": "Resume Tracker API running on Render!"}
