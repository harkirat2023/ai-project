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

def fetch_tracks(query, limit=5):
    if not sp:
        return [{'error': 'Spotify API not connected'}]

    if not query:
        return [{'error': 'No search term provided.'}]

    try:
        results = sp.search(q=query, type='track', limit=limit)

        if results['tracks']['items']:
            track_list = []
            for track in results['tracks']['items']:
                name = track['name']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                album = track['album']['name']
                url = track['external_urls']['spotify']
                preview_url = track['preview_url']
                duration_ms = track['duration_ms']
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000

                track_list.append({
                    'name': name,
                    'artists': artists,
                    'album': album,
                    'url': url,
                    'preview_url': preview_url or 'Not available',
                    'duration': f"{duration_min}:{duration_sec:02d}"
                })
            return track_list
        else:
            return [{'error': 'No tracks found for that search.'}]
    except Exception as e:
        return [{'error': str(e)}]

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    track_list = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            track_list = fetch_tracks(query)
    return render_template("index.html", track_list=track_list)

if __name__ == "__main__":
    mode = input("Enter 'web' to run Flask or 'cli' for console: ").strip().lower()

    if mode == "web":
        app.run(debug=True)
    elif mode == "cli":
        query = input("Enter song/mood/artist: ")
        tracks = fetch_tracks(query)
        for idx, track in enumerate(tracks, 1):
            if 'error' in track:
                print(f"Error: {track['error']}")
            else:
                print(f"\n{idx}. {track['name']} - {track['artists']}")
                print(f"   Album: {track['album']}")
                print(f"   Duration: {track['duration']} mins")
                print(f"   Spotify: {track['url']}")
                print(f"   Preview: {track['preview_url']}")
    else:
        print("Invalid mode. Use 'web' or 'cli'.")
