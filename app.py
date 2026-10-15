# api.py
# The entry point. It creates the FastAPI app and plugs all the route files into it.
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import init_db
from routes import pages, users, concepts, contact, collaborations, talents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once when the server starts: make sure the tables exist
    init_db()
    yield


app = FastAPI(title="LinkupMates_backend", lifespan=lifespan)

# CORS lets a page opened from somewhere else (e.g. your old index.html
# double-clicked from your folder) call this API from the browser.
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# plug in each router
api.include_router(pages.router)
api.include_router(users.router)
api.include_router(concepts.router)
api.include_router(contact.router)
api.include_router(collaborations.router)
api.include_router(talents.router)

# serve any other files in /static (css, js, other html pages) at /static/...
api.mount("/static", StaticFiles(directory="static"), name="static")
