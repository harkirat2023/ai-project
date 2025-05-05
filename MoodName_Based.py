
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request

app = Flask(__name__)

client_id = "f3316e651384400397b8cbae40e56d0e"
client_secret = "476bee27586a40c18e64f25e70f9c891"


try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    print("Spotify API Connected Successfully ✅\n")
except Exception as e:
    print("Spotify API Authentication Error:", e)
    sp = None  


def get_recommendations(mood):
    if not sp:
        return [{'error': 'Spotify client not initialized'}]

    try:
        results = sp.search(q=mood, type='track', limit=5)

        if results['tracks']['items']:
            recommendations = []
            for track in results['tracks']['items']:
                name = track['name']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                album = track['album']['name']
                url = track['external_urls']['spotify']
                preview = track['preview_url'] or "No preview available"

                recommendations.append({
                    'name': name,
                    'artists': artists,
                    'album': album,
                    'url': url,
                    'preview': preview
                })
            return recommendations
        else:
            return [{'error': f"No songs found for mood '{mood}' ❌"}]
    except Exception as e:
        return [{'error': str(e)}]


@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    selected_mood = ""
    if request.method == "POST":
        selected_mood = request.form.get("mood")
        if selected_mood:
            recommendations = get_recommendations(selected_mood)
    return render_template("index.html", recommendations=recommendations, selected_mood=selected_mood)



if __name__ == "__main__":
    mode = input("Enter 'web' to run Flask app or 'cli' for console mode: ").strip().lower()

    if mode == "web":
        app.run(debug=True)

    elif mode == "cli":
        mood = input("Enter your mood (e.g., happy, sad, chill, romantic, energetic): ").strip()
        songs = get_recommendations(mood)
        print(f"\nSongs matching mood '{mood}':\n")
        for idx, track in enumerate(songs, 1):
            if 'error' in track:
                print(track['error'])
            else:
                print(f"{idx}. {track['name']} - {track['artists']}")
                print(f"   Album: {track['album']}")
                print(f"   Spotify URL: {track['url']}")
                print(f"   Preview: {track['preview']}\n")
    else:
        print("Invalid mode selected. Please enter 'web' or 'cli'.")
