from fastapi import FastAPI, Query, HTTPException, Security, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from typing import List, Optional
import secrets
import io
import pandas as pd
from logic import (
    ingest_trademark_status,
    get_trademarks_to_ingest,
    TrademarkSearchParams,
    TrademarkWithStatus,
)
from logic.csv_import import process_csv_upload, CSVImportError
from config import API_TOKEN, LOG_LEVEL, CORS_ORIGINS
from jobs import job_manager
from logger import setup_logger
from rate_limiter import rate_limit_middleware
from models import BulkDeleteRequest

# Set up logger
logger = setup_logger(__name__, LOG_LEVEL)


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,       # Allow all configured origins
    allow_credentials=True,           # Allow credentials (e.g., cookies)
    allow_methods=["*"],              # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],              # Allow all headers including Authorization
)

logger.info(f"CORS enabled for origins: {CORS_ORIGINS}")

security = HTTPBearer()


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Does not require authentication.
    """
    from db import engine
    from sqlalchemy import text

    # Check database connection
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")

    response = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "database": db_status,
        "service": "autoipindia-api"
    }

    status_code = 200 if db_status == "healthy" else 503
    return response if status_code == 200 else HTTPException(status_code=status_code, detail=response)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the Bearer token matches the configured API_TOKEN.
    Raises HTTPException if token is invalid or missing.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="API_TOKEN not configured on server"
        )

    if not secrets.compare_digest(credentials.credentials, API_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return credentials.credentials


def run_ingestion_job(job_id: str, params: List[TrademarkSearchParams]):
    """Background task to run trademark ingestion"""
    try:
        logger.info(f"Starting ingestion job {job_id} with {len(params)} trademarks")
        job_manager.start_job(job_id)
        result = ingest_trademark_status(
            params, max_workers=1, headless=True, write_each_to_db=True
        )
        job_manager.complete_job(job_id, result)
        logger.info(f"Completed ingestion job {job_id}: {result}")
    except Exception as e:
        logger.error(f"Failed ingestion job {job_id}: {str(e)}", exc_info=True)
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


@app.post("/import/csv")
async def import_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(verify_token),
):
    """
    Import trademarks from CSV file and start background ingestion job.

    Expected CSV formats:
    1. application_number only:
       ```
       application_number
       1234567
       2345678
       ```

    2. wordmark and class_name:
       ```
       wordmark,class_name
       NIKE,25
       APPLE,9
       ```

    3. All fields (application_number, wordmark, class_name)

    Returns job_id for tracking the ingestion progress.
    """
    # Check if we can start a new job
    if not job_manager.can_start_job():
        running_count = len(job_manager.get_running_jobs())
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({job_manager.max_concurrent_jobs}) reached. Currently running: {running_count}"
        )

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )

    try:
        # Read file content
        content = await file.read()
        file_content = content.decode('utf-8')

        # Process CSV and validate
        result = process_csv_upload(file_content)

        # Check if there are any valid trademarks
        if result['valid_count'] == 0:
            raise HTTPException(
                status_code=400,
                detail=f"No valid trademarks found in CSV. Errors: {result['errors']}"
            )

        # Convert trademarks back to TrademarkSearchParams objects
        params = [TrademarkSearchParams(**tm) for tm in result['trademarks']]

        # Create job
        job = job_manager.create_job(
            job_type="ingest_csv",
            params={
                "filename": file.filename,
                "valid_count": result['valid_count'],
                "error_count": result['error_count'],
                "errors": result['errors'][:10] if result['errors'] else []  # Limit errors to first 10
            }
        )

        # Start background task
        background_tasks.add_task(run_ingestion_job, job.id, params)

        return {
            "job_id": job.id,
            "status": "started",
            "message": f"CSV import started for {result['valid_count']} trademarks",
            "valid_count": result['valid_count'],
            "error_count": result['error_count'],
            "errors": result['errors'][:10] if result['errors'] else []  # Return first 10 errors
        }

    except CSVImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CSV file: {str(e)}"
        )


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


@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, token: str = Depends(verify_token)):
    """
    Cancel a running or pending job.
    Note: Cancellation is cooperative - the background task must check cancellation status.
    """
    success = job_manager.cancel_job(job_id)

    if success:
        logger.info(f"Job {job_id} cancelled successfully")
        return {"success": True, "message": f"Job {job_id} has been cancelled"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Job not found or already completed/failed"
        )


# Trademark retrieval endpoints
@app.get("/retrieve/all", response_model=list[TrademarkWithStatus])
async def retrieve(token: str = Depends(verify_token)):
    """Get all trademarks (non-paginated). Consider using /retrieve/paginated for large datasets."""
    return TrademarkWithStatus.get_all(as_df=False)


@app.get("/retrieve/paginated")
async def retrieve_paginated(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    wordmark: Optional[str] = Query(None, description="Filter by wordmark (partial match)"),
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    status: Optional[str] = Query(None, description="Filter by status (partial match)"),
    application_number: Optional[str] = Query(None, description="Filter by application number (partial match)"),
    token: str = Depends(verify_token),
):
    """
    Get paginated trademarks with optional filters.

    Supports filtering by:
    - wordmark (partial, case-insensitive)
    - class_name (exact match)
    - status (partial, case-insensitive)
    - application_number (partial match)

    Returns paginated results with metadata.
    """
    return TrademarkWithStatus.get_paginated_with_filters(
        page=page,
        page_size=page_size,
        wordmark=wordmark,
        class_name=class_name,
        status=status,
        application_number=application_number,
        as_df=False
    )


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


@app.post("/delete/bulk")
async def bulk_delete_trademarks(
    request: BulkDeleteRequest,
    token: str = Depends(verify_token),
):
    """
    Bulk delete trademarks by application numbers.

    Request body:
    {
        "application_numbers": ["123456", "234567", "345678"]
    }
    """
    logger.info(f"Bulk delete request for {len(request.application_numbers)} trademarks")
    result = TrademarkWithStatus.bulk_delete_by_application_numbers(request.application_numbers)

    return result


@app.get("/export/csv")
async def export_trademarks_csv(
    token: str = Depends(verify_token),
):
    """
    Export all trademarks to CSV file.
    Returns a downloadable CSV file with all trademark data.
    """
    logger.info("Exporting trademarks to CSV")

    try:
        # Get all trademarks as DataFrame
        trademarks = TrademarkWithStatus.get_all(as_df=True)

        if trademarks.empty:
            raise HTTPException(
                status_code=404,
                detail="No trademarks found to export"
            )

        # Convert to CSV
        output = io.StringIO()
        trademarks.to_csv(output, index=False)
        output.seek(0)

        # Return as streaming response
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=trademarks_export.csv"
            }
        )

    except Exception as e:
        logger.error(f"Error exporting trademarks to CSV: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export trademarks: {str(e)}"
        )


@app.get("/export/excel")
async def export_trademarks_excel(
    token: str = Depends(verify_token),
):
    """
    Export all trademarks to Excel file.
    Returns a downloadable Excel file with all trademark data.
    """
    logger.info("Exporting trademarks to Excel")

    try:
        # Get all trademarks as DataFrame
        trademarks = TrademarkWithStatus.get_all(as_df=True)

        if trademarks.empty:
            raise HTTPException(
                status_code=404,
                detail="No trademarks found to export"
            )

        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            trademarks.to_excel(writer, index=False, sheet_name='Trademarks')

        output.seek(0)

        # Return as streaming response
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=trademarks_export.xlsx"
            }
        )

    except Exception as e:
        logger.error(f"Error exporting trademarks to Excel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export trademarks: {str(e)}"
        )


@app.get("/history/tm/{application_number}", response_model=list[TrademarkWithStatus])
async def get_history_by_application_number(
    application_number: str,
    token: str = Depends(verify_token),
):
    return TrademarkWithStatus.get_history_by_application_number(application_number)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
