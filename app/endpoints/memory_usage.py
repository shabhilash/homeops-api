import logging
from fastapi import APIRouter, HTTPException
import subprocess
import os

# Logger
logger = logging.getLogger("homeops.server")

# Create FastAPI router
router = APIRouter()


@router.get("/memory-usage")
def get_memory_usage():
    logger.info("Fetching memory usage statistics")

    try:
        # Check if the system is Unix-based (free command exists)
        if not os.path.exists("/usr/bin/free"):
            logger.error("The 'free' command is not available on this system")
            raise HTTPException(status_code=501, detail="The 'free' command is not available on this system")

        # Run the 'free' command to get memory stats
        result = subprocess.run(['free', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logger.error("Failed to execute 'free' command")
            raise HTTPException(status_code=500, detail="Failed to fetch memory usage using the 'free' command")

        logger.info("Successfully fetched memory usage data")

        # Parse the output from 'free' command
        lines = result.stdout.strip().split("\n")
        memory_line = lines[1]  # The second line contains memory stats
        parts = memory_line.split()

        if len(parts) < 4:
            logger.error("Failed to parse memory usage data")
            raise HTTPException(status_code=500, detail="Failed to parse memory usage data")

        total_memory = parts[1]
        used_memory = parts[2]
        free_memory = parts[3]
        memory_usage_percent = parts[2] + " of " + parts[1]  # Example: "1.5G of 8G"

        logger.info("Memory usage statistics retrieved successfully")
        return {
            "total": total_memory,
            "used": used_memory,
            "free": free_memory,
            "memory_usage_percent": memory_usage_percent
        }

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e}")
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except Exception as e:
        logger.error(f"Unexpected error fetching memory usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching memory usage")
