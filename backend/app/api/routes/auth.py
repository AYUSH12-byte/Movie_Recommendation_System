from fastapi import (
    APIRouter,
    HTTPException
)

from app.models.user import (
    UserCreate,
    UserLogin
)

from app.services.auth_service import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user: UserCreate
):

    result = register_user(
        name=user.name,
        email=user.email,
        password=user.password
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


@router.post("/login")
def login(
    user: UserLogin
):

    result = login_user(
        email=user.email,
        password=user.password
    )

    if not result["success"]:

        raise HTTPException(
            status_code=401,
            detail=result["message"]
        )

    return result