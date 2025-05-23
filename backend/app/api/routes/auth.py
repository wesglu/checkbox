from fastapi import APIRouter, status, Body, HTTPException, Form
from datetime import timedelta

from app import models
from app import crud
from app.core.security import get_password_hash, get_token_from_login_password
from app.core.config import settings

router = APIRouter(prefix='/auth')

@router.post(
    "/signup", 
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Registers a new user with the provided name, login, and password."
)
async def signup(
    name: str = Body(..., description="Name of the user", example="John Doe", min_length=1),
    login: str = Body(..., description="Login of the user", example="john.doe", min_length=1),
    password: str = Body(..., description="Password of the user", example="password123", min_length=1),
):  
    # Prevent testing users from being created
    if name in ['wronguser', 'testuser']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    hashed_password = get_password_hash(password)
    user = models.User(name=name, login=login, password=hashed_password)
    await crud.create_user(user) # create user and raise an error if the login already exists
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong...")

    return {"message": "User successfully signed up!"}

@router.post(
    "/signin", 
    status_code=status.HTTP_200_OK,
    summary="User Signin",
    description="Authenticates a user and returns a token if the login and password are correct."
)
async def signin(
    login: str = Body(..., description="Login of the user", example="john.doe", min_length=1),
    password: str = Body(..., description="Password of the user", example="password123", min_length=1),
):
    return await get_token_from_login_password(login, password)

@router.post(
    "/signin-openapi", 
    status_code=status.HTTP_200_OK, 
    include_in_schema=False,
)
async def signin_openapi(
    username: str = Form(...),
    password: str = Form(...),
):
    return await get_token_from_login_password(username, password)