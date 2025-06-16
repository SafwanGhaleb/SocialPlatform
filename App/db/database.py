from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

DATABASE_URL = "mysql+mysqlconnector://root:Motopp2025@localhost/database_info"
#DATABASE_URL = "sqlite:///./test.db"



engine = create_engine(DATABASE_URL)

def create_tables():
    Base.metadata.create_all(bind=engine)

#  Session factory in order to open a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
