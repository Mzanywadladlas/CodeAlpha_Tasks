Event Registration System API
 
Overview - A backend API for managing events and 
user registrations using Flask and SQLite.
 
Features
- Create events
- List all events
- Register users for events
- Structured REST API design
 
API Endpoints
Create Event
POST /create_event
 
View Events
GET /events
 
Register for Event
POST /register_event

Example Request:
api.add_resource(CreateEvent, "/create_event")  #POST - http://127.0.0.1:5002/create_event

{
  "title": "Music Concert",
  "description": "Johannesburg",
  "event_date": "2025-06-21"
}

api.add_resource(ListEvents, "/events") #GET - http://127.0.0.1:5002/events
no body - it will return events added

api.add_resource(RegisterEvent, "/register_event") #POST - http://127.0.0.1:5002/register_event

{
  "name": "Hackathon",
  "email": "test@testsa.co.za",
  "event_id": "1"
}
 
Run the Project
py app.py / python app.py
Server runs on:
http://127.0.0.1:5002
