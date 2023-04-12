#!/usr/bin/env python3

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import time


'''
export SPOTIPY_CLIENT_ID=d44c1b8a65604265a5abc858294aa830
export SPOTIPY_CLIENT_SECRET=09ff84f3e5774851858751621647985e
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback
'''
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def main():

	total_result = dict() # id to artist
	
	for year in range(2023, 1900, -1):
		queryForYear(year, total_result)
		# time.sleep(60)

		print("Total result so far: " + str(len(total_result)))

	json_object = json.dumps(total_result)

	with open("results.json", "w") as outfile:
		outfile.write(json_object)

def queryForYear(year, total_result):
	print("Fetching for year: " + str(year))
	offset = 0
	limit = 50
	valid = True
	while valid and offset < 1000:
		try:
			query_result = spotify.search("year:"+str(year), limit=limit, offset=offset, type='artist', market='US')
			
			for item in query_result['artists']['items']:
				artist = simplifyArtistItem(item)
				total_result[artist['id']] = artist

			offset += limit
		except spotipy.SpotifyException:
			print("Query maximum offset hit at: " + str(offset))
			valid = False

	return total_result
	
	
def simplifyArtistItem(item):
	result = dict()
	result['id'] = item['id']
	result['name'] = item['name']
	result['genres'] = item['genres']
	result['popularity'] = item['popularity']
	return result



if __name__ == '__main__':
    main()