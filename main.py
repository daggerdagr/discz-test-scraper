#!/usr/bin/env python3

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


'''
export SPOTIPY_CLIENT_ID=d44c1b8a65604265a5abc858294aa830
export SPOTIPY_CLIENT_SECRET=09ff84f3e5774851858751621647985e
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback
'''

def main():
	birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
	spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

	results = spotify.artist_albums(birdy_uri, album_type='album')
	albums = results['items']
	while results['next']:
	    results = spotify.next(results)
	    albums.extend(results['items'])

	for album in albums:
	    print(album['name'])

if __name__ == '__main__':
    main()