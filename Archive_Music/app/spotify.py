import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session

SPOTIPY_CLIENT_ID = "fad179f5f27c437ca9dfc70e7eb5e62c"
SPOTIPY_CLIENT_SECRET = "6b051d09374b4573b73df9d848150547"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:4000/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-top-read playlist-modify-public"))

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read user-top-read playlist-modify-public")
