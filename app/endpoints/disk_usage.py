import logging
from fastapi import APIRouter, HTTPException
import subprocess
import os

# Logger
logger = logging.getLogger("homeops.server")

# Create FastAPI router
router = APIRouter()


@router.get("/disk-usage")
def get_all_disk_usage():
    logger.info("Fetching disk usage statistics")

    try:
        # Check if the system is Unix-based (df command exists)
        if not os.path.exists("/bin/df"):
            logger.error("The 'df' command is not available on this system")
            raise HTTPException(status_code=501, detail="The 'df' command is not available on this system")

        # Run the 'df' command to get disk usage stats for all mounted file systems
        result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # If the 'df' command fails
        if result.returncode != 0:
            logger.error("Failed to execute 'df' command")
            raise HTTPException(status_code=500, detail="Failed to fetch disk usage using the 'df' command")

        logger.info("Successfully fetched disk usage data")

        # Parse the output from 'df' command
        lines = result.stdout.strip().split("\n")
        disk_usage_list = []

        # Skip the first line (headers)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                # Extract relevant information for each partition
                device = parts[0]
                mountpoint = parts[5]
                total = parts[1]
                used = parts[2]
                available = parts[3]
                percent_used = parts[4]

                # Log each partition's disk usage
                logger.debug(
                    f"Device: {device}, Mountpoint: {mountpoint}, Total: {total}, Used: {used}, Available: {available}, Percent Used: {percent_used}")

                disk_usage_list.append({
                    "device": device,
                    "mountpoint": mountpoint,
                    "total": total,
                    "used": used,
                    "free": available,
                    "percent_used": percent_used
                })

        logger.info("Disk usage statistics retrieved successfully")
        return disk_usage_list

    except subprocess.CalledProcessError as e:
        # Handle subprocess errors (e.g., command execution failure)
        logger.error(f"Subprocess error: {e}")
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e}")

    except FileNotFoundError as e:
        # Handle missing executable (e.g., 'df' command not found)
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except Exception as e:
        # General error handler for unexpected errors
        logger.error(f"Unexpected error fetching disk usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching disk usage")
