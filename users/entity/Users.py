from pydantic import BaseModel,Field

class Users(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")