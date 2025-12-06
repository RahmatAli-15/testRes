from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI()

# ---------------------------
# Allow all origins (Render)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------
# Paths
# ---------------------------
RESUME_FILE = "Resume.pdf"
LOG_FILE = "views.json"


# ---------------------------
# Utility: Log views
# ---------------------------
def log_resume_view(email: str):
    if not os.path.exists(LOG_FILE):
        data = {}
    else:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)

    data[email] = {
        "views": data.get(email, {}).get("views", 0) + 1,
        "last_view": str(datetime.utcnow())
    }

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------
# Resume Endpoint (Public Link)
# ---------------------------
@app.get("/resume", response_class=HTMLResponse)
async def serve_resume(request: Request, id: str):

    # Log the view (email-based)
    log_resume_view(id)

    # HTML response with download link
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
            <a href="/download_resume?id={id}" download>
                Download Resume (PDF)
            </a>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


# ---------------------------
# Download PDF File
# ---------------------------
@app.get("/download_resume")
async def download_resume(id: str):
    if not os.path.exists(RESUME_FILE):
        return JSONResponse({"error": "Resume file not found"}, status_code=404)

    # Returning PDF resume
    return FileResponse(
        RESUME_FILE,
        media_type="application/pdf",
        filename="Rahmat_Ali_Resume.pdf"
    )


# ---------------------------
# Root message
# ---------------------------
@app.get("/")
async def home():
    return {"status": "online", "message": "Resume Tracker API running on Render!"}
