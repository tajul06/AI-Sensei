from slowapi import Limiter
from slowapi.util import get_remote_address

def get_user_key(request):
    return getattr(request.state, "user_id", None) or get_remote_address(request)

limiter = Limiter(key_func=get_user_key)