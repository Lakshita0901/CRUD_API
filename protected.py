from fastapi import APIRouter, Depends
from dependencies import get_current_user

router = APIRouter()

@router.get("/public/info", summary="Public information")
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}

@router.get("/protected/profile", summary="Get authenticated user profile")
def get_profile(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@router.get("/protected/dashboard", summary="Get protected dashboard")
def get_dashboard(current_user = Depends(get_current_user)):
    return {
        "message": "Welcome to your protected dashboard!",
        "email": current_user.email
    }
