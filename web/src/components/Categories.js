import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import './Categories.css';

const Categories = () => {
    const navigate = useNavigate();
    const { playlistId } = useParams();
    const [searchParams] = useSearchParams();
    const numCategories = searchParams.get('numCategories') || 5;
    const [categories, setCategories] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('spotify_access_token');

        if (!token) {
            setError('No Spotify access token found');
            setLoading(false);
            return;
        }

        const fetchCategories = async () => {
            try {
                const response = await fetch(`http://localhost:5000/categories?token=${token}&playlist_id=${playlistId}&num_categories=${numCategories}`);
                const data = await response.json();
                if (response.ok) {
                    setCategories(data);
                } else {
                    setError(data.error || 'Unable to fetch categories');
                }
            } catch (error) {
                setError('An error occurred while fetching categories');
            } finally {
                setLoading(false);
            }
        };

        fetchCategories();
    }, [playlistId, numCategories]);

    const handleGenerate = () => {
        navigate(`/generate-results/${playlistId}?numCategories=${numCategories}`, {
            state: { categories }
        });
    };

    return (
        <div className="categories-container">
            <button className="button" onClick={() => navigate(-1)}>Back</button>
            <h2>Categories for Playlist: {playlistId}</h2>
            <p>Number of Categories: {numCategories}</p>

            {loading ? (
                <p>Loading categories...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <div className="categories-list">
                    {categories.map((category) => (
                        <div key={category.category_number} className="category">
                            <h3>{category.category_name}</h3>
                            <p>{category.description}</p>
                        </div>
                    ))}
                </div>
            )}

            <button className="button" onClick={handleGenerate}>Generate</button>
        </div>
    );
};

export default Categories;
