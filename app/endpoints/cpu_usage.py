import logging
from fastapi import APIRouter, HTTPException
import subprocess
import os

# Logger
logger = logging.getLogger("homeops.server")

# Create FastAPI router
router = APIRouter()


@router.get("/cpu-usage")
def get_cpu_usage():
    logger.info("Fetching CPU usage statistics")

    try:
        # Check if the system is Unix-based (top command exists)
        if not os.path.exists("/usr/bin/top"):
            logger.error("The 'top' command is not available on this system")
            raise HTTPException(status_code=501, detail="The 'top' command is not available on this system")

        # Run the 'top' command to get CPU stats (1 for 1 iteration, -b for batch mode)
        result = subprocess.run(['top', '-bn1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logger.error("Failed to execute 'top' command")
            raise HTTPException(status_code=500, detail="Failed to fetch CPU usage using the 'top' command")

        logger.info("Successfully fetched CPU usage data")

        # Parse the output from 'top' command to extract CPU usage
        lines = result.stdout.strip().split("\n")
        cpu_usage_line = next((line for line in lines if "Cpu(s)" in line), None)

        if not cpu_usage_line:
            logger.error("Failed to find CPU usage data")
            raise HTTPException(status_code=500, detail="Failed to find CPU usage data")

        # Extract the percentage of CPU usage
        cpu_usage = cpu_usage_line.split(":")[1].split(",")[0].strip()

        logger.info("CPU usage statistics retrieved successfully")
        return {"cpu_usage": cpu_usage}

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e}")
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except Exception as e:
        logger.error(f"Unexpected error fetching CPU usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching CPU usage")
