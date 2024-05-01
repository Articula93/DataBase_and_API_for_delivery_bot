from pydantic import BaseModel
from typing import Optional
from typing import List
from pydantic import Field
from odin_doma_db_model import*

class UserIn(BaseModel):
    login: str
    password: str
    password_check: str
    is_admin: bool

class UserOut(BaseModel):
    id: int
    login: str
    is_admin: bool

class UserOutUpdate(BaseModel):
    login: str
    is_admin: bool

class UserChecking(BaseModel):
    check: bool

def user_in_db_to_user(user_in_db):
    create_user = UserOut(id=user_in_db.id,login=user_in_db.login,is_admin=user_in_db.is_admin)
    return create_user

class RequestCreateUsers(BaseModel):
    user:UserIn

class RequestUpdateUser(BaseModel):
    login: Optional[str] = Field(None)
    password: Optional[str]  = Field(None)
    password_check: Optional[str]  = Field(None)
    is_admin: Optional[bool]  = Field(None)

class RequestCheckingUser(BaseModel):
    login: str
    password: str

class ResponceCreateUsers(BaseModel):
    success: bool
    error: str | None
    user: UserOut

class ResponceListUsers(BaseModel):
    success: bool
    error: str | None
    user: List[UserOut]

class ResponceSearchUsers(BaseModel):
    success: bool
    error: str | None
    user: List[UserOut]

class ResponceUpdateUsers(BaseModel):
    success: bool
    error: str | None
    user: UserOutUpdate


class ResponceCheckingUsers(BaseModel):
    success: bool
    error: str | None
    user: bool
    token: str

class ResponceSearchToken(BaseModel):
    success: bool
    error: str | None