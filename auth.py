from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from supabase import AuthApiError, AuthError
from supabase_client import supabase
from dependencies import get_current_user, security

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCredentials(BaseModel):
    email: str
    password: str

@router.post("/signup", status_code=status.HTTP_201_CREATED, summary="Sign up a new user")
def signup(credentials: UserCredentials):
    if not credentials.email or not credentials.email.strip() or not credentials.password or not credentials.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email.strip(),
            "password": credentials.password
        })
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Failed to create user"}
            )
        return response.user
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message}
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

@router.post("/login", status_code=status.HTTP_200_OK, summary="Log in an existing user")
def login(credentials: UserCredentials):
    if not credentials.email or not credentials.email.strip() or not credentials.password or not credentials.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email.strip(),
            "password": credentials.password
        })
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid login credentials"}
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except (AuthApiError, AuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log out the current user")
def logout(
    current_user = Depends(get_current_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    try:
        if credentials and credentials.credentials:
            try:
                supabase.auth.admin.sign_out(credentials.credentials)
            except Exception:
                supabase.auth.sign_out()
        else:
            supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)
