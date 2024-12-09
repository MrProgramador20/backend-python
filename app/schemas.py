from pydantic import BaseModel

# Esquema para crear un nuevo usuario
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

# Esquema para devolver los detalles del usuario (sin contraseña)
class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
