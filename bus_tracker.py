from flask import Flask, request, render_template, jsonify, session, redirect , url_for , flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

app = Flask('__name__'  , template_folder='templates')
user_locations = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./abcd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


app.secret_key = 'secret'

class User(db.Model):
    __tablename__ = 'user_cred'

    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(30) , nullable = False , unique = True)
    passw = db.Column(db.String(60) , nullable = False)
    role = db.Column(db.String(30) , nullable = False)
    transportid = db.Column(db.String(100) , nullable = True)

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'passw':self.passw,
            'role':self.role,
            'transportid':self.transportid
        }



class Bus(db.Model):
    __tablename__ = 'bus_details'
    id = db.Column(db.Integer , primary_key = True)
    bus_number = db.Column(db.String(10) , unique = True , nullable = False)
    starting = db.Column(db.String(300))#coordinates

    def to_dict(self):
        return {
            'id' : self.id,
            'bus_number' : self.bus_number,
            'starting' : self.starting
        }

migrate = Migrate(app, db)

def verify():
    if 'username' not in session:
        print("User Not Logged In")
        return False
    return True



@app.route('/student')
def student_dashboard():
    if 'username' in session and 'role' in session and session.get('role') == 'student':
        return render_template('student/dashboard.html' , user_id = session.get('username'))
    return redirect(url_for('login'))


@app.route('/driver')
def driver_dashboard():
    if 'username' in session and 'role' in session and session.get('role') == 'driver':
        flash('Login Successful', 'success')
        return render_template('driver/dashboard.html' , username = User.name)
    else:
        flash('You are not a driver', 'error')
        return redirect('/login')


@app.route('/admin')
def admin_dashboard():
    if 'username' in session and 'role' in session and session.get('role') == 'admin':
        buses = Bus.query.all()
        flash('Login Successful', 'success')
        return render_template('admin/dashboard.html', username=session['username'], buses=buses)
    else:
        flash('You are not a Admin', 'error')
        return redirect('/login')


@app.route('/add_bus' , methods = ['POST'])
def add_bus():
    if 'username' in session and 'role' in session and session.get('role') == 'admin':
        bus_number = request.form['bus_number']
        starting = request.form['start']

        obj = Bus(bus_number = bus_number , starting = starting)
        db.session.add(obj)
        db.session.commit()
        flash('Bus added successfully' , 'success')
        return redirect('/admin')
    flash('Error while adding the bus' , 'error')
    return redirect('/admin')

@app.route('/view_bus')
def view_bus():
    if not verify() or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('viewbus.html')

@app.route('/locations')
def get_locations():
    if not verify():
        return redirect(url_for('login'))
    return jsonify(user_locations)


@app.route('/location', methods=['POST'])
def receive_location():
    if not verify():
        return redirect(url_for('login'))
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    lat = data['latitude']
    lon = data['longitude']

    if user_id not in user_locations:
        user_locations[user_id] = {
            'color': '#%06x' % (hash(user_id) & 0xFFFFFF),
            'trail': []
        }

    user_locations[user_id]['trail'].append({
        'lat': lat,
        'lon': lon,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    print(f"Received from {user_id}: {lat}, {lon}")

    return 'OK', 200  # ✅ Important: return a valid HTTP response!


@app.route('/signup' , methods = ['GET','POST'])

def signup():
    if request.method == 'POST':
            user_name = request.form['username']
            passw = request.form['password']
            role = request.form['role']

            obj = User(name = user_name , passw = passw , role = role)
            db.session.add(obj)
            db.session.commit()
    return render_template('signup.html')


@app.route('/login' , methods = ['GET' , 'POST'])

def login():
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        role = request.form['role']
        data = User.query.all()
        cred = ([x.to_dict() for x in data])
        print(cred)
        for x in cred:
            if x['name'] == user and x['passw'] == passw and x['role'] == 'student' and role == x['role']:
                session['username'] = x['name']
                session['role'] = x['role']
                return redirect(url_for('student_dashboard'))

            elif x['name'] == user and x['passw'] == passw and x['role'] == 'driver' and role == x['role']:
                session['username'] = x['name']
                session['role'] = x['role']
                return redirect(url_for('driver_dashboard'))

            elif x['name'] == user and x['passw'] == passw and x['role'] == 'admin' and role == x['role']:
                session['username'] = x['name']
                session['role'] = x['role']
                return redirect(url_for('admin_dashboard'))
            else:
                pass
        return redirect(url_for('view_bus'))
    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/logout' , methods=['POST' , 'GET'])
def logout():
    session.clear()
    return '<h1>Logout Successfull</h1>'

if __name__ == '__main__':
    """ app.app_context().push()"""
    """with app.app_context():
        db.create_all()"""
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(name='admin').first()
        if not admin:
            admin = User(
                name='admin',
                passw=generate_password_hash('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    app.run(host = '0.0.0.0' , debug=True , port = 5000)
