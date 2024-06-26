# PlaylistGenius
**Description:** 

Spotify Playlist Curation Tool that transforms how users experience their music libraries. 
Traditional playlist organization methods based on simple genres or artist names don't always capture the nuanced vibes listeners seek.
The tool analyzes users' existing playlists, generates dynamic categories based on song metadata and genres, and curates new, personalized playlists tailored to diverse listening preferences by leveraging LLM capabilities.


## Installation Instructions

### 1. **Prerequisites**
    - Python version 3.10+
    - NodeJs version 22

### 2. **Clone this repository**

### 3. **Installing the dependencies**

Install for Macbooks 
```
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ..
cd web
npm ci

```
Install for Windows 

```
cd server
python -m venv venv
Set-ExecutionPolicy Unrestricted -Scope Process (This would allow running virtualenv in the current PowerShell session.)
venv\Scripts\activate
pip install -r requirements.txt

cd ..
cd web
npm ci
```
### 4. **Configuration**

Create .env file with the following content:
```
CLIENT_ID=...
CLIENT_SECRET=...
REDIRECT_URI=http://localhost:3000
OPENAI_API_KEY=...
```

### 5. **Execution**

Open two terminals or powershells

Terminal 1:
```
python app.py
```
Terminal 2:
```
npm start
```


### 6. **Unit Tests**

To run the unit tests 
```
# navigate to the test folder 
cd tests/unit/

# run the test 
pytest test_unit.py
```


## How to use

1. Click on "Login to Spotify" in the center of the page and log in to your Spotify account.
2. Choose a playlist you want to classify. The playlist name and the number of songs will be displayed on the left and right sides.
3. Select the number of categories you want to classify, which should not exceed the number of songs in the playlist. Click on the "Generate" button to generate category names and descriptions based on your selection.
4. Wait for the AI classification to complete. You can track the progress of the classification from the progress bar at the top.

### Video showcasing the features 
[demo_vid.webm](https://github.com/ChatSam/PlaylistGenius/assets/6478266/7bda5990-8575-4ea3-8399-92d5fbbb1b30)

<p align="center">
  <a href="https://drive.google.com/file/d/1BGU3JGHngOQEYC0OuHm_bt39WNVBJJpK/view?usp=sharing">Video Link to showcase the features</a>
</p>
