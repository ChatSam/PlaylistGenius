import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams, useLocation } from 'react-router-dom';
import './GenerateResults.css';

const GenerateResults = () => {
    const navigate = useNavigate();
    const { playlistId } = useParams();
    const [searchParams] = useSearchParams();
    const numCategories = searchParams.get('numCategories') || 5;
    const { state } = useLocation();
    const { categories } = state || {};
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('spotify_access_token');

        if (!token) {
            setError('No Spotify access token found');
            setLoading(false);
            return;
        }

        const fetchResults = async () => {
            try {
                const response = await fetch(`http://localhost:5000/generate?token=${token}&playlist_id=${playlistId}&num_categories=${numCategories}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ categories })
                });

                const data = await response.json();
                if (response.ok) {
                    setResults(data);
                } else {
                    setError(data.error || 'Unable to generate results');
                }
            } catch (error) {
                setError('An error occurred while fetching results');
            } finally {
                setLoading(false);
            }
        };

        if (categories) {
            fetchResults();
        } else {
            setError('No categories available for generation');
            setLoading(false);
        }
    }, [playlistId, numCategories, categories]);

    return (
        <div className="generate-results-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Generated Results for Playlist: {playlistId}</h2>

            {loading ? (
                <p>Loading results...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <div className="results-list">
                    {results.map((songs, index) => (
                        <div key={index} className="result-category">
                            <h3>{categories[index].category_name}</h3>
                            <p>{categories[index].description}</p>
                            <ul>
                                {songs.map((song, idx) => (
                                    <li key={idx}>
                                        <strong>{song.track_name}</strong> - {song.artists.join(', ')}
                                        <br />
                                        <small>{song.reasoning}</small>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default GenerateResults;
