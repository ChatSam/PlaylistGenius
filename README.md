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