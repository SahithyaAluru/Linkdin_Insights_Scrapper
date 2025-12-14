from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "mysql+pymysql://root:Sahi%408761@localhost:3306/linkedin_insights_db"
engine = create_engine(
    DATABASE_URL,
    echo=True,      
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()
