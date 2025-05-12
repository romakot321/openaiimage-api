from fastapi import APIRouter


router = APIRouter(prefix="/api/context", tags=["Context"])


@router.post("")
async def create_new_context():
    pass
