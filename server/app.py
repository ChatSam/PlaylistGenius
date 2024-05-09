from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests

from lib import load_tracks, load_genres, add_genre_information_to_tracks, get_audio_features_for_tracks, \
    create_shuffled_list_of_genres, get_categories, format_categories, categorize_tracks, generate_spotify_playlists, \
    stream_categorization, get_total_tracks

app = Flask(__name__)
CORS(app)

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
        print(response.json())
        return jsonify(response.json())
    else:
        print(response.json())
        return jsonify({"error": "Failed to retrieve access token"}), 400

@app.route('/categories', methods=['GET'])
def create_categories():
    token = request.args.get('token')
    playlist_id = request.args.get('playlist_id')
    num_categories = request.args.get('num_categories')
    load_tracks(token, playlist_id)
    load_genres(token, playlist_id)
    add_genre_information_to_tracks(token, playlist_id)
    get_audio_features_for_tracks(token, playlist_id)
    genres_text = create_shuffled_list_of_genres(playlist_id)
    categories = get_categories(num_categories, genres_text)
    return jsonify(categories)

@app.route('/total-tracks', methods=['GET'])
def total_tracks():
    playlist_id = request.args.get('playlist_id')
    return jsonify({"total_tracks":  get_total_tracks(playlist_id)})

@app.route('/generate', methods=['POST'])
def generate_playlists():
    token = request.args.get('token')
    playlist_id = request.args.get('playlist_id')
    # get category data from POST request body
    categories = request.json['categories']
    total_tracks = get_total_tracks(playlist_id)

    generate_spotify_playlists(token, playlist_id, categories)

    response = Response(
        stream_with_context(stream_categorization(token, playlist_id, categories)),
        mimetype='application/json'
    )
    response.headers['X-Total-Tracks'] = str(total_tracks)
    return response



if __name__ == '__main__':
    app.run(debug=True, port=5000)
