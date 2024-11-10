from flask import Flask, jsonify, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

import os
import signal

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=API_KEY)

conversation = Conversation(
    # API client and agent ID.
    client,
    AGENT_ID,

    # Assume auth is required when API_KEY is set.
    requires_auth=bool(API_KEY),

    # Use the default audio interface.
    audio_interface=DefaultAudioInterface(),

    # Simple callbacks that print the conversation to the console.
    callback_agent_response=lambda response: print(f"Agent: {response}"),
    callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),

    # Uncomment if you want to see latency measurements.
    # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
)

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a sample model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10))
    address = db.Column(db.String(50))
    patient_name = db.Column(db.String(50), nullable=False)
    health = db.Column(db.JSON)

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'phone': self.phone,
            'address': self.address,
            'patient_name': self.patient_name,
            'health': self.health
        }

class ConversationTemplate(db.Model):
    convo_template_id = db.Column(db.Integer, primary_key=True)
    convo_name = db.Column(db.String(50))
    convo_workflow = db.Column(db.JSON)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    convo_template_id = db.Column(db.Integer, db.ForeignKey('conversation_template.convo_template_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    end_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    frequency = db.Column(db.String)

class Call(db.Model):
    call_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    convo_template_id = db.Column(db.Integer, db.ForeignKey('conversation_template.convo_template_id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), nullable=False)
    transcript = db.Column(db.JSON)
    audio = db.Column(db.String(100))  # S3 Bucket reference
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())


# Create the tables
with app.app_context():
    db.create_all()  # This will create example.db and tables if they don't exist

# Sample data to simulate database records
# patients = [
#     {"patient_id": 1, "phone": "1234567890", "address": "123 Main St", "customer_name": "John Doe", "health": {}},
#     {"patient_id": 2, "phone": "0987654321", "address": "456 Elm St", "customer_name": "Jane Smith", "health": {}}
# ]

# conversation_templates = [
#     {"id": 1, "name": "New Patient", "convo_workflow": {}, "last_updated": "2023-01-01"},
#     {"id": 2, "name": "Medical Checkup", "convo_workflow": {}, "last_updated": "2023-02-01"}
# ]

# schedules = [
#     {"schedule_id": 1, "convo_template_id": 1, "start_date": "2023-01-01 10:00:00", "end_date": "2023-01-01 11:00:00", "frequency": "1D"},
#     {"schedule_id": 2, "convo_template_id": 2, "start_date": "2023-02-01 10:00:00", "end_date": "2023-02-01 11:00:00", "frequency": "2W"}
# ]

# calls = [
#     {"call_id": 1, "patient_id": 1, "convo_template_id": 1, "schedule_id": 1, "transcript": {}, "audio": "audio1.mp3", "timestamp": "2023-01-01 10:00:00"},
#     {"call_id": 2, "patient_id": 2, "convo_template_id": 2, "schedule_id": 2, "transcript": {}, "audio": "audio2.mp3", "timestamp": "2023-02-01 10:00:00"}
# ]


@app.route('/')
def home():
    patients = Patient.query.all()
    patients_dict = [patient.to_dict() for patient in patients]

    return render_template('home2.html',  patients=patients_dict)

@app.route('/scheduler', methods=['GET', 'POST'])
def scheduler():

    schedules = Schedule.query.all()
    conversation_templates = ConversationTemplate.query.all()
    
    if request.method == 'POST':

        r = request.json
        if r:
            new_schedule_entry = Schedule(
                schedule_id=len(schedules) + 1,
                convo_template_id=int(r['conversationTemplateId']),
                start_date=datetime.strptime(r['startDate'], '%Y-%m-%d'),
                end_date=datetime.strptime(r['endDate'], '%Y-%m-%d'),
                frequency=r['frequency']
            )
            db.session.add(new_schedule_entry)
            db.session.commit()

    return render_template('scheduler.html', schedules=schedules, current_date="2024-11-09", conversation_templates=conversation_templates)


@app.route('/convo-workflow', methods=['GET', 'POST'])
def convo_workflow():

    schedules = Schedule.query.all()
    conversation_templates = ConversationTemplate.query.all()

    if request.method == 'POST':
        print("post")
        
    return render_template('convo-workflow.html', schedules=schedules, conversation_templates=conversation_templates)

@app.route('/patient', methods=['GET', 'POST'])
def patient():

    patients = Patient.query.all()
    patients_dict = [patient.to_dict() for patient in patients]
    calls = Call.query.all()

    if request.method == 'POST':
        print("post")

    return render_template('patient.html', patients=patients_dict, calls=calls)

@app.route('/start-convo',methods=['GET', 'POST'])
def start_convo():
    conversation.start_session()

@app.route('/end-convo', methods=['GET','POST'])
def end_convo():
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())
    conversation_id = conversation.wait_for_session_end()
    print(f"Conversation ID: {conversation_id}")

import requests

# Define the URL
url = 'https://api.us.elevenlabs.io/v1/convai/conversations/j1j4DLVqmLODCKJwQ3C1'

# Define the headers
headers = {
    'Host': 'api.us.elevenlabs.io',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImI4Y2FjOTViNGE1YWNkZTBiOTY1NzJkZWU4YzhjOTVlZWU0OGNjY2QiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiUmV2YW50aCBLb3JyYXBvbHUiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSlJNQWVBNl82NWpmaE9wdUhMdlotZ25RVmRMNXU5LTFGLWh1TnNzd1RGQVRWSHQyVHNmQT1zOTYtYyIsIndvcmtzcGFjZV9pZCI6IjE2Yzk2OGZlMjU5MjQwOWE4MmQxOWVhMzg1Nzg0NzIxIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL3hpLWxhYnMiLCJhdWQiOiJ4aS1sYWJzIiwiYXV0aF90aW1lIjoxNzMxMTc0NDQzLCJ1c2VyX2lkIjoiSk8yNk9YQlM2RVF1OGwwNHlnOEkweU5Jb2pVMiIsInN1YiI6IkpPMjZPWEJTNkVRdThsMDR5ZzhJMHlOSW9qVTIiLCJpYXQiOjE3MzEyNTU3NDksImV4cCI6MTczMTI1OTM0OSwiZW1haWwiOiJyZXZrcm9ja0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJnb29nbGUuY29tIjpbIjExMDkwNDg3MDcxNDQzNjI3MjA4NyJdLCJlbWFpbCI6WyJyZXZrcm9ja0BnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.fqUysn_mVD19SjoqTgbTuJK8I0xsC_S4Ckb-uaI-jP5HjfIkeJXReo-MXr33uFr818_ALaMkkK6-DCbLgyAW8bAMc5bSGaK3NqkSZ4AMJg_zL4eJdb03ASG3Bt8_450wPtaVhMf6uCmqhkRJdL0StgAERMQrLd1IvqJg0dWWssv-24pjF33sFsqCcoTi4aufHhaGFNTrAU7Le2kvZTDpuerC9ERSEM0Otjod61U4wRnu80bF4zi9h2t0lrKG34uEYssSBVGfi06ivAIoWU3ruOoA8pm2RSw-2ykgBdk-5vvs3L_YBJuEY7RH4AnT7MJgB1uteRnqePxfkncXyRWo1Q',
    'Content-Type': 'application/json'
}

# Define the proxy
proxies = {
    'http': 'http://localhost:9090',
    'https': 'http://localhost:9090'
}


@app.route('/get-convo-data', methods=['GET','POST'])
def get_convo_data():
    response = requests.get(url, headers=headers, proxies=proxies)

    # Print the response
    r = response.json()

    if r:
        new_schedule_entry = Schedule(
            schedule_id=len(schedules) + 1,
            convo_template_id=int(r['conversationTemplateId']),
            start_date=datetime.strptime(r['startDate'], '%Y-%m-%d'),
            end_date=datetime.strptime(r['endDate'], '%Y-%m-%d'),
            frequency=r['frequency']
        )
        db.session.add(new_schedule_entry)
        db.session.commit()

    return r['analysis']['data_collection_results']['New Information on General Check']['value'], 200
    


if __name__ == '__main__':
    app.run(debug=True)
