from flask import Flask
from functools import wraps
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")

API_KEY = os.getenv('API_KEY', 'your_api_key_here')
REQUIRE_API_KEY = getenv_bool('REQUIRE_API_KEY', True)

print(API_KEY)

@app.route('/')
def hello_world():
    return "Hello World!"
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')