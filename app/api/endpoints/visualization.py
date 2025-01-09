from fastapi import APIRouter
from app.services.analysis import perform_analysis

router = APIRouter()

@router.post("/")
async def vizualize(data: dict):
    result = perform_analysis(data)
    return {"analysis_result": result}
