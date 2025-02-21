import time
from fastapi import Request, status

from app.exceptions.global_exception import GlobalHTTPException

# In-memory storage for request counters
request_counters = {}


# Custom RateLimiter class with dynamic rate limiting values per route
class RateLimiter:
    def __init__(self, requests_limit: int, time_window: int):
        self.requests_limit = requests_limit
        self.time_window = time_window

    async def __call__(self, request: Request):
        client_ip = request.client.host
        route_path = request.url.path

        # Get the current timestamp
        current_time = int(time.time())

        # Create a unique key based on client IP and route path
        key = f"{client_ip}:{route_path}"

        # Check if client's request counter exists
        if key not in request_counters:
            request_counters[key] = {"timestamp": current_time, "count": 1}
        else:
            # Check if the time window has elapsed, reset the counter if needed
            if current_time - request_counters[key]["timestamp"] > int(self.time_window):
                # Reset the counter and update the timestamp
                request_counters[key]["timestamp"] = current_time
                request_counters[key]["count"] = 1
            else:
                # Check if the client has exceeded the request limit
                if request_counters[key]["count"] >= self.requests_limit:
                    raise GlobalHTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            title="Too Many Requests",
                            detail=f"Rate limit exceeded. You've made {self.requests_limit} requests within {self.time_window} seconds. Please try again later.",
                            code="REQUEST_LIMIT_EXCEEDED"
                    )
                else:
                    request_counters[key]["count"] += 1

        # Clean up expired client data (optional)
        for k in list(request_counters.keys()):
            if current_time - request_counters[k]["timestamp"] > int(self.time_window):
                request_counters.pop(k)

        return True