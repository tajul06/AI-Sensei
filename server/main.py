from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exceptions_middleware
app = FastAPI(title="Ai Sensei", description="Ai Sensei API", version="1.0.0")

#cors setup

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=["*"],
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
#middleware exceptions handlers
