import json
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

USER_ID = ""
SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
OAUTH_AUTHORIZE_URL = ""
SEARCH_URL = ""
PLAYLIST_CREATE_URL = f""

try:
    travel_date = input("What year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{travel_date}/")
    response.raise_for_status()
except requests.exceptions.HTTPError:
    print("Please remember about proper format.")
    travel_date = input("What year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{travel_date}/")

top_100_web = response.text

soup = BeautifulSoup(top_100_web, 'html.parser')
titles = [' '.join(song_titles.get_text().split()) for song_titles in soup.select('li.o-chart-results-list__item > h3')]
artists = [' '.join(song_artists.get_text().split()) for song_artists in soup.select('li.o-chart-results-list__item > span.c-label')]

new_artists = []
for item in artists:
    if item.isdigit() or item == '-' or item == 'NEW':
        del item
    else:
        re.sub('\(.*?\)', "", item)
        new_artists.append(item)

re_titles = [re.sub('\(.*?\)', "", item) for item in titles]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="playlist-modify-public",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
        ))

user_id = sp.current_user()

values = json.load(open("token.txt"))

uri_list = []
for i in range(len(titles)):
    params = {
                "q": f"{re_titles[i]} {new_artists[i]}",
                "type": "track",
                "access_token": f"{values['access_token']}",
                "limit": 1,
                "market": "US"
                }

    search = requests.get(url=SEARCH_URL, params=params)
    search.raise_for_status()
    data = search.json()
    try:
        uri_list.append(data['tracks']['items'][0]['uri'])
    except IndexError:
        print(f"Sorry we cannot find {new_artists[i]} - {titles[i]}, this song was omitted. Process will continue")
        pass
    continue

playlist_params = {
    "name": f"{travel_date} TOP HITS",
    "public": True,
}

header = {
    'Authorization': f"Bearer {values['access_token']}"
}

playlist = requests.post(url=PLAYLIST_CREATE_URL, headers=header, json=playlist_params)
playlist.raise_for_status()
playlist_id = playlist.json()['id']

TRACK_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

tracks_params = {
    "uris": uri_list
}

track_adding = requests.post(url=TRACK_URL, headers=header, json=tracks_params)
track_adding.raise_for_status()


