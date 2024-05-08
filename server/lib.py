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

        d = {'id': track['id'],
             'uri': track['uri'],
             'popularity': track['popularity'],
             'album': track['album']['name'],
             'artists': [artist['name'] for artist in track['artists']],
             'artists_id': [artist['id'] for artist in track['artists']],
             'name': track['name'],
             'release_date': track['album']['release_date']}
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
    "their associated genres:\n\n{genres_text}",
)
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
chain_categories = LLMChain(llm=llm, prompt=prompt_categories, verbose=True)

def get_categories(num_categories, genres_text):

    categories_output = chain_categories.run(num_categories=num_categories, genres_text=genres_text)

    # Updated regex pattern to ensure entire descriptions are captured
    pattern = r"(\d+)\.\s*([^:]+):\s*((?:.(?!\n\s*\d+\.))+.)"

    matches = re.findall(pattern, categories_output, re.DOTALL)

    categories = {int(num): (name.strip(), desc.strip()) for num, name, desc in matches}

    data = [{'category_number': category_number,
             'category_name': category_name,
             'description': description
             } for category_number, (category_name, description) in categories.items()]

    return data

