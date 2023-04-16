#!/usr/bin/env python3

from datetime import datetime
from multiprocessing import Pool
from spotipy.oauth2 import SpotifyClientCredentials
import json
import logging
import spotipy
import time


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

latestYear = 2023
earliestYear = 1899
query_limit = 50

total_result = dict() # id to artist

def main():
	start_time = datetime.now()
	logging.basicConfig(filename=start_time.strftime("%Y%m%d-%H%M%S")+".log", level=logging.INFO)
	logging.info("Start time: {time}".format(time=start_time))
	
	genres = spotify.recommendation_genre_seeds()['genres']

	# artistQueryForParam("year:0-" + str(earliestYear), total_result) # Query Stage C
	# fetchArtistsFromHipsterAlbums(total_result) # Query Stage B
	# fetchRelatedArtistsFromCurrentArtists(total_result) # Query Stage D
	fetchTop1000ArtistPerGenre(total_result, genres) # Query Stage A

	json_object = json.dumps(total_result)

	with open("results.json", "w") as outfile:
		outfile.write(json_object)
	end_time = datetime.now()
	logging.info("End time: {time}".format(time=end_time))
	logging.info("Total time spent: {total}".format(total=end_time - start_time))

def fetchRelatedArtistsFromCurrentArtists(total_result):
	logging.info("Fetching related artists from currently collected artists")
	for artist_id in set(total_result.keys()):
		relatedArtists = spotify.artist_related_artists(artist_id)['artists']
		logging.info("-- Found related artists: " + str(len(relatedArtists)))
		for artistJson in relatedArtists:
			artist = simplifyArtistJson(artistJson)
			total_result[artist['id']] = artist
		logging.info("Total result so far: " + str(len(total_result)))
		logging.info("Current time: {time}".format(time=datetime.now()))


def fetchArtistsFromHipsterAlbums(total_result):
	# Fetching artists from hipster albums every year from latestYear to 0
	query_param_fmt = "tag:hipster year:{year}"
	for year in range(latestYear, earliestYear, -1):
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
					artist = simplifyArtistJson(artistJson)
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
	# Fetching approximately top 1000 artists per year from latestYear to 1900
	query_param_fmt = "year:{year} genre:{genre}"
	for year in range(latestYear, earliestYear, -1):
		for genre in genres:
			artistQueryForParam(query_param_fmt.format(year=year, genre=genre))

def artistQueryForParamFn(limit, offset, query_param):
	result = dict()
	execute = True
	while execute:
		try:
			query_result = spotify.search(query_param, limit=limit, offset=offset, type='artist', market='US')
			for item in query_result['artists']['items']:
				artist = simplifyArtistJson(item)
				result[artist['id']] = artist
			execute = False
		except spotipy.SpotifyException:
			logging.info("Query failed at offset: " + str(offset))
			execute = False;
		except requests.exceptions.ReadTimeout:
			logging.info("Read time out encountered. Sleeping for 5.")
			time.sleep(5)
	return result

def artistQueryForParam(query_param):
	logging.info("Fetching for query parameters: " + query_param)
	p = Pool()
	offsetRange = list(range(0, 1000, query_limit))
	
	results = p.starmap(artistQueryForParamFn, zip([query_limit] * len(offsetRange), offsetRange, [query_param] * len(offsetRange)))
	for result in results:
		total_result.update(result)

	logging.info("Total result so far: " + str(len(total_result)))
	logging.info("Current time: {time}".format(time=datetime.now()))
	return total_result
	
	
def simplifyArtistJson(artistJson):
	result = dict()
	result['id'] = artistJson['id']
	result['name'] = artistJson['name']
	result['genres'] = artistJson['genres']
	result['popularity'] = artistJson['popularity']
	return result



if __name__ == '__main__':
    main()