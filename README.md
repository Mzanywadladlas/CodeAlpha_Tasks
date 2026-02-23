CodeAlpha Backend Development Tasks
 
This repository contains backend development projects completed as part of the CodeAlpha Internship Program.
All projects are built using Flask, REST APIs, SQLite, and a structured Resource-based architecture.
 
Internship Tasks Covered
- Task 1: Simple URL Shortener
- Task 2: Event Registration System
- Task 3: Restaurant Management System
 
Each project follows:
- Clean API structure (Flask + flask_restful)
- Central validation logic
- SQLite database integration
- Production-ready JSON responses
 
-------------------------------------------------------------------------------
 
Project 1: URL Shortener API
 
Description
A backend service that converts long URLs into short codes and redirects users to the original link.
 
Features
- Shorten long URLs
- Unique short code generation
- Redirect to original URL
- Hit tracking using database
 
Endpoints
POST /shorten
Body:
{
"url": "https://example.com"
}
 
GET /<code>
Redirects to original URL
 
Tech Stack
- Flask
- Flask-RESTful
- SQLite
 
--------------------------------------------------------------------------
 
Project 2: Event Registration System
 
Description
A backend API that allows users to create events and register for them.
 
Features
- Create events
- View event list
- Register for events
- Database-backed registrations
 
Endpoints
POST /create_event
GET /events
POST /register_event
 
Example Request
{
"title": "Tech Conference",
"event_date": "2026-03-10"
}
 
Tech Stack
- Flask
- Flask-RESTful
- SQLite
 
----------------------------------------------------------------------------------
 
Project 3: Restaurant Management System
 
Description 
A backend system for managing restaurant operations including menu, orders, tables, and inventory.
 
Features
- Menu management
- Table reservation system
- Order placement
- Automatic inventory update
- Order tracking
 
Endpoints
POST /add_menu
GET /menu
POST /place_order
GET /orders
POST /add_table
POST /reserve_table
GET /tables
 
Tech Stack
- Flask
- Flask-RESTful
- SQLite
 
-------------------------------------------------------------------------------------
 
****Installation Guide****
 
Step 1: Clone Repository
git clone https://github.com/yourusername/CodeAlpha_Projects.git
cd CodeAlpha_tasks
 
Step 2: Create Virtual Environment
python -m venv venv / py -m venv venv
venv\Scripts\activate  (Windows)
source venv/bin/activate  (Mac/Linux)
 
Step 3: Install Dependencies
update pip - py -m pip install --upgrade pip / python -m pip install --upgrade pip 
py -m pip install -r requirements.txt / python -m pip install -r requirements.txt
 
Step 4: Run Project
cd Project_Folder
py app.py / python app.py
 
****************************************************************************************
 
Mzanywa Dladla Developer
 
Backend Developer Intern – CodeAlpha
Built using structured REST API architecture with Flask.
