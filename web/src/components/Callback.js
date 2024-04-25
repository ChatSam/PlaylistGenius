import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate instead of useHistory

const Callback = () => {
    const navigate = useNavigate(); // useNavigate hook for navigation

    useEffect(() => {
        const code = new URLSearchParams(window.location.search).get('code');
        if (code) {
            localStorage.setItem('spotify_auth_code', code);
            // Redirect user to another page after successful login, for example
            navigate('/dashboard'); // Use navigate for redirection
        }
    }, [navigate]);

    return (
        <div>Loading...</div>
    );
};

export default Callback;
