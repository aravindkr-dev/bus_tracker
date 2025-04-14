from bus_tracker import app, db
"""
obj = Mytable(name='admin', passw='admin', role='admin')
db.session.add(obj)
db.session.commit()
"""
with app.app_context():
    db.create_all()