import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request


client_id = "f3316e651384400397b8cbae40e56d0e"
client_secret = "476bee27586a40c18e64f25e70f9c891"

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    print("Spotify API Connected ✅")
except Exception as e:
    print("Spotify API Error:", e)
    sp = None  


def fetch_by_name(song_name):
    if not sp:
        return {'error': 'Spotify API not connected'}
    if not song_name:
        return {'error': 'No song name provided'}

    try:
        results = sp.search(q=song_name, type='track', limit=1)

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            name = track['name']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            album = track['album']['name']
            url = track['external_urls']['spotify']
            preview_url = track['preview_url']
            duration_ms = track['duration_ms']
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000

            return {
                'name': name,
                'artists': artists,
                'album': album,
                'url': url,
                'preview_url': preview_url or 'Not available',
                'duration': f"{duration_min}:{duration_sec:02d} mins"
            }
        else:
            return {'error': 'No track found with that name.'}
    except Exception as e:
        return {'error': str(e)}


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    track_info = None
    if request.method == "POST":
        song_name = request.form.get("song_name")
        if song_name:
            track_info = fetch_by_name(song_name)
    return render_template("index.html", track_info=track_info)


if __name__ == "__main__":
    mode = input("Enter 'web' to run Flask or 'cli' for console: ").strip().lower()

    if mode == "web":
        app.run(debug=True)  
    elif mode == "cli":
        song_name = input("Enter song name: ")
        track_info = fetch_by_name(song_name)

        if 'error' in track_info:
            print("Error:", track_info['error'])
        else:
            print(f"\nTrack: {track_info['name']}")
            print(f"Artist(s): {track_info['artists']}")
            print(f"Album: {track_info['album']}")
            print(f"Duration: {track_info['duration']}")
            print(f"Spotify URL: {track_info['url']}")
            print(f"Preview URL: {track_info['preview_url']}")
    else:
        print("Invalid input. Please enter 'web' or 'cli'.")
