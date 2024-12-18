from fastapi import APIRouter, Depends

from app.utils.auth import is_superuser_required
from app.utils.schemas import User
from app.utils.sync_adusers import sync_ad_users

router = APIRouter()


# noinspection PyUnusedLocal
@router.put("/reload/ad-users")
async def refresh_users(current_user: User = Depends(is_superuser_required())):
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