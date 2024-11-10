from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import os
from elevenlabs.client import ElevenLabs

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
SERVER_DOMAIN = os.getenv('SERVER_DOMAIN', 'localhost')

# ElevenLabs API Key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

@app.route('/call/outgoing', methods=['POST'])
def outgoing_call():
    """
    Initiates an outgoing call and streams ElevenLabs audio.
    """
    data = request.json
    to_phone = data.get('to')  # Recipient's phone number
    from_phone = TWILIO_PHONE_NUMBER  # Twilio phone number
    twiml_url = f'https://{SERVER_DOMAIN}/twiml'

    try:
        # Create an outgoing call with Twilio
        call = client.calls.create(
            to=to_phone,
            from_=from_phone,
            url=twiml_url  # TwiML endpoint to stream audio
        )
        return jsonify({'status': 'success', 'call_sid': call.sid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/twiml', methods=['POST'])
def twiml_response():
    """
    Generates TwiML response with <Stream> to connect ElevenLabs audio.
    """
    response = VoiceResponse()
    connect = Connect()
    connect.stream(
        url=f'wss://{SERVER_DOMAIN}/call/stream',  # WebSocket URL for streaming
        name='elevenlabs-stream'  # Optional name
    )
    response.append(connect)
    return str(response)

@app.route('/call/stream', methods=['POST'])
def stream_audio():
    """
    Streams ElevenLabs audio into the call over WebSocket.
    """
    # Example: ElevenLabs Text-to-Speech
    text = "Hello! This is an ElevenLabs test message. Enjoy the call."
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Replace with your voice ID
    stream_url = f'https://{SERVER_DOMAIN}/call/stream'

    # Generate ElevenLabs audio
    audio_stream = eleven_client.tts.generate_stream(
        text=text,
        voice_id=voice_id,
        output_format="ulaw_8000"
    )

    # Stream audio to the call
    return audio_stream

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 5000)), debug=True)