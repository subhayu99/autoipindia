from fastapi import FastAPI, Query, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from logic import (
    ingest_trademark_status,
    get_trademarks_to_ingest,
    TrademarkSearchParams,
    TrademarkWithStatus,
)
from config import API_TOKEN

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:8050",      # Dash frontend
        "http://127.0.0.1:3000",      # Alternative localhost
        "http://127.0.0.1:8050",      # Alternative localhost
        # Add your production frontend URLs here when deploying
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


@app.get("/ingest/all", response_model=dict)
async def ingest(
    stale_since_days: int = Query(
        15, description="Number of days since which trademarks should not have been ingested",
    ),
    token: str = Depends(verify_token),
):
    params = get_trademarks_to_ingest(stale_since_days)
    stats = ingest_trademark_status(
        params, max_workers=1, headless=True, write_each_to_db=True
    )
    return stats


@app.get("/ingest/tm", response_model=dict)
async def ingest_trademark(
    tm: TrademarkSearchParams,
    token: str = Depends(verify_token),
):
    return ingest_trademark_status(
        [tm], max_workers=1, headless=True, write_each_to_db=True
    )


@app.get("/ingest/tm/{application_number}", response_model=dict)
async def ingest_by_application_number(
    application_number: str,
    token: str = Depends(verify_token),
):
    return ingest_trademark_status(
        [TrademarkSearchParams(application_number=application_number)],
        max_workers=1,
        headless=True,
        write_each_to_db=True,
    )


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
