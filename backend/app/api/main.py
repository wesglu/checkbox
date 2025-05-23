from fastapi import APIRouter

from app.api.routes import auth, check


router = APIRouter()

router.include_router(auth.router)
router.include_router(check.router)
