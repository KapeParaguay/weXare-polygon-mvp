from fastapi import APIRouter
from app.api import users, creator, worker, judge, external, reputation, skills, feed

api_router = APIRouter()
api_router.include_router(users.router, tags=["auth"])
api_router.include_router(creator.router, tags=["creator"])
api_router.include_router(worker.router, tags=["worker"])
api_router.include_router(judge.router, tags=["judge"])
api_router.include_router(external.router, tags=["external"])
api_router.include_router(reputation.router, tags=["reputation"])
api_router.include_router(skills.router, tags=["skills"])
api_router.include_router(feed.router, tags=["feed"])
