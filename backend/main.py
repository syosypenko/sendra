from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import db
from src.routes.auth_routes import router as auth_router
from src.routes.email_routes import router as email_router
from src.routes.analytics_routes import router as analytics_router
from src.routes.gmail_routes import router as gmail_router
from src.routes.collection_routes import router as collection_router

app = FastAPI(title="Sendra API", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    await db.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await db.close_db()


app.include_router(auth_router)
app.include_router(email_router)
app.include_router(analytics_router)
app.include_router(gmail_router)
app.include_router(collection_router)
