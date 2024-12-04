from fastapi import APIRouter

from server.sync_adusers import sync_ad_users

router = APIRouter()


@router.put("/reload/ad-users", tags=["reload"], status_code=204)
async def refresh_users():
    """
    This endpoint will sync all the AD users to the local database
    """
    await sync_ad_users()
    # return {"message": "Users Refreshed"}