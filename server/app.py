import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

load_dotenv()

client_id = os.environ.get('CLIENT_ID', '61a763c599484a729f9b5a31c1057143')
client_secret = os.environ.get('CLIENT_SECRET')
redirect_uri = os.environ.get('REDIRECT_URI', 'http://localhost:3000')


@app.route('/exchange-code', methods=['GET'])
def exchange_code():
    code = request.args.get('code')

    # Prepare the request for exchanging the code for an access token
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    # Make the request
    response = requests.post(token_url, data=payload)

    # Handle the response
    if response.ok:
        # Send the access token back to the frontend
        return jsonify(response.json())
    else:
        print(response.json())
        return jsonify({"error": "Failed to retrieve access token"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
