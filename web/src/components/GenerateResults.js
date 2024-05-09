import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useParams, useSearchParams, useLocation } from 'react-router-dom';
import './GenerateResults.css';

const sanitizeCategoryName = (name) => name.replace(/\*/g, '');

const GenerateResults = () => {
    const navigate = useNavigate();
    const { playlistId } = useParams();
    const [searchParams] = useSearchParams();
    const numCategories = searchParams.get('numCategories') || 5;
    const { state } = useLocation();
    const { categories: initialCategories } = state || {};
    const [results, setResults] = useState({});
    const [categories, setCategories] = useState(initialCategories || []);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState(0);
    const fetchOnce = useRef(false);

    useEffect(() => {
        if (fetchOnce.current || !categories.length) {
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

                if (!response.ok) {
                    const errorData = await response.json();
                    setError(errorData.error || 'Unable to generate results');
                    setLoading(false);
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                // Initialize the results object with empty lists for each category
                const dynamicResults = {};
                categories.forEach((category) => {
                    const sanitizedName = sanitizeCategoryName(category.category_name);
                    dynamicResults[sanitizedName] = [];
                });

                const updateResults = () => {
                    setResults({ ...dynamicResults });
                };

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });

                    let jsonStart = buffer.indexOf('{');
                    let jsonEnd = buffer.indexOf('}');

                    while (jsonStart !== -1 && jsonEnd !== -1) {
                        const jsonString = buffer.substring(jsonStart, jsonEnd + 1);
                        buffer = buffer.slice(jsonEnd + 1);

                        try {
                            const track = JSON.parse(jsonString);
                            const sanitizedCategoryName = sanitizeCategoryName(track.category_name);

                            if (dynamicResults[sanitizedCategoryName]) {
                                dynamicResults[sanitizedCategoryName].push(track);
                            } else {
                                console.error(`Unknown category: ${sanitizedCategoryName}`);
                            }
                        } catch (e) {
                            console.error('Parsing error:', e);
                        }

                        jsonStart = buffer.indexOf('{');
                        jsonEnd = buffer.indexOf('}');
                    }

                    // Update results state after every chunk
                    updateResults();
                }

                setLoading(false);
            } catch (error) {
                setError('An error occurred while fetching results');
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
                        {categories.map((category, index) => {
                            const sanitizedCategoryName = sanitizeCategoryName(category.category_name);
                            return (
                                <li
                                    key={index}
                                    className={`tab ${activeTab === index ? 'active' : ''}`}
                                    onClick={() => handleTabClick(index)}
                                >
                                    {sanitizedCategoryName}
                                </li>
                            );
                        })}
                    </ul>

                    {categories[activeTab] && (
                        <div className="category-details">
                            <h3>{sanitizeCategoryName(categories[activeTab].category_name)}</h3>
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
                                {results[sanitizeCategoryName(categories[activeTab].category_name)]?.map((song, index) => (
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
