
    # ***************************ALL SONGS**********************************
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

client_id = "f3316e651384400397b8cbae40e56d0e"  
client_secret = "476bee27586a40c18e64f25e70f9c891"  

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    print("API Successfully Connected \n")

    artist_name = input("Enter the artist name: ").strip()

    
    result = sp.search(q=artist_name, type='artist', limit=1)
    if not result['artists']['items']:
        print(f"Artist '{artist_name}' not found.")
    else:
        artist = result['artists']['items'][0]
        artist_id = artist['id']
        print(f"\nFound Artist: {artist['name']}")
        print("Fetching albums and tracks...\n")

        
        albums = sp.artist_albums(artist_id, album_type='album', limit=50)
        album_ids = list({album['id'] for album in albums['items']})  

        all_tracks = set() 

        for album_id in album_ids:
            tracks = sp.album_tracks(album_id)
            for track in tracks['items']:
                all_tracks.add(track['name'])  

        if all_tracks:
            print(f"{len(all_tracks)} songs found for '{artist_name}':\n")
            for i, track in enumerate(sorted(all_tracks), 1):
                print(f"{i}. {track}")
        else:
            print("No songs found in the artist's albums.")

except Exception as e:
    print("Error:", e)
