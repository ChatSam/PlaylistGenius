import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
    const [playlists, setPlaylists] = useState([]);
    const [error, setError] = useState(null);
    const [nextUrl, setNextUrl] = useState('https://api.spotify.com/v1/me/playlists?limit=50');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const fetchPlaylists = useCallback(async () => {
        const accessToken = localStorage.getItem('spotify_access_token');
        if (!accessToken) {
            setError('No access token found');
            return;
        }

        if (!nextUrl || isLoading) return; // Prevent fetching if no next page or currently loading

        setIsLoading(true);

        try {
            const response = await fetch(nextUrl, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch playlists');
            }

            const data = await response.json();
            setPlaylists(prevPlaylists => [...prevPlaylists, ...data.items]);
            setNextUrl(data.next); // Update next page URL or null if none

        } catch (error) {
            console.error('Error:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    }, [nextUrl, isLoading]);

    // Initial Fetch
    useEffect(() => {
        fetchPlaylists();
    }, [fetchPlaylists]);

    // Infinite Scroll Listener
    useEffect(() => {
        const handleScroll = () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200 && !isLoading) {
                fetchPlaylists();
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [fetchPlaylists, isLoading]);

    const handlePlaylistClick = (playlist) => {
        navigate(`/categorize/${playlist.id}`, {
            state: {
                playlistName: playlist.name,
                totalTracks: playlist.tracks.total
            }
        });
    };

    if (error) {
        return <div>An error occurred: {error}</div>;
    }

    return (
        <div className="dashboard-container">
            <h1>Your Playlists</h1>
            {playlists.length > 0 ? (
                <table className="playlist-table">
                    <thead>
                    <tr>
                        <th>COVER</th>
                        <th>NAME</th>
                        <th>TRACK COUNT</th>
                        <th>OWNER</th>
                    </tr>
                    </thead>
                    <tbody>
                    {playlists.map(playlist => (
                        <tr
                            key={playlist.id}
                            onClick={() => handlePlaylistClick(playlist)}
                            className="clickable-row"
                        >
                            <td>
                                {playlist.images && playlist.images.length > 0 ? (
                                    <img
                                        src={playlist.images[0].url}
                                        alt={playlist.name}
                                        className="playlist-cover"
                                    />
                                ) : (
                                    <div className="no-cover">No Image</div>
                                )}
                            </td>
                            <td>{playlist.name}</td>
                            <td>{playlist.tracks.total}</td>
                            <td>{playlist.owner.display_name || playlist.owner.id}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            ) : (
                <p>No playlists found</p>
            )}
            {isLoading && <p>Loading more playlists...</p>}
        </div>
    );
};

export default Dashboard;
