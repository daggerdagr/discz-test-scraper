#!/usr/bin/env python3

from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import json
import logging
import spotipy
import time


'''
export SPOTIPY_CLIENT_ID=d44c1b8a65604265a5abc858294aa830
export SPOTIPY_CLIENT_SECRET=09ff84f3e5774851858751621647985e
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback
'''
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def main():
	start_time = datetime.now()
	logging.basicConfig(filename=start_time.strftime("%Y%m%d-%H%M%S")+".log", level=logging.INFO)
	logging.info("Start time: {time}".format(time=start_time))
	
	genres = spotify.recommendation_genre_seeds()['genres'][:1]

	total_result = dict() # id to artist

	fetchArtistsFromHipsterAlbums(total_result)
	# fetchTop1000ArtistPerGenre(total_result, genres)

	json_object = json.dumps(total_result)

	with open("results.json", "w") as outfile:
		outfile.write(json_object)
	end_time = datetime.now()
	logging.info("End time: {time}".format(time=end_time))
	logging.info("Total time spent: {total}".format(total=end_time - start_time))


def fetchArtistsFromHipsterAlbums(total_result):
	# Fetching artists from hipster albums every year from 2023 to 0
	query_param_fmt = "tag:hipster year:{year}"
	for year in range(2023, 1900, -1):		
		fetchArtistsFromAlbumQuery(query_param_fmt.format(year=year), total_result)
	fetchArtistsFromAlbumQuery("year:0-1900", total_result)

def fetchArtistsFromAlbumQuery(query_param, total_result):
	logging.info("Fetching for album query parameters: " + query_param)
	offset = 0
	limit = 50
	valid = True
	while valid and offset < 1000:
		try:
			query_result = spotify.search(query_param, limit=limit, offset=offset, type='album', market='US')
			
			artist_ids = []
			for album in query_result['albums']['items']:
				if album:
					for incomplete_artist in album['artists']:
						artist_ids.append(incomplete_artist['id'])

			querySegmentStart = 0
			querySegmentEnd = 50

			while querySegmentStart < len(artist_ids):
				querySegment = artist_ids[querySegmentStart:querySegmentEnd]
				artistsJson = spotify.artists(querySegment)['artists']
				for artistJson in artistsJson:
					artist = simplifyArtistItem(artistJson)
					total_result[artist['id']] = artist
				querySegmentStart = querySegmentEnd
				querySegmentEnd += 50

			offset += limit
		except spotipy.SpotifyException:
			valid = False
	logging.info("Album query offset maximum hit at: " + str(offset))
	logging.info("Total result so far: " + str(len(total_result)))
	return total_result

def fetchTop1000ArtistPerGenre(total_result, genres):
	# Fetching approximately top 1000 artists per year from 2023 to 0
	query_param_fmt = "year:{year} genre:{genre}"
	for year in range(2023, 1889, -1):
		for genre in genres:
			artistQueryForParam(query_param_fmt.format(year=year, genre=genre), total_result)
		# time.sleep(60)
	artistQueryForParam("year:0-1889", total_result)

def artistQueryForParam(query_param, total_result):
	logging.info("Fetching for query parameters: " + query_param)
	offset = 0
	limit = 50
	valid = True
	while valid and offset < 1000:
		try:
			query_result = spotify.search(query_param, limit=limit, offset=offset, type='artist', market='US')
			
			for item in query_result['artists']['items']:
				artist = simplifyArtistItem(item)
				total_result[artist['id']] = artist

			offset += limit
		except spotipy.SpotifyException:
			logging.info("Query maximum offset hit at: " + str(offset))
			valid = False
	logging.info("Total result so far: " + str(len(total_result)))
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