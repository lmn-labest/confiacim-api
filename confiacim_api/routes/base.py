from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Base"])


@router.get("/")
def index():
    return {"message": "Api do confiacim"}
