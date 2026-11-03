from users.entity.Users import Users
from users.Service.UsersService import login, register
from fastapi import APIRouter

api_router = APIRouter()


@api_router.post("/login")
def login_endpoint(users: Users):
    return login(users)


@api_router.post("/register")
def register_endpoint(users: Users):
    return register(users)