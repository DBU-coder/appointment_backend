from fastapi import APIRouter

from .auth import router as auth_router
from .patients import router as patients_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(patients_router)
