import logging
from fastapi import APIRouter, HTTPException
import subprocess
import os
import re

# Logger
logger = logging.getLogger("homeops.server")

# Create FastAPI router
router = APIRouter()

def parse_cpu_usage(top_output):
    try:
        # Extract the line containing CPU usage statistics
        cpu_line = None
        for line in top_output.split('\n'):
            if '%Cpu(s):' in line:
                cpu_line = line
                break

        if not cpu_line:
            raise ValueError("CPU usage line not found")

        # Print the CPU line and its length for debugging purposes
        print(f"CPU Line: '{cpu_line}'")
        print(f"Length of CPU Line: {len(cpu_line)}")

        # Regex to extract CPU usage percentages with flexible whitespace
        match = re.search(
            r'%Cpu\(s\):\s*(\d+\.\d+)\s+us,\s*(\d+\.\d+)\s+sy,\s*(\d+\.\d+)\s+ni,\s*(\d+\.\d+)\s+id,\s*(\d+\.\d+)\s+wa,\s*(\d+\.\d+)\s+hi,\s*(\d+\.\d+)\s+si,\s*(\d+\.\d+)\s+st',
            cpu_line
        )

        if not match:
            print("Failed to match CPU line")
            raise ValueError("Failed to match CPU usage data")

        # Parse the CPU usage data
        cpu_data = {
            'user': float(match.group(1)),
            'system': float(match.group(2)),
            'nice': float(match.group(3)),
            'idle': float(match.group(4)),
            'wait': float(match.group(5)),
            'hardware_interrupts': float(match.group(6)),
            'software_interrupts': float(match.group(7)),
            'steal': float(match.group(8))
        }

        return cpu_data
    except Exception as e:
        raise ValueError(f"Error parsing CPU usage: {str(e)}")


@router.get("/cpu-usage")
def get_cpu_usage():
    """
    Fetch and return detailed CPU usage statistics.

    Returns:
        dict: A dictionary containing various CPU usage statistics.

    Raises:
        HTTPException: If there is an error fetching or parsing CPU usage data.
    """
    logger.info("Fetching CPU usage statistics")

    try:
        # Check if the 'top' command is available on the system
        if not os.path.exists("/usr/bin/top"):
            logger.error("The 'top' command is not available on this system")
            raise HTTPException(status_code=501, detail="The 'top' command is not available on this system")

        # Run the 'top' command to get CPU stats (1 for 1 iteration, -b for batch mode)
        result = subprocess.run(['top', '-bn1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logger.error("Failed to execute 'top' command")
            raise HTTPException(status_code=500, detail="Failed to fetch CPU usage using the 'top' command")

        logger.info("Successfully fetched CPU usage data")

        # Parse the output from the 'top' command to extract CPU usage details
        cpu_usage_data = parse_cpu_usage(result.stdout)

        logger.info("CPU usage statistics retrieved successfully")
        return cpu_usage_data

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e}")
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Parsing error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error fetching CPU usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching CPU usage")
