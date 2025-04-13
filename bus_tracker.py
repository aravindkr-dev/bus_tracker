from flask import Flask, request, render_template, jsonify, session, redirect , url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sympy.codegen.ast import continue_


app = Flask('__name__'  , template_folder='templates')
user_locations = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./abcd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


app.secret_key = 'secret'

class Mytable(db.Model):
    __tablename__ = 'user_cred'

    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(30) , nullable = False , unique = True)
    passw = db.Column(db.String(60) , nullable = False)
    role = db.Column(db.String(30) , nullable = False)

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'passw':self.passw,
            'role':self.role
        }


def verify():
    if 'username' not in session:
        print("User Not Logged In")
        return False
    return True



@app.route('/')
def dashboard():
    v = verify()
    if v:
        return render_template('dashboard.html' , user_id = session.get('username'))
    else:
        return redirect(url_for('login'))





@app.route('/bus')
def bus():
    if not verify() and session['role'] != 'bus':
        return redirect(url_for('login'))
    return render_template('bus.html')

@app.route('/view_bus')
def view_bus():
    if not verify() or session.get('role') == 'student':
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

            obj = Mytable(name = user_name , passw = passw , role = 'student')
            db.session.add(obj)
            db.session.commit()
    return render_template('signup.html')


@app.route('/login' , methods = ['GET' , 'POST'])

def login():
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        data = Mytable.query.all()
        cred = ([x.to_dict() for x in data])
        print(cred)
        for x in cred:
            if x['name'] == user and x['passw'] == passw and x['role'] == 'student':
                session['username'] = x['name']
                session['role'] = x['role']
                return redirect(url_for('dashboard'))
            elif x['name'] == user and x['passw'] == passw and x['role'] == 'admin':
                session['username'] = x['name']
                session['role'] = x['role']
                return 'admin'
        return redirect(url_for('view_bus'))
    elif request.method == 'GET':
        return render_template('login.html')



if __name__ == '__main__':
    """ app.app_context().push()"""
    with app.app_context():
        db.create_all()
    app.run(host = '0.0.0.0' , debug=True , port = 5000)
