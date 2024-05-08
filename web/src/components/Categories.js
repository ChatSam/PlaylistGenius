import React from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import './Categories.css';

const Categories = () => {
    const navigate = useNavigate();
    const { playlistId } = useParams();
    const [searchParams] = useSearchParams();
    const numCategories = searchParams.get('numCategories');

    return (
        <div className="categories-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Categories for Playlist: {playlistId}</h2>
            <p>Number of Categories: {numCategories}</p>
            {/* Add further categorization UI logic here */}
        </div>
    );
};

export default Categories;
