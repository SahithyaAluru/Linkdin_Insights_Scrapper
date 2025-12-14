from app.models import Page, Post
def get_page_by_id(db, page_id: str):
    return db.query(Page).filter(Page.linkedin_id == page_id).first()
def create_page(db, page_data: dict):
    page = Page(**page_data)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page
def get_posts_by_page(db, page_id: int):
    return db.query(Post).filter(Post.page_id == page_id).all()
def create_posts(db, page_id: int, posts: list):
    saved_posts = []
    for post in posts:
        db_post = Post(
            page_id=page_id,
            content=post["content"],
            likes=post["likes"],
            comments_count=post["comments_count"]
        )
        db.add(db_post)
        saved_posts.append(db_post)

    db.commit()
    return saved_posts
