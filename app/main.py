from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.scraper import scrape_linkedin_page, scrape_company_posts
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn Insights")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/page/{page_id}")
def get_page(page_id: str, db: Session = Depends(get_db)):
    page = crud.get_page_by_id(db, page_id)
    if page:
        return page

    data = scrape_linkedin_page(page_id)
    page = crud.create_page(db, data)
    return page

@app.get("/page/{page_id}/posts")
def get_posts(page_id: str, db: Session = Depends(get_db)):
    try:
        page = crud.get_page_by_id(db, page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")

        posts = crud.get_posts_by_page(db, page.id)
        if posts:
            return posts

        print("Starting Selenium scraper...")
        scraped_posts = scrape_company_posts(page_id)
        print("Scraped posts:", scraped_posts)

        posts = crud.create_posts(db, page.id, scraped_posts)
        return posts

    except Exception as e:
        import traceback
        print("FULL ERROR TRACEBACK:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
