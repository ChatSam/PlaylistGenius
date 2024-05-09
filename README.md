# PlaylistGenius

## Server

### Install
```
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create .env file with the following content:
```
CLIENT_ID=...
CLIENT_SECRET=...
REDIRECT_URI=http://localhost:3000
OPENAI_API_KEY=...
```

### Run
```
python app.py
```

## Client

### Install
```
cd client
npm ci
```

### Run
```
npm start
```

# How to use

1. Click on "Login to Spotify" in the center of the page and log in to your Spotify account.
2. Choose a playlist you want to classify. The playlist name and the number of songs will be displayed on the left and right sides.
3. Select the number of categories you want to classify, which should not exceed the number of songs in the playlist. Click on the "Generate" button to generate category names and descriptions based on your selection.
4. Wait for the AI classification to complete. You can track the progress of the classification from the progress bar at the top.
