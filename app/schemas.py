from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OneTimeToken(BaseModel):
    token: str
