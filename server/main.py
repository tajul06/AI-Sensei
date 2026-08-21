from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exceptions_middleware
from api.upload_pdf import router as upload_pdf_router
from api.user_qs import router as user_qs_router



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
app.middleware("http")(catch_exceptions_middleware)

#1,UPload PDF route
app.include_router(upload_pdf_router)

#2,User Q&A route
app.include_router(user_qs_router)