Restaurant Management System API
 
Overview - A backend system designed to manage restaurant 
operations including menu, orders, tables, and inventory.
 
Features
- Add and view menu items
- Place food orders
- Automatic inventory deduction
- Table management and reservations
- Order tracking with database
 
API Endpoints
Menu
POST /add_menu
GET /menu
 
Orders
POST /place_order
GET /orders
 
Tables 
POST /add_table
POST /reserve_table
GET /tables
 
Example Order Request:
api.add_resource(AddMenuItem, "/add_menu") #POST - http://127.0.0.1:5003/add_menu
{
  "name": "Chicken",
  "price": "95.00",
  "stock": "28"
}

api.add_resource(ViewMenu, "/menu") #GET - http://127.0.0.1:5003/menu
{
  "menu": " "
}
 
api.add_resource(PlaceOrder, "/place_order") #POST - http://127.0.0.1:5003/place_order
{
  "item_id": " ",
  "quantity": " "
}

api.add_resource(ViewOrders, "/orders") #GET - http://127.0.0.1:5003/orders
{
  "orders": " "
}
 
api.add_resource(AddTable, "/add_table") #POST - http://127.0.0.1:5003/add_table
{
  "table_number": " ",
  "seats": " "
}

api.add_resource(ReserveTable, "/reserve_table") #POST - http://127.0.0.1:5003/reserve_table
{
  "table_number": " "
}

api.add_resource(ViewTables, "/tables") #GET - http://127.0.0.1:5003/tables
{
  "table": " "
}
 
Run the Project
py app.py / python app.py
Server runs on:
http://127.0.0.1:5003
