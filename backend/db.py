from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("USUARIO_DB_GOSTOS")
password = os.getenv("SENHA_DB_GOSTOS")
host = os.getenv("HOST_DB_GOSTOS")
database = os.getenv("BANCO_DB_GOSTOS")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
