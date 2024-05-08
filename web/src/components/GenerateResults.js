import React, { useEffect, useState, useRef } from 'react';
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
    const [activeTab, setActiveTab] = useState(0);
    const fetchOnce = useRef(false);

    useEffect(() => {
        if (fetchOnce.current || !categories) {
            setLoading(false);
            return;
        }

        fetchOnce.current = true;

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

        fetchResults();
    }, [playlistId, numCategories, categories]);

    const handleTabClick = (index) => {
        setActiveTab(index);
    };

    return (
        <div className="generate-results-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Generated Results for Playlist: {playlistId}</h2>

            {loading ? (
                <p>Loading results...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <div className="results-content">
                    <ul className="tabs">
                        {categories.map((category, index) => (
                            <li
                                key={index}
                                className={`tab ${activeTab === index ? 'active' : ''}`}
                                onClick={() => handleTabClick(index)}
                            >
                                {category.category_name}
                            </li>
                        ))}
                    </ul>

                    {results[activeTab] && (
                        <div className="category-details">
                            <h3>{categories[activeTab].category_name}</h3>
                            <p>{categories[activeTab].description}</p>
                            <table className="songs-table">
                                <thead>
                                <tr>
                                    <th>Track Name</th>
                                    <th>Artists</th>
                                    <th>Album</th>
                                    <th>Release Date</th>
                                    <th>Reasoning</th>
                                </tr>
                                </thead>
                                <tbody>
                                {results[activeTab].map((song, index) => (
                                    <tr key={index}>
                                        <td>{song.track_name}</td>
                                        <td>{song.artists.join(', ')}</td>
                                        <td>{song.album}</td>
                                        <td>{song.release_date}</td>
                                        <td>{song.reasoning}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default GenerateResults;
