# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API credentials
CLIENT_ID = "f3316e651384400397b8cbae40e56d0e"
CLIENT_SECRET = "476bee27586a40c18e64f25e70f9c891"
REDIRECT_URI = "http://localhost:5000/callback"

# Initialize Spotify client for non-user-specific features
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))
    print("Spotify API Connected ✅")
except Exception as e:
    print("Spotify API Error:", e)
    sp = None

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

# Route for artist-based search
@app.route('/artist', methods=['GET', 'POST'])
def artist_search():
    if request.method == 'POST':
        artist_name = request.form.get('artist_name')
        if artist_name and sp:
            try:
                result = sp.search(q=artist_name, type='artist', limit=1)
                if not result['artists']['items']:
                    return render_template('artist.html', error=f"Artist '{artist_name}' not found.")
                
                artist = result['artists']['items'][0]
                artist_id = artist['id']
                albums = sp.artist_albums(artist_id, album_type='album', limit=50)
                album_ids = list({album['id'] for album in albums['items']})
                
                all_tracks = set()
                for album_id in album_ids:
                    tracks = sp.album_tracks(album_id)
                    for track in tracks['items']:
                        all_tracks.add(track['name'])
                
                return render_template('artist.html', 
                                     artist_name=artist['name'], 
                                     tracks=sorted(all_tracks),
                                     count=len(all_tracks))
            except Exception as e:
                return render_template('artist.html', error=str(e))
    return render_template('artist.html')

# Route for song-based search
@app.route('/song', methods=['GET', 'POST'])
def song_search():
    track_info = None
    if request.method == 'POST' and sp:
        song_name = request.form.get('song_name')
        if song_name:
            try:
                results = sp.search(q=song_name, type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    duration_ms = track['duration_ms']
                    duration_min = duration_ms // 60000
                    duration_sec = (duration_ms % 60000) // 1000
                    
                    track_info = {
                        'name': track['name'],
                        'artists': ", ".join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'url': track['external_urls']['spotify'],
                        'preview_url': track['preview_url'] or 'Not available',
                        'duration': f"{duration_min}:{duration_sec:02d} mins"
                    }
            except Exception as e:
                track_info = {'error': str(e)}
    return render_template('song.html', track_info=track_info)

# Route for mood-based search
@app.route('/mood', methods=['GET', 'POST'])
def mood_search():
    recommendations = []
    selected_mood = ""
    if request.method == 'POST' and sp:
        selected_mood = request.form.get('mood')
        if selected_mood:
            try:
                results = sp.search(q=selected_mood, type='track', limit=5)
                if results['tracks']['items']:
                    for track in results['tracks']['items']:
                        recommendations.append({
                            'name': track['name'],
                            'artists': ", ".join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'url': track['external_urls']['spotify'],
                            'preview': track['preview_url'] or "No preview available"
                        })
            except Exception as e:
                recommendations = [{'error': str(e)}]
    return render_template('mood.html', recommendations=recommendations, selected_mood=selected_mood)

# Route for NLP sentiment analysis
@app.route('/nlp', methods=['GET', 'POST'])
def nlp_analysis():
    mood = None
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            sentiment_score = analyzer.polarity_scores(text)
            if sentiment_score['compound'] > 0.2:
                mood = "happy"
            elif sentiment_score['compound'] < -0.2:
                mood = "sad"
            else:
                mood = "neutral"
    return render_template('nlp.html', mood=mood)

# Route for Spotify history
@app.route('/history')
def history():
    if not session.get('token_info'):
        return redirect(url_for('login'))
    return redirect(url_for('recommendations'))

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           redirect_uri=REDIRECT_URI,
                           scope="user-library-read user-read-recently-played")
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           redirect_uri=REDIRECT_URI,
                           scope="user-library-read user-read-recently-played")
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('recommendations'))

@app.route('/recommendations')
def recommendations():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))
    
    sp_user = spotipy.Spotify(auth=token_info['access_token'])
    results = sp_user.current_user_recently_played(limit=5)
    
    if not results['items']:
        return render_template('history.html', tracks=[], message="No recent listening history found.")
    
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append({
            'name': track['name'],
            'artists': ", ".join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'url': track['external_urls']['spotify']
        })
    
    return render_template('history.html', tracks=tracks)

if __name__ == '__main__':
    app.run(debug=True)