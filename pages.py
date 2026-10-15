# routes/pages.py
# Routes that return HTML pages (the landing page).
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@router.get("/")
def landing_page():
    # send the index.html file to the browser
    return FileResponse(STATIC_DIR / "index.html")
