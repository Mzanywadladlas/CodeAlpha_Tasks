URL Shortener API
 
Overview - This project is a Flask-based backend API that shortens 
long URLs and redirects users using a unique short code.
 
Features
- Generate short URLs
- Redirect to original URL
- SQLite database storage
- RESTful API structure
 
API Endpoints
Shorten URL - POST /shorten
Request Body:
api.add_resource(Shorten, "/shorten") #POST - http://127.0.0.1:5001/shorten
{
  "url": " ",
  "code": " "
}
Response:
{
"Message": "http://localhost:5001/abc123",
"Status Code": 200
}
 
GET /<short_code>
Redirects to the original URL.
N.B - use the code from the urls table
api.add_resource(RedirectURL, "/<string:code>") #GET - http://127.0.0.1:5001/code from the urls table
 
Run the Project
py app.py / python app.py 
Server runs on:
http://127.0.0.1:5001
