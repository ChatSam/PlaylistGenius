import React, { useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './Categorize.css';

const Categorize = () => {
    const [numCategories, setNumCategories] = useState(5);
    const navigate = useNavigate();
    const { playlistId } = useParams();
    const { state } = useLocation();
    const { playlistName, totalTracks } = state || {};

    const handleGenerate = () => {
        navigate(`/categories/${playlistId}?numCategories=${numCategories}`, {
            state: {
                playlistName,
                totalTracks
            }
        });
    };

    return (
        <div className="categorize-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Categorize Playlist: "{playlistName}"</h2>
            <p>Number of Tracks: {totalTracks}</p>
            <label>
                Number of Categories:
                <select value={numCategories} onChange={(e) => setNumCategories(Number(e.target.value))}>
                    {[...Array(9).keys()].map(i => (
                        <option key={i + 2} value={i + 2}>{i + 2}</option>
                    ))}
                </select>
            </label>
            <button className="button" onClick={handleGenerate}>Generate</button>
        </div>
    );
};

export default Categorize;
