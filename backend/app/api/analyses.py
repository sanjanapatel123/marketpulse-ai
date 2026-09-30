from fastapi import APIRouter, BackgroundTasks, status

from app.models.schemas import (
    CreateAnalysisRequest,
    CreateAnalysisResponse,
)
from app.services.analysis_service import create_analysis
from app.services.run_generation_service import generate_run

router = APIRouter(
    prefix="/api/analyses",
    tags=["Analyses"],
)


@router.post(
    "",
    response_model=CreateAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_analysis(
    payload: CreateAnalysisRequest,
    background_tasks: BackgroundTasks,
) -> CreateAnalysisResponse:
    result = await create_analysis(payload)

    background_tasks.add_task(
        generate_run,
        result.run_id,
    )

    return result