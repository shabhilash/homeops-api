from fastapi import APIRouter

from app.server.sync_adusers import sync_ad_users

router = APIRouter()


@router.put("/reload/ad-users", tags=["reload"])
async def refresh_users():
    """
    This endpoint will sync all the AD users to the local database
    """
    total_users, new_users, modified_users = await sync_ad_users()
    return {
        "status": "Success",
        "details": {
            "message": "Users Refreshed",
            "total_users": total_users,
            "new_users": new_users,
            "modified_users": modified_users
        }
    }