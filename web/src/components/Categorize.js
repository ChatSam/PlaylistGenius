import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Categorize.css';

const Categorize = () => {
    const [numCategories, setNumCategories] = useState(5);
    const navigate = useNavigate();
    const { playlistId } = useParams();

    const handleGenerate = () => {
        navigate(`/categories/${playlistId}?numCategories=${numCategories}`);
    };

    return (
        <div className="categorize-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Categorize Playlist</h2>
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
