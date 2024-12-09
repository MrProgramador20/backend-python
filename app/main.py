from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import hashlib

# Configuración de la base de datos
DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3310/mydatabase"

# Conexión y configuración de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Crear la aplicación FastAPI
app = FastAPI()

# Habilitar CORS para aceptar solicitudes del frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringirlo a solo tu dominio: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

# Definir el modelo de base de datos para los usuarios
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Modelo de datos para recibir en las solicitudes
class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

# Función para hashear la contraseña
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", status_code=201)
async def register_user(user: User, db: Session = Depends(get_db)):
    # Verificar si el correo ya está registrado
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hashear la contraseña
    hashed_password = hash_password(user.password)
    
    # Crear el nuevo usuario en la base de datos
    new_user = UserDB(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user": user.dict()}

@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users

@app.post("/login/")
async def login_user(login: Login, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == login.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Verificar que la contraseña coincida
    hashed_password = hash_password(login.password)
    if db_user.password != hashed_password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "user": db_user.name}