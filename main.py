#!/usr/bin/env python3

from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import json
import logging
import spotipy
import time


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def main():
	start_time = datetime.now()
	logging.basicConfig(filename=start_time.strftime("%Y%m%d-%H%M%S")+".log", level=logging.INFO)
	logging.info("Start time: {time}".format(time=start_time))
	
	genres = spotify.recommendation_genre_seeds()['genres'][:1]

	total_result = dict() # id to artist

	# artistQueryForParam("year:0-1889", total_result) # Query Stage C
	fetchArtistsFromHipsterAlbums(total_result) # Query Stage B
	# fetchTop1000ArtistPerGenre(total_result, genres) # Query Stage A

	json_object = json.dumps(total_result)

	with open("results.json", "w") as outfile:
		outfile.write(json_object)
	end_time = datetime.now()
	logging.info("End time: {time}".format(time=end_time))
	logging.info("Total time spent: {total}".format(total=end_time - start_time))


def fetchArtistsFromHipsterAlbums(total_result):
	# Fetching artists from hipster albums every year from 2023 to 0
	query_param_fmt = "tag:hipster year:{year}"
	for year in range(2023, 1899, -1):		
		fetchArtistsFromAlbumQuery(query_param_fmt.format(year=year), total_result)

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

			artistCheckSegmentStart = 0
			artistCheckSegmentEnd = 50

			while artistCheckSegmentStart < len(artist_ids):
				artistCheckSegment = artist_ids[artistCheckSegmentStart:artistCheckSegmentEnd]
				artistsJson = spotify.artists(artistCheckSegment)['artists']
				for artistJson in artistsJson:
					artist = simplifyArtistItem(artistJson)
					total_result[artist['id']] = artist
				artistCheckSegmentStart = artistCheckSegmentEnd
				artistCheckSegmentEnd += 50

			offset += limit
		except spotipy.SpotifyException:
			valid = False
	logging.info("Album query offset maximum hit at: " + str(offset))
	logging.info("Total result so far: " + str(len(total_result)))
	logging.info("Current time: {time}".format(time=datetime.now()))
	return total_result

def fetchTop1000ArtistPerGenre(total_result, genres):
	# Fetching approximately top 1000 artists per year from 2023 to 1900
	query_param_fmt = "year:{year} genre:{genre}"
	for year in range(2023, 1889, -1):
		for genre in genres:
			artistQueryForParam(query_param_fmt.format(year=year, genre=genre), total_result)
		# time.sleep(60)

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