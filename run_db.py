from bus_tracker import app, db
app.app_context().push()
db.create_all()