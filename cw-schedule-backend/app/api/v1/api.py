from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    schedules,
    friends,
    shared_schedules,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    schedules.router, prefix="/schedules", tags=["schedules"]
)
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(
    shared_schedules.router,
    prefix="/shared-schedules",
    tags=["shared-schedules"],
)
