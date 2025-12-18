from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import events, security, cp, analytics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/events")
app.include_router(security.router, prefix="/security")
app.include_router(cp.router, prefix="/cp")
app.include_router(analytics.router, prefix="/analytics")
