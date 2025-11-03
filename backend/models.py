"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class IngestByWordmarkRequest(BaseModel):
    """Request model for ingesting trademark by wordmark and class."""
    wordmark: str = Field(..., min_length=1, max_length=200, description="Trademark wordmark")
    class_name: int = Field(..., ge=1, le=45, description="Trademark class number (1-45)")

    @field_validator('wordmark')
    @classmethod
    def validate_wordmark(cls, v: str) -> str:
        """Validate and clean wordmark."""
        return v.strip()


class IngestByApplicationNumberRequest(BaseModel):
    """Request model for ingesting trademark by application number."""
    application_number: str = Field(..., min_length=1, max_length=50, description="Trademark application number")

    @field_validator('application_number')
    @classmethod
    def validate_application_number(cls, v: str) -> str:
        """Validate and clean application number."""
        return v.strip()


class SearchByWordmarkRequest(BaseModel):
    """Request model for searching trademark by wordmark and class."""
    wordmark: str = Field(..., min_length=1, max_length=200, description="Trademark wordmark")
    class_name: str = Field(..., description="Trademark class name")


class IngestAllRequest(BaseModel):
    """Request model for ingesting all stale trademarks."""
    stale_since_days: int = Field(default=15, ge=1, le=365, description="Number of days since last ingestion")


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete operations."""
    application_numbers: List[str] = Field(..., min_items=1, max_items=1000, description="List of application numbers to delete")

    @field_validator('application_numbers')
    @classmethod
    def validate_application_numbers(cls, v: List[str]) -> List[str]:
        """Validate and clean application numbers."""
        return [num.strip() for num in v if num.strip()]


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=1000, description="Items per page")


class SearchFilters(BaseModel):
    """Search and filter parameters."""
    wordmark: Optional[str] = Field(None, description="Filter by wordmark (partial match)")
    class_name: Optional[str] = Field(None, description="Filter by class name")
    status: Optional[str] = Field(None, description="Filter by status")
    application_number: Optional[str] = Field(None, description="Filter by application number (partial match)")
