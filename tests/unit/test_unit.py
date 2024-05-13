
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch
import os
import pytest
import sys
from unittest.mock import patch
sys.path.insert(0, '../../server')
sys.path.insert(0, '../../')
from server import lib
from server.app import app as flask_app
import pandas as pd
import random

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_read_pickle():
    with patch('pandas.read_pickle') as mock:
        genres_data = {
            'genres': pd.Series([['rock', 'pop'], ['jazz'], ['blues', 'classical']])
        }
        df = pd.DataFrame(genres_data)
        mock.return_value = df
        yield mock


def test_exchange_code(client):
    with patch('requests.post') as mock_post:
        # Setup mock response
        mock_response = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'test_refresh_token',
            'scope': 'user-read-private user-read-email',
        }
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = mock_response

        response = client.get('/exchange-code', query_string={'code': 'test_code'})

        assert response.status_code == 200
        assert response.json == mock_response



def test_create_shuffled_list_of_genres(mock_read_pickle):
    playlist_id = '123'
    expected_genres = "rock, pop\nblues, classical\njazz"  

    random.seed(42)  
    genre_list = lib.create_shuffled_list_of_genres(playlist_id)

    # Check the output
    assert genre_list == expected_genres


@pytest.fixture
def mock_llm_chain():
    with patch('langchain.chains.LLMChain') as mock:
        mock_instance = mock.return_value
        mock_instance.run.return_value = "1. **Rock Genres**: Encompassing classic rock and modern rock.\n\n" \
                                         "2. **Pop Genres**: Covering all forms of pop music.\n\n"
        yield mock_instance

def test_get_categories_format():
    num_categories = 2
    genres_text = "Rock, Pop"

    categories = lib.get_categories(num_categories, genres_text)

    for category in categories:
        assert isinstance(category, dict), "Each category should be a dictionary."
        assert 'category_number' in category, "Each category should have a 'category_number'."
        assert 'category_name' in category, "Each category should have a 'category_name'."
        assert 'description' in category, "Each category should have a 'description'."
    