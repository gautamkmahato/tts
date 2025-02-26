# server.py

from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os
from supabase import create_client
import uuid

from tts_handler import generate_speech, get_models, get_voices
from utils import require_api_key, AUDIO_FORMAT_MIME_TYPES

app = Flask(__name__)
load_dotenv()

# Initialize Supabase
SUPABASE_URL = "https://liwhmzelbdivxwpfhcez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxpd2htemVsYmRpdnh3cGZoY2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MjUzMDYsImV4cCI6MjA1NTIwMTMwNn0.77Jgs6J2uXxNaTlPFiGoXsxVHPjkC-x8Y-PcbPkMOKc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


API_KEY = os.getenv('API_KEY', 'your_api_key_here')
PORT = int(os.getenv('PORT', 5050))

DEFAULT_VOICE = os.getenv('DEFAULT_VOICE', 'en-US-AndrewNeural')
DEFAULT_RESPONSE_FORMAT = os.getenv('DEFAULT_RESPONSE_FORMAT', 'mp3')
DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', 1.0))

# DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'tts-1')

@app.route("/")
def hello_world():
    return "<h1>Hello, World!</h1>"

@app.route('/v1/audio/speech', methods=['POST'])
@require_api_key
def text_to_speech():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Missing 'input' in request body"}), 400

    text = data.get('input')
    # model = data.get('model', DEFAULT_MODEL)
    voice = data.get('voice', DEFAULT_VOICE)

    response_format = data.get('response_format', DEFAULT_RESPONSE_FORMAT)
    speed = float(data.get('speed', DEFAULT_SPEED))
    
    mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, "audio/mpeg")

    # # Generate the audio file in the specified format with speed adjustment
    # output_file_path = generate_speech(text, voice, response_format, speed)

    # # Return the file with the correct MIME type
    # return send_file(output_file_path, mimetype=mime_type, as_attachment=True, download_name=f"speech.{response_format}")

    # Generate the audio file
    output_file_path = generate_speech(text, voice, response_format, speed)
    # file_name = f"speech.{response_format}"
    file_name = f"speech_{uuid.uuid4().hex}.{response_format}"

    # Upload the file to Supabase Storage
    with open(output_file_path, "rb") as audio_file:
        res = supabase.storage.from_("tts-audio").upload(file_name, audio_file.read(), file_options={"content-type": mime_type})
        print("Supabase response:", res)
    
    # if res.get("error"):
    #     return jsonify({"error": "Failed to upload file to Supabase"}), 500

    # Get the public URL of the uploaded file
    print("----------------public_url-----------------")
    public_url = supabase.storage.from_("tts-audio").get_public_url(file_name)
    print(public_url)

    return jsonify({"success": True, "uploadResponse": res, "file_url": public_url})

@app.route('/v1/models', methods=['GET', 'POST'])
@require_api_key
def list_models():
    return jsonify({"data": get_models()})

@app.route('/v1/voices', methods=['GET', 'POST'])
@require_api_key
def list_voices():
    specific_language = None

    data = request.args if request.method == 'GET' else request.json
    if data and ('language' in data or 'locale' in data):
        specific_language = data.get('language') if 'language' in data else data.get('locale')

    return jsonify({"voices": get_voices(specific_language)})

@app.route('/v1/voices/all', methods=['GET', 'POST'])
@require_api_key
def list_all_voices():
    return jsonify({"voices": get_voices('all')})

print(f" Edge TTS (Free Azure TTS) Replacement for OpenAI's TTS API")
print(f" ")
print(f" * Serving OpenAI Edge TTS")
print(f" * Server running on http://localhost:{PORT}")
print(f" * TTS Endpoint: http://localhost:{PORT}/v1/audio/speech")
print(f" ")

# if __name__ == '__main__':
#     http_server = WSGIServer(('0.0.0.0', PORT), app)
#     http_server.serve_forever()

if __name__ == '__main__':
    from gunicorn.app.wsgiapp import run
    run()
