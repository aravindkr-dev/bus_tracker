from flask import Flask, request, render_template, jsonify, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


usera = None

app = Flask('__name__'  , template_folder='templates')
user_locations = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./abcd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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



@app.route('/')
def index():
    return render_template('user.html' , user_id = usera)

@app.route('/admin')
def admin():
    return render_template('admin.html')

"""@app.route('/location', methods=['POST'])
def receive_location():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    lat = data['latitude']
    lon = data['longitude']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if user_id not in user_locations:
        user_locations[user_id] = {
            'trail': [],
            'color': '#' + ''.join([hex(ord(c) % 16)[2:] for c in user_id[:3]])
        }

    user_locations[user_id]['trail'].append({
        'lat': lat,
        'lon': lon,
        'timestamp': timestamp
    })

    if len(user_locations[user_id]['trail']) > 20:
        user_locations[user_id]['trail'] = user_locations[user_id]['trail'][-20:]

    return 'Location received'"""

@app.route('/locations')
def get_locations():
    return jsonify(user_locations)


@app.route('/location', methods=['POST'])
def receive_location():
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
    global usera
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        data = Mytable.query.all()
        cred = ([x.to_dict() for x in data])
        print(cred)
        for x in cred:
            if x['name'] == user and x['passw'] == passw and x['role'] == 'student':
                usera = x['name']
                return 'ok'
            elif x['name'] == user and x['passw'] == passw and x['role'] == 'admin':
                return 'admin'
        return 'not ok'
    elif request.method == 'GET':
        return render_template('login.html')



if __name__ == '__main__':
    """ app.app_context().push()"""
    with app.app_context():
        db.create_all()
    app.run(host = '0.0.0.0' , debug=True)
