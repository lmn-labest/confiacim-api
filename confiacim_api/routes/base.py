from fastapi import APIRouter

router = APIRouter(tags=["Base"])


@router.get("/")
def index():
    return {"message": "Api do confiacim"}
