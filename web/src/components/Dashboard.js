import React, { useEffect, useState } from 'react';

const Dashboard = () => {
    const [playlists, setPlaylists] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const accessToken = localStorage.getItem('spotify_access_token');
        if (!accessToken) {
            setError('No access token found');
            return;
        }

        const fetchPlaylists = async () => {
            try {
                const response = await fetch('https://api.spotify.com/v1/me/playlists?limit=50', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });

                if (!response.ok) {
                    console.log(response);
                    throw new Error('Failed to fetch playlists');
                }

                const data = await response.json();
                setPlaylists(data.items);

                // If you need to fetch more than 50 playlists, you can make additional
                // requests here using data.next as the URL for the next set of playlists.
            } catch (error) {
                console.error('Error:', error);
                setError(error.message);
            }
        };

        fetchPlaylists();
    }, []);

    if (error) {
        return <div>An error occurred: {error}</div>;
    }

    return (
        <div>
            <h1>Your Playlists</h1>
            {playlists.length > 0 ? (
                <ul>
                    {playlists.map(playlist => (
                        <li key={playlist.id}>
                            {playlist.images.length > 0 && (
                                <img src={playlist.images[0].url} alt={playlist.name} style={{ width: 60, height: 60, marginRight: 20 }} />
                            )}
                            {playlist.name}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No playlists found</p>
            )}
        </div>
    );
};

export default Dashboard;
