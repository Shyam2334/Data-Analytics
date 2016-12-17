from flask import Flask, request, render_template, redirect, flash, url_for, g, session, jsonify, make_response
#from flask_login import LoginManager, login_user, logout_user, current_user, login_required, AnonymousUserMixin
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from json import dumps
from flask_wtf import Form
import os

#Create a engine for connecting to SQLite3.
#Assuming salaries.db is in your app root folder

e = create_engine('sqlite:///driver.db')

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__,template_folder=tmpl_dir)
app.config['SECRET_KEY']='THIS IS AN INSECURE SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basic_app.sqlite'
app.config['USER_SEND_PASSWORD_CHANGED_EMAIL'] = False
app.config['USER_SEND_REGISTERED_EMAIL'] = False
app.config['USER_SEND_USERNAME_CHANGED_EMAIL'] = False
app.config['USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL = False'] = True
app.config['USER_AUTO_LOGIN'] = True
app.config['CSRF_ENABLED'] = True
api = Api(app)

# Initialize Flask extensions
db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy


    # Define the User data model. Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

        # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    # Create all database tables
db.create_all()

    # Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

class Users_All(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select * from users")
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return result

class Users_Meta(Resource):
    def get(self,id):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select * from users where id=%i"%id)
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return result

class Trips_Meta(Resource):
    def get(self,id):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select * from trips where user_id=%i"%id)
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return result

class Trips_details(Resource):
    def get(self,id):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        for row in conn.execute("select count(distinct id),sum(distance),sum(duration),sum(score) from trips where user_id=%i"%id):
        	Count = row[0]
        	dist = row[1]
        	duration = row[2]
        	average_score = row[3]
        SpeedThresholdExceeded = 0
        for row in conn.execute("select avg(speed) from events where trip_id in ( select distinct id from trips where user_id=%i)"%id):
            average_speed = row[0]
        #print Count,dist,duration,average_score
        result = [{'average_speed':average_speed,'total_trips':Count,'duration':duration,'dist':dist,'average_score':float(average_score/Count)}]
        return result
       

class Events_Meta(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select * from events")
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return result

class Speed_details(Resource):
    def get(self,id):
        conn = e.connect()
        query = conn.execute("select trip_id,count(distinct id) from events where event_type='SpeedThresholdExceeded' and trip_id in ( select distinct id from trips where user_id=%i) group by trip_id"%id)
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return  result

class Behaviour_details(Resource):
    def get(self,id):
        conn = e.connect()
        query = conn.execute("select event_type,count(distinct id) from events where event_type in ('SpeedThresholdExceeded','RapidAcceleration','HardBraking','GeneralPhoneHandling') and trip_id in ( select distinct id from trips where user_id=%i) group by event_type"%id)
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        return  result

api.add_resource(Users_Meta, '/users/<int:id>')
api.add_resource(Trips_Meta, '/trips/<int:id>')
api.add_resource(Trips_details, '/trips_details/<int:id>')
api.add_resource(Speed_details, '/speed_details/<int:id>')
api.add_resource(Behaviour_details, '/behaviour_details/<int:id>')
api.add_resource(Events_Meta, '/events')
api.add_resource(Users_All,'/all_drivers')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/driver')
@login_required
def driver():
    return render_template('index.html')

if __name__ == '__main__':
     app.run(debug=True)