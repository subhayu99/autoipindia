"""
Simple rate limiting middleware for FastAPI.
"""
from fastapi import Request, HTTPException
from time import time
from collections import defaultdict
from typing import Dict, Tuple
import threading

class RateLimiter:
    """
    Simple in-memory rate limiter.

    Tracks requests per IP address within a time window.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.requests: Dict[str, list[float]] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if a request is allowed for the given identifier.

        Args:
            identifier: Unique identifier (e.g., IP address)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time()

        with self.lock:
            # Remove old requests outside the time window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < self.window_size
            ]

            # Check if under limit
            if len(self.requests[identifier]) >= self.requests_per_minute:
                return False, 0

            # Add current request
            self.requests[identifier].append(current_time)
            remaining = self.requests_per_minute - len(self.requests[identifier])

            return True, remaining

    def cleanup_old_entries(self):
        """Remove entries for identifiers with no recent requests."""
        current_time = time()

        with self.lock:
            identifiers_to_remove = []

            for identifier, req_times in self.requests.items():
                # Remove old requests
                recent_requests = [
                    req_time for req_time in req_times
                    if current_time - req_time < self.window_size
                ]

                if not recent_requests:
                    identifiers_to_remove.append(identifier)
                else:
                    self.requests[identifier] = recent_requests

            # Remove empty identifiers
            for identifier in identifiers_to_remove:
                del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request):
    """
    Rate limiting middleware for FastAPI.

    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Skip rate limiting for health check endpoint
    if request.url.path == "/health":
        return

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )

    # Add rate limit info to response headers (will be added by dependency)
    request.state.rate_limit_remaining = remaining
