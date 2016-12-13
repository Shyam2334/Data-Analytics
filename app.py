from flask import Flask, request, render_template, redirect, flash, url_for, g, session, jsonify, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import os

#Create a engine for connecting to SQLite3.
#Assuming salaries.db is in your app root folder

e = create_engine('sqlite:///driver.db')

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__,template_folder=tmpl_dir)
api = Api(app)

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

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
     app.run(debug=True)