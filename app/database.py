from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cadena de conexión a MySQL (sin contraseña)
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3310/myapp"

# Crear el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear una sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para las clases ORM
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
