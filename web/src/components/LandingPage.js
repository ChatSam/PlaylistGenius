// src/components/LandingPage.js
import React, { useEffect, useState } from 'react';
import Dashboard from "./Dashboard";

const clientId = '61a763c599484a729f9b5a31c1057143'; // Replace with your Spotify app's client ID
const redirectUri = 'http://localhost:3000'; // Replace with your app's redirect URI
const scope = 'playlist-read-private playlist-modify-private playlist-modify-public';
const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}`;
const backendUrl = 'http://127.0.0.1:5000'; // Replace with your backend server's URL
const LandingPage = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        // This effect runs once on component mount to check for an existing login state.
        const token = localStorage.getItem('spotify_access_token');
        if (token) {
            setIsLoggedIn(true);
        } else {
            // Extract 'code' from URL parameters if present
            const urlParams = new URLSearchParams(window.location.search);
            const authCode = urlParams.get('code');
            if (authCode) {
                fetch(`${backendUrl}/exchange-code?code=${authCode}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.access_token) {
                            localStorage.setItem('spotify_access_token', data.access_token);
                            setIsLoggedIn(true);

                            // Clean up URL by removing the code query parameter
                            window.history.pushState({}, document.title, window.location.pathname);
                        }
                    })
                    .catch(error => console.error('Error exchanging auth code:', error));
            }
        }
    }, []);

    if (isLoggedIn) {
        return <Dashboard />;
    }

    return (
        <div>
            <h1>Playlist Genius</h1>
            <p>Find the perfect playlist for any mood or occasion.</p>
            <a href={authUrl}>
                <button>Login to Spotify</button>
            </a>
        </div>
    );
};

export default LandingPage;