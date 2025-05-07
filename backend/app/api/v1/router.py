from fastapi import APIRouter

from .endpoints import users

router = APIRouter()

# from .endpoints import auth, events, tags

# router.include_router(auth.router, prefix="/auth", tags=["auth"])
# router.include_router(events.router, prefix="/events", tags=["events"])
# router.include_router(tags.router, prefix="/tags", tags=["tags"])
router.include_router(users.router, prefix="/users", tags=["users"])
