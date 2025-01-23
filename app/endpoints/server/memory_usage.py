import logging
from fastapi import APIRouter, HTTPException
import subprocess
import os
import re

# Logger
logger = logging.getLogger("homeops.server")

# Create FastAPI router
router = APIRouter()


def parse_memory_value(value: str) -> float:
    """
    Helper function to parse memory values and handle non-numeric characters like 'i' (e.g., '263i').
    Returns a float, or 0.0 if the value is invalid.
    """
    try:
        # Remove non-numeric characters and try converting to float
        return float(re.sub(r'[^\d.]', '', value))
    except ValueError:
        return 0.0


@router.get("/memory-usage")
def get_memory_usage():
    """
    Fetches and returns detailed memory usage statistics of the system. \n

    This function runs the 'free' command to gather memory and swap usage information
    and parses the output. It calculates memory usage percentages, handles errors,
    and returns the data in a structured format. \n

    Returns: \n
        dict: A dictionary containing memory usage details including total, used,
              free, buffers, cached memory, and memory usage percentages. \n
        - total_memory: Total physical memory \n
        - used_memory: Memory currently used by processes \n
        - free_memory: Unused memory \n
        - buffers_memory: Memory used for file system buffers \n
        - cached_memory: Memory used for caching data \n
        - memory_usage_percent: Percentage of memory used \n
        - total_swap: Total swap space \n
        - used_swap: Swap space used \n
        - free_swap: Unused swap space \n

    Raises: \n
        HTTPException: If there's an error executing the 'free' command or parsing
                       the memory data. The exception will contain an appropriate status code.
    """
    logger.info("Fetching memory usage statistics")

    try:
        # Check if the system is Unix-based (free command exists)
        if not os.path.exists("/usr/bin/free"):
            # Log error if the 'free' command is not available
            logger.error("The 'free' command is not available on this system")
            raise HTTPException(status_code=501, detail="The 'free' command is not available on this system")

        # Run the 'free' command to get memory stats in human-readable format
        result = subprocess.run(['free', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            # Log error if the 'free' command fails
            logger.error("Failed to execute 'free' command")
            raise HTTPException(status_code=500, detail="Failed to fetch memory usage using the 'free' command")

        logger.info("Successfully fetched memory usage data")

        # Check the output of the 'free' command for debugging purposes
        logger.debug(f"Free command output: {result.stdout.strip()}")

        # Parse the output from 'free' command (split by lines)
        lines = result.stdout.strip().split("\n")
        memory_line = lines[1]  # The second line contains memory stats
        swap_line = lines[2]    # The third line contains swap stats

        # Split memory and swap data into their respective components
        memory_parts = memory_line.split()
        swap_parts = swap_line.split()

        # Ensure there are enough data parts in both lines to proceed with parsing
        if len(memory_parts) < 7 or len(swap_parts) < 3:
            # Log error if the data is malformed
            logger.error("Failed to parse memory or swap usage data")
            raise HTTPException(status_code=500, detail="Failed to parse memory or swap usage data")

        # Extract and parse memory values using the helper function
        total_memory = parse_memory_value(memory_parts[1])  # Total memory
        used_memory = parse_memory_value(memory_parts[2])   # Used memory
        free_memory = parse_memory_value(memory_parts[3])   # Free memory
        buffers_memory = parse_memory_value(memory_parts[4])  # Memory used by buffers
        cached_memory = parse_memory_value(memory_parts[5])   # Memory used by cache
        # Calculate memory usage percentage based on total and used memory
        memory_usage_percent = (used_memory / total_memory) * 100 if total_memory > 0 else 0

        # Extract and parse swap memory values
        total_swap = parse_memory_value(swap_parts[1])   # Total swap space
        used_swap = parse_memory_value(swap_parts[2])    # Used swap space
        free_swap = parse_memory_value(swap_parts[3])    # Free swap space

        logger.info("Memory usage statistics retrieved successfully")

        # Return the parsed and calculated memory data in a structured format
        return {
            "total_memory": total_memory,   # Total physical memory
            "used_memory": used_memory,     # Memory currently used
            "free_memory": free_memory,     # Available (free) memory
            "buffers_memory": buffers_memory,  # Memory used for buffers
            "cached_memory": cached_memory,   # Memory used for cache
            "memory_usage_percent": round(memory_usage_percent, 2),  # Percentage of memory used
            "total_swap": total_swap,       # Total swap space
            "used_swap": used_swap,         # Used swap space
            "free_swap": free_swap          # Free swap space
        }

    except subprocess.CalledProcessError as e:
        # Log and raise HTTP exception if there’s a subprocess error
        logger.error(f"Subprocess error: {e}")
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e}")

    except FileNotFoundError as e:
        # Log and raise HTTP exception if the 'free' command is not found
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    except ValueError as e:
        # Log and raise HTTP exception if there's a parsing error (invalid data)
        logger.error(f"ValueError: {e}")
        raise HTTPException(status_code=500, detail=f"ValueError: {e}")

    except Exception as e:
        # Log and raise HTTP exception for any other unexpected errors
        logger.error(f"Unexpected error fetching memory usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching memory usage")
