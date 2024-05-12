from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import logging

from lib import load_tracks, load_genres, add_genre_information_to_tracks, get_audio_features_for_tracks, \
    create_shuffled_list_of_genres, get_categories, format_categories, categorize_tracks, generate_spotify_playlists, \
    stream_categorization, get_total_tracks

# Set up logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
    logging.info('Creating categories')
    token = request.args.get('token')
    playlist_id = request.args.get('playlist_id')
    num_categories = request.args.get('num_categories')

    logging.info('Loading tracks')
    load_tracks(token, playlist_id)
    logging.info('Tracks loaded')

    logging.info('Loading genres')
    load_genres(token, playlist_id)
    logging.info('Genres loaded')

    logging.info('Adding genre information to tracks')
    add_genre_information_to_tracks(token, playlist_id)
    logging.info('added Genre information to tracks')

    logging.info('Getting audio features for tracks')
    get_audio_features_for_tracks(token, playlist_id)
    logging.info('Got Audio features for tracks')

    logging.info('Shuffling list of genres created')
    genres_text = create_shuffled_list_of_genres(playlist_id)
    logging.info('Shuffled list of genres created') 

    logging.info('Getting Categories')
    categories = get_categories(num_categories, genres_text)
    logging.info('Got Categories')

    return jsonify(categories)

@app.route('/total-tracks', methods=['GET'])
def total_tracks():
    logging.info('Getting total tracks')
    playlist_id = request.args.get('playlist_id')
    return jsonify({"total_tracks":  get_total_tracks(playlist_id)})

@app.route('/generate', methods=['POST'])
def generate_playlists():
    logging.info('Generating playlists')
    token = request.args.get('token')
    playlist_id = request.args.get('playlist_id')
    # get category data from POST request body
    categories = request.json['categories']
    total_tracks = get_total_tracks(playlist_id)
    logging.info('Total tracks: %s', total_tracks)

    generate_spotify_playlists(token, playlist_id, categories)
    logging.info('Playlists generated')
    logging.info('Streaming categorization started')
    response = Response(
        stream_with_context(stream_categorization(token, playlist_id, categories)),
        mimetype='application/json'
    )
    logging.info('Streaming categorization finished')
    response.headers['X-Total-Tracks'] = str(total_tracks)
    return response



if __name__ == '__main__':
    logging.info('Starting server')
    app.run(debug=True, port=5000)
