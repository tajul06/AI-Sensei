import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException, Request
from config.settings import SUPABASE_URL

_jwks_client = PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json")

def get_current_user(request : Request, authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.removeprefix("Bearer ")

    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token, 
            signing_key.key, 
            algorithms=["ES256","RS256"], 
            audience="authenticated",
            )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    user_id = payload.get("sub")
    request.state.user_id = user_id  # Store user_id in request state for later use
    return user_id