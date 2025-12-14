# Linkdin_Insights_Scrapper
This project is a FastAPI application that acts as a LinkedIn Insights Scraper and API. It uses SQLAlchemy and a MySQL database to efficiently store scraped company pages and posts. The API prioritizes database lookup (caching) before triggering web scraping with Selenium and BeautifulSoup. 
LinkedIn Insights Scraper API
This project implements a FastAPI application that serves as an API for scraping and storing LinkedIn company page and post data into a MySQL database. It uses SQLAlchemy for database interaction and Selenium with BeautifulSoup for handling the web scraping of dynamic content.

🚀 Getting Started
This section outlines the foundational steps and components of the application.

📦 Database Setup
The core data is managed in a MySQL database named linkedin_insights_db. The following tables were created to store the scraped information:

pages: Stores general company page information.

CREATE TABLE pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_name VARCHAR(255),
    page_url VARCHAR(500),
    linkedin_id VARCHAR(100), -- Used as the unique ID in the LinkedIn URL
    profile_picture TEXT,
    description TEXT,
    website VARCHAR(255),
    industry VARCHAR(255),
    followers INT,
    head_count INT
);

posts: Stores individual posts associated with a company page.

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT,
    content TEXT,
    likes INT,
    comments_count INT,
    created_at DATETIME,
    FOREIGN KEY (page_id) REFERENCES pages(id)
);

employees: An auxiliary table for employee data (though the provided code does not currently implement scraping for this table, the schema is prepared).

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT,
    name VARCHAR(255),
    designation VARCHAR(255),
    FOREIGN KEY (page_id) REFERENCES pages(id)
);
🔑 Authentication (For Post Scraping)
LinkedIn requires a logged-in session to reliably access and scrape post data. This application is configured to use a local file for storing session cookies:

A file named linkedin_cookies.txt must be present in the project's base directory. The load_cookies function in scraper.py is designed to read and use these cookies to authenticate the Selenium browser instance, allowing it to scrape post content.

▶️ Running the Application
The application is run as a standard FastAPI service:

Bash :-

uvicorn app.main:app --workers 1 --port 8003
This command starts the API server, making the endpoints available at http://127.0.0.1:8003.

💻 Code Architecture: File by File Explanation
The project is structured into several files, each handling a specific, decoupled part of the overall logic.

database.py:-
1.This file is the Database Connector.

2.It defines the DATABASE_URL to connect to the MySQL database.

3.It creates the SQLAlchemy engine for managing connections.

4.It sets up SessionLocal, which is a factory for creating database sessions (db).

5.It defines Base, the declarative base class that all model classes inherit from to define the table structure.

models.py:-
1.This file defines the Database Schema.

2.It contains the SQLAlchemy models (Page and Post) that map Python classes to the pages and posts tables in the database.

3.It specifies the columns (e.g., Column(Integer, primary_key=True)) and their relationships (e.g., the page_id in Post is a ForeignKey to pages.id).

crud.py (Create, Read, Update, Delete):-
1.This file is the Database Interaction Layer.

2.It contains functions like get_page_by_id, create_page, get_posts_by_page, and create_posts.

3.These functions handle all the logic for querying and saving data to the database, ensuring that the main API logic remains clean and focused. For instance, create_page takes a Python dictionary of data, converts it into a Page object, adds it to the session, and commits it.

scraper.py:-
1.This file is the Web Scraping Engine.

2.scrape_linkedin_page(page_id): Uses a simple requests GET and BeautifulSoup to scrape the static company page information (name, URL, description, followers, etc.). This data is generally public and does not require a login.

3.scrape_company_posts(page_id):

This function requires Selenium to launch a full web browser (Chrome) because LinkedIn loads post content dynamically using JavaScript.It's configured to open the posts URL, then scroll down (driver.execute_script) multiple times to load more content.After scrolling, it uses BeautifulSoup to parse the fully loaded page source and extract post details (content, likes, comments).

Crucially, this is where the need for a login arises. To access and scrape a page's posts without being immediately redirected to a login prompt, a valid, authenticated session is necessary, which is handled by the (currently non-implemented) load_cookies function.

main.py:-
1.This is the API Endpoint Handler using FastAPI.

2.It initializes the FastAPI app and ensures the database tables are created (Base.metadata.create_all).

3.get_db(): This is a FastAPI dependency function that handles creating and closing a database session for each request.

/page/{page_id} (GET):

Tries to read the page from the database (crud.get_page_by_id).

If found, it immediately returns the saved data (avoiding unnecessary scraping).

If not found, it calls scraper.scrape_linkedin_page to fetch the data.

It then calls crud.create_page to save the new data into the pages table.

/page/{page_id}/posts (GET):

First, it verifies the page exists in the DB.

Tries to read existing posts for that page (crud.get_posts_by_page).

If posts are found, it returns them.

If no posts are found, it executes the resource-intensive process: it calls scraper.scrape_company_posts (which launches the Selenium browser).

Finally, it calls crud.create_posts to save the newly scraped posts to the posts table.

🌐 API Workflow & Data Persistence
The application's design is based on a Cache-Aside pattern, where the database acts as a cache for scraped data.

Request to /page/deepsolv:

The API first checks the pages table for a record with linkedin_id = 'deepsolv'.

If a record exists, the stored JSON data is instantly returned.

If it does not exist, the scraper is activated to fetch the page's public information. This new data is then saved into the pages table for future, faster access.

Request to /page/deepsolv/posts:
<img width="1354" height="751" alt="image" src="https://github.com/user-attachments/assets/d77e84d5-40db-498a-b682-a39009797e88" />

The API checks the posts table for any posts linked to the deepsolv page (via page_id).

If posts are found, they are returned.

If no posts are found, the Selenium scraper is launched. This step is where the local server opens a LinkedIn page in a browser, attempts to log in using the cookies, scrolls to load posts, scrapes the content, and then the extracted data is saved to the posts table
