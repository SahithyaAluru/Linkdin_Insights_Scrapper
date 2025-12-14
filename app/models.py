from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(Text)
    page_url = Column(Text)
    linkedin_id = Column(Text, unique=True)
    profile_picture = Column(Text)
    description = Column(Text)
    website = Column(Text)
    industry = Column(Text)
    followers = Column(Integer)
    head_count = Column(Integer)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    content = Column(Text)
    likes = Column(Integer)
    comments_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
