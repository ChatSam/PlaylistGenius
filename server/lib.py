import json
from datetime import datetime
import random
import re
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import pandas as pd
import spotipy
from tqdm import tqdm


def load_tracks(token, playlist_id):
    sp = spotipy.Spotify(auth=token)

    if Path(f'playlist-{playlist_id}.pkl').exists():
        df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    else:
        df = pd.DataFrame()

    items = []
    offset = 0
    page = 100

    results = sp.playlist_tracks(playlist_id=playlist_id)
    total = results['total']

    for i in tqdm(range(0, total)):
        if i != 0 and i % page == 0:
            offset += page
            results = sp.playlist_tracks(playlist_id=playlist_id, offset=offset)

        item = results['items'][i % page]
        track = item['track']

        if track['id'] in df.index:
            continue

        album_images = track['album'].get('images', [])
        thumbnail_url = album_images[0]['url'] if album_images else None

        d = {'id': track['id'],
             'uri': track['uri'],
             'popularity': track['popularity'],
             'album': track['album']['name'],
             'artists': [artist['name'] for artist in track['artists']],
             'artists_id': [artist['id'] for artist in track['artists']],
             'name': track['name'],
             'release_date': track['album']['release_date'],
             'thumbnail_url': thumbnail_url}
        items.append(d)

    if len(items) > 0:
        print(f'Adding {len(items)} new tracks')
        df_new_tracks = pd.DataFrame(items)
        df_new_tracks.set_index('id', inplace=True)
        df = pd.concat([df, df_new_tracks])

        df.to_pickle(f'playlist-{playlist_id}.pkl')
    else:
        print('No new tracks')

def load_genres(token, playlist_id):
    sp = spotipy.Spotify(auth=token)

    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    all_artists = df['artists_id'].explode().unique().tolist()

    if Path('artists.pkl').exists():
        df_artists = pd.read_pickle(f'artists.pkl')
        existing_artists = set(df_artists.index)
        all_artists = [artist for artist in all_artists if artist not in existing_artists]
    else:
        df_artists = pd.DataFrame()

    total = len(all_artists)

    items = []
    offset = 0
    page = 50

    for i in tqdm(range(0, total)):
        if i % page == 0:
            try:
                results = sp.artists(all_artists[offset:offset+page])
            except Exception as e:
                # print(f'Error: {e}')
                break
            offset += page

        artist = results['artists'][i % page]
        d = {'id': artist['id'], 'genres': artist['genres'], 'popularity': artist['popularity']}
        items.append(d)

    if len(items) > 0:
        print(f'Adding {len(items)} new artists')
        df_new_artists = pd.DataFrame(items)
        df_new_artists.set_index('id', inplace=True)
        df_artists = pd.concat([df_artists, df_new_artists])

        df_artists.to_pickle(f'artists.pkl')
    else:
        print('No new artists')

def add_genre_information_to_tracks(token, playlist_id):
    sp = spotipy.Spotify(auth=token)

    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    df_artists = pd.read_pickle(f'artists.pkl')

    items = []

    for i, x in tqdm(df.iterrows(), total=len(df)):
        if 'genres' in x and pd.notna(x['genres']):
            continue

        genres = set()
        for artist_id in x['artists_id']:
            artist = df_artists.loc[artist_id]
            for genre in artist['genres']:
                if genre not in genres:
                    genres.add(genre)
        items.append({'id': i, 'genres': tuple(genres)})


    if len(items) > 0:
        df_genres = pd.DataFrame(items)
        df_genres.set_index('id', inplace=True)
        df = pd.concat([df, df_genres], axis=1)

        df.to_pickle(f'playlist-{playlist_id}.pkl')
        print(f'Added genre information to {len(items)} tracks')
    else:
        print('No genre information added.')

def get_audio_features_for_tracks(token, playlist_id):
    sp = spotipy.Spotify(auth=token)

    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    track_ids = df.index.tolist()
    if 'acousticness' in df.columns:
        track_ids_with_audio_features = set(df[df['acousticness'].notna()].index)
        track_ids = [track_id for track_id in track_ids if track_id not in track_ids_with_audio_features]

    total = len(track_ids)
    offset = 0
    page = 100

    seen = 0
    for i in tqdm(range(0, total)):
        seen = i
        if i % page == 0:
            try:
                results = sp.audio_features(track_ids[offset:offset+page])
            except Exception as e:
                # print(f'Error: {e}')
                break
            offset += page

        audio_features = results[i % page]
        for feature in ['acousticness',
                        'danceability',
                        'duration_ms',
                        'energy',
                        'instrumentalness',
                        'key',
                        'liveness',
                        'loudness',
                        'mode',
                        'speechiness',
                        'tempo',
                        'time_signature',
                        'valence']:
            df.loc[audio_features['id'], feature] = audio_features[feature]

    if seen > 0:
        print(f'Adding {i} new audio features')
        df.to_pickle(f'playlist-{playlist_id}.pkl')
    else:
        print('No new audio features')

def create_shuffled_list_of_genres(playlist_id):
    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    genres_list = (df[df['genres'].apply(lambda x: len(x) > 0)]['genres']).apply(lambda x: ", ".join(x)).tolist()
    random.seed(0)
    random.shuffle(genres_list)
    genres_text = "\n".join(genres_list)
    return genres_text

prompt_categories = PromptTemplate.from_template(
    "I have a list of songs, each with one or more genres associated with it. Based on these genres, I would like you "
    "to analyze the list and create {num_categories} distinct categories that these songs could be grouped into. Each "
    "category should represent a unique theme or commonality found within the genres. Please provide a brief "
    "description for each category to explain the common theme or elements that define it.\nPlease output each "
    "category using the following format:\n[[NUMBER]]. **[[TITLE]]**: [[DESCRIPTION]]\n\nHere is the list of songs and "
    "their associated genres:\n\n{genres_text}\n\n"
    "Remember, the categories must be exactly {num_categories}."
)
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
chain_categories = LLMChain(llm=llm, prompt=prompt_categories, verbose=True)

def get_categories(num_categories, genres_text):
    # print(f'length of genres_text: {len(genres_text)}')
    # print(f'Genres text: {genres_text}')
    categories_output = chain_categories.run(num_categories=num_categories, genres_text=genres_text[:50000])

    print(categories_output)

    # Updated regex pattern to ensure entire descriptions are captured
    pattern = r"(\d+)\.\s*([^:]+):\s*((?:.(?!\n\s*\d+\.))+.)"
    matches = re.findall(pattern, categories_output, re.DOTALL)

    categories = {int(num): (name.strip(), desc.strip()) for num, name, desc in matches}

    data = [{'category_number': category_number,
             'category_name': category_name,
             'description': description
             } for category_number, (category_name, description) in categories.items()]

    return data

prompt_categorize = PromptTemplate.from_template(
    """Given a list of categories and their descriptions, please determine which category the following song fits best into. Use the song's genres, along with any other relevant information provided, to make your decision. After making your decision, structure your response as follows: Start with "Category number:" followed by the number of the category. Then, on a new line, write "Category name:" followed by the name of the category. Then, on a new line, write "Reasoning:" followed by a brief explanation of why the song fits best in the chosen category. Here are the categories:

{categories_output}

Song Information:

    Name: {name}
    Artists: {artists}
    Album: {album}
    Release Date: {release_date}
    Genres: {genres}
    Popularity: {popularity}
    Danceability: {danceability}
    Energy: {energy}
    Key: {key}
    Loudness: {loudness}
    Mode: {mode}
    Speechiness: {speechiness}
    Acousticness: {acousticness}
    Instrumentalness: {instrumentalness}
    Liveness: {liveness}
    Valence: {valence}
    Tempo: {tempo}
    Duration MS: {duration_ms}
    Time Signature: {time_signature}

Based on the genres listed and any other information you deem relevant from the song information provided, which of the categories does "{name}" by {artists} fit best into? Please explain your reasoning.""",
)

def format_categories(categories):
    categories_output = "\n\n".join([f"{category['category_number']}. {category['category_name']}: {category['description']}" for category in categories])
    return categories_output

chain_categorize = LLMChain(llm=llm, prompt=prompt_categorize, verbose=True)
def categorize_track(categories_output, track):
    output = chain_categorize.run(categories_output=categories_output,
                       name=track['name'],
                       artists=", ".join(track['artists']),
                       album=track['album'],
                       release_date=track['release_date'],
                       genres=track['genres'],
                       popularity=track['popularity'],
                       danceability=track['danceability'],
                       energy=track['energy'],
                       key=track['key'],
                       loudness=track['loudness'],
                       mode=track['mode'],
                       speechiness=track['speechiness'],
                       acousticness=track['acousticness'],
                       instrumentalness=track['instrumentalness'],
                       liveness=track['liveness'],
                       valence=track['valence'],
                       tempo=track['tempo'],
                       duration_ms=track['duration_ms'],
                       time_signature=track['time_signature'])

    pattern = r"Category number: (\d+)\s+Category name: ([\w\s]+)\s+Reasoning: (.+)"
    # Search for the pattern in the LLM output
    match = re.search(pattern, output, re.DOTALL)

    if match:
        # Extract the category number, name, and reasoning from the match
        category_number = int(match.group(1))
        category_name = match.group(2).strip()
        reasoning = match.group(3).strip()

        return category_number, category_name, reasoning
    else:
        raise ValueError("Failed to extract category information from LLM output")

def generate_spotify_playlists(token, playlist_id, categories):
    sp = spotipy.Spotify(auth=token)

    print('Creating playlists')
    user_id = sp.current_user()['id']
    playlist_nane = sp.playlist(playlist_id)['name']
    for category in categories:
        category_name = category['category_name'].replace('*', '')
        description = re.sub(r'\n+', ' ', category['description'])[:512]
        category['category_number'] = str(category['category_number'])

        timestamp = datetime.now().isoformat()[:16].replace(':', '')
        playlist_name = f"{playlist_nane} - {category_name.replace('*', '')}_{timestamp}"
        result = sp.user_playlist_create(user=user_id,
                                         name=playlist_name,
                                         public=False,
                                         description=description)
        created_playlist_id = result['id']
        category['playlist_id'] = created_playlist_id

    return categories

def categorize_tracks(token, playlist_id, categories):
    sp = spotipy.Spotify(auth=token)

    categories_output = format_categories(categories)
    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    categorized_tracks = []

    for i, track in tqdm(df.iterrows(), total=len(df)):
        try:
            category_number, category_name, reasoning = categorize_track(categories_output, track)
        except ValueError as e:
            print(f'Error: {e}')
            continue
        categorized_tracks.append({'track_name': track['name'],
                                                      'artists': track['artists'],
                                                      'album': track['album'],
                                                      'release_date': track['release_date'],
                                                      # 'genres': track['genres'],
                                                      # 'popularity': track['popularity'],
                                                      # 'danceability': track['danceability'],
                                                      # 'energy': track['energy'],
                                                      # 'key': track['key'],
                                                      # 'loudness': track['loudness'],
                                                      # 'mode': track['mode'],
                                                      # 'speechiness': track['speechiness'],
                                                      # 'acousticness': track['acousticness'],
                                                      # 'instrumentalness': track['instrumentalness'],
                                                      # 'liveness': track['liveness'],
                                                      # 'valence': track['valence'],
                                                      # 'tempo': track['tempo'],
                                                      # 'duration_ms': track['duration_ms'],
                                                      # 'time_signature': track['time_signature'],
                                                      'category_name': category_name,
                                                    'category_number': category_number,
                                                      'reasoning': reasoning})
        new_playlist_id = categories[category_number-1]['playlist_id']
        sp.playlist_add_items(playlist_id=new_playlist_id, items=[track['uri']])

    return categorized_tracks


def get_total_tracks(playlist_id):
    return pd.read_pickle(f'playlist-{playlist_id}.pkl').shape[0]


def stream_categorization(token, playlist_id, categories):
    sp = spotipy.Spotify(auth=token)
    categories_output = format_categories(categories)
    df = pd.read_pickle(f'playlist-{playlist_id}.pkl')
    categorized_tracks = []

    yield '[\n'

    first = True
    for i, track in tqdm(df.iterrows(), total=len(df)):
        try:
            category_number, category_name, reasoning = categorize_track(categories_output, track)
        except ValueError as e:
            print(f'Error: {e}')
            continue
        track_info = {
            'thumbnail_url': track['thumbnail_url'],
            'track_name': track['name'],
            'artists': track['artists'],
            'album': track['album'],
            'release_date': track['release_date'],
            'category_name': category_name,
            'category_number': category_number,
            'reasoning': reasoning
        }
        categorized_tracks.append(track_info)

        new_playlist_id = categories[category_number - 1]['playlist_id']
        sp.playlist_add_items(playlist_id=new_playlist_id, items=[track['uri']])

        if not first:
            yield ',\n'
        else:
            first = False

        yield json.dumps(track_info)

    yield '\n]'