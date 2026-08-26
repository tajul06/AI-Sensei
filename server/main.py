from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import  _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from middlewares.exception_handlers import catch_exceptions_middleware
from api.upload_pdf import router as upload_pdf_router
from api.user_qs import router as user_qs_router
from api import chat_sessions
from api import health 
from api import uploaded_files
from services.limiter import limiter


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

def get_user_key(request):

    return getattr(request.state, "user_id",None) or get_remote_address(request)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#1,UPload PDF route
app.include_router(upload_pdf_router)
app.include_router(uploaded_files.router)

#2,User Q&A route
app.include_router(user_qs_router)
#3,Chat sessions route
app.include_router(chat_sessions.router)
#4,Health check route
app.include_router(health.router)