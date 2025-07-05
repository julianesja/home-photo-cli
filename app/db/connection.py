# db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Cambia estos valores con tus credenciales reales
DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/photo_organizer"

# Crear el engine
engine = create_engine(DATABASE_URL, echo=False)

# Crear una fábrica de sesiones
SessionLocal = sessionmaker(bind=engine)
