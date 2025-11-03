from fastapi import FastAPI, Query, HTTPException, Security, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from logic import (
    ingest_trademark_status,
    get_trademarks_to_ingest,
    TrademarkSearchParams,
    TrademarkWithStatus,
)
from config import API_TOKEN
from jobs import job_manager


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:8050",      # Dash frontend
        "http://127.0.0.1:3000",      # Alternative localhost
        "http://127.0.0.1:8050",      # Alternative localhost
        "https://subhayu99.github.io", # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],              # Allow all headers including Authorization
)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the Bearer token matches the configured API_TOKEN.
    Raises HTTPException if token is invalid or missing.
    """
    if not API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="API_TOKEN not configured on server"
        )

    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return credentials.credentials


def run_ingestion_job(job_id: str, params: List[TrademarkSearchParams]):
    """Background task to run trademark ingestion"""
    try:
        job_manager.start_job(job_id)
        result = ingest_trademark_status(
            params, max_workers=1, headless=True, write_each_to_db=True
        )
        job_manager.complete_job(job_id, result)
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@app.get("/ingest/all")
async def ingest(
    background_tasks: BackgroundTasks,
    stale_since_days: int = Query(
        15, description="Number of days since which trademarks should not have been ingested",
    ),
    token: str = Depends(verify_token),
):
    """Start background job to ingest stale trademarks"""
    # Check if we can start a new job
    if not job_manager.can_start_job():
        running_count = len(job_manager.get_running_jobs())
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({job_manager.max_concurrent_jobs}) reached. Currently running: {running_count}"
        )

    params = get_trademarks_to_ingest(stale_since_days)

    # Create job
    job = job_manager.create_job(
        job_type="ingest_all",
        params={"stale_since_days": stale_since_days, "count": len(params)}
    )

    # Start background task
    background_tasks.add_task(run_ingestion_job, job.id, params)

    return {
        "job_id": job.id,
        "status": "started",
        "message": f"Ingestion job started for {len(params)} trademarks"
    }


@app.get("/ingest/tm")
async def ingest_trademark(
    background_tasks: BackgroundTasks,
    wordmark: Optional[str] = None,
    class_name: Optional[str] = None,
    application_number: Optional[str] = None,
    token: str = Depends(verify_token),
):
    """Start background job to ingest a specific trademark"""
    if not job_manager.can_start_job():
        running_count = len(job_manager.get_running_jobs())
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({job_manager.max_concurrent_jobs}) reached. Currently running: {running_count}"
        )

    # Validate parameters
    if application_number:
        params = [TrademarkSearchParams(application_number=application_number)]
        job_params = {"application_number": application_number}
    elif wordmark and class_name:
        params = [TrademarkSearchParams(wordmark=wordmark, class_name=int(class_name))]
        job_params = {"wordmark": wordmark, "class_name": class_name}
    else:
        raise HTTPException(
            status_code=400,
            detail="Either application_number OR (wordmark and class_name) must be provided"
        )

    # Create job
    job = job_manager.create_job(job_type="ingest_single", params=job_params)

    # Start background task
    background_tasks.add_task(run_ingestion_job, job.id, params)

    return {
        "job_id": job.id,
        "status": "started",
        "message": "Ingestion job started"
    }


@app.get("/ingest/tm/{application_number}")
async def ingest_by_application_number(
    background_tasks: BackgroundTasks,
    application_number: str,
    token: str = Depends(verify_token),
):
    """Start background job to ingest by application number"""
    if not job_manager.can_start_job():
        running_count = len(job_manager.get_running_jobs())
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({job_manager.max_concurrent_jobs}) reached. Currently running: {running_count}"
        )

    params = [TrademarkSearchParams(application_number=application_number)]

    # Create job
    job = job_manager.create_job(
        job_type="ingest_single",
        params={"application_number": application_number}
    )

    # Start background task
    background_tasks.add_task(run_ingestion_job, job.id, params)

    return {
        "job_id": job.id,
        "status": "started",
        "message": f"Ingestion job started for {application_number}"
    }


# Job status endpoints
@app.get("/jobs")
async def get_all_jobs(token: str = Depends(verify_token)):
    """Get all jobs"""
    jobs = job_manager.get_all_jobs()
    return [job.to_dict() for job in jobs]


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str, token: str = Depends(verify_token)):
    """Get status of a specific job"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@app.get("/jobs/status/running")
async def get_running_jobs(token: str = Depends(verify_token)):
    """Get all currently running jobs"""
    jobs = job_manager.get_running_jobs()
    return [job.to_dict() for job in jobs]


# Trademark retrieval endpoints (unchanged)
@app.get("/retrieve/all", response_model=list[TrademarkWithStatus])
async def retrieve(token: str = Depends(verify_token)):
    return TrademarkWithStatus.get_all(as_df=False)


@app.get("/search/tm", response_model=TrademarkWithStatus)
async def search_by_wordmark_and_class(
    wordmark: str,
    class_name: str,
    token: str = Depends(verify_token),
):
    return TrademarkWithStatus.get_by_wordmark_and_class(wordmark, class_name)


@app.get("/search/tm/{application_number}", response_model=TrademarkWithStatus)
async def search_by_application_number(
    application_number: str,
    token: str = Depends(verify_token),
):
    return TrademarkWithStatus.get_by_application_number(application_number)


@app.delete("/delete/tm/{application_number}", response_model=dict)
async def delete_by_application_number(
    application_number: str,
    token: str = Depends(verify_token),
):
    return TrademarkWithStatus.delete_by_application_number(application_number)


@app.get("/history/tm/{application_number}", response_model=list[TrademarkWithStatus])
async def get_history_by_application_number(
    application_number: str,
    token: str = Depends(verify_token),
):
    return TrademarkWithStatus.get_history_by_application_number(application_number)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
