from fastapi import APIRouter

router = APIRouter()



@router.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """
    Lightweight health check — used by uptime pingers (e.g. UptimeRobot) to
    keep the Render instance from spinning down after inactivity.
    
    """
    return {"status": "ok"}