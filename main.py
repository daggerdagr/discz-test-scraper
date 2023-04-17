#!/usr/bin/env python3

from datetime import datetime
from multiprocessing import Pool
from spotipy.oauth2 import SpotifyClientCredentials
import json
import logging
import requests
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
	
	genres = spotipyFetchGenres()

	artistQueryForParam("year:0-" + str(earliestYear)) # Query Stage C
	fetchArtistsFromHipsterAlbums() # Query Stage B
	fetchRelatedArtistsFromCurrentArtists() # Query Stage D
	fetchTop1000ArtistPerGenre(genres) # Query Stage A

	json_object = json.dumps(total_result)

	with open("results.json", "w") as outfile:
		outfile.write(json_object)
	end_time = datetime.now()
	logging.info("End time: {time}".format(time=end_time))
	logging.info("Total time spent: {total}".format(total=end_time - start_time))

def spotipyFetchGenres():
	genres = []
	retry = True
	while retry:
		try:
			genres = spotify.recommendation_genre_seeds()['genres']
			retry = False
		except spotipy.SpotifyException:
			print("Genres fetch failed at offset: " + str(offset))
			retry = False
		except requests.exceptions.ReadTimeout:
			print("Read time out encountered. Sleeping for 5.")
			time.sleep(5)
			retry = True
	return genres

def spotipyFetchRelatedArtists(artist_id):
	relatedArtists = spotify.artist_related_artists(artist_id)['artists']
	logging.info("-- Found related artists: " + str(len(relatedArtists)))
	return relatedArtists

def fetchRelatedArtistsFromCurrentArtists():
	logging.info("Fetching related artists from currently collected artists")
	p = Pool()

	results = p.map(spotipyFetchRelatedArtists, set(total_result.keys()))

	for relatedArtists in results:
		for artistJson in relatedArtists:
			artist = simplifyArtistJson(artistJson)
			total_result[artist['id']] = artist

	logging.info("Total result so far: " + str(len(total_result)))
	logging.info("Current time: {time}".format(time=datetime.now()))


def fetchArtistsFromHipsterAlbums():
	# Fetching artists from hipster albums every year from latestYear to 0
	query_param_fmt = "tag:hipster year:{year}"
	for year in range(latestYear, earliestYear, -1):
		fetchArtistsFromAlbumQuery(query_param_fmt.format(year=year))

def spotipyFetchArtistsFromAlbums(query_param, limit, offset):
	artist_ids = set()
	retry = True
	while retry:
		try:
			query_result = spotify.search(query_param, limit=limit, offset=offset, type='album', market='US')
			
			for album in query_result['albums']['items']:
				if album:
					for incomplete_artist in album['artists']:
						artist_ids.add(incomplete_artist['id'])
			retry = False
		except spotipy.SpotifyException:
			print("Query failed at offset: " + str(offset))
			retry = False
		except requests.exceptions.ReadTimeout:
			print("Read time out encountered. Sleeping for 5.")
			time.sleep(5)
			retry = True
	return artist_ids

def completeArtists(segment):
	results = dict()
	artistsJson = spotify.artists(segment)['artists']
	retry = True
	while retry:
		try:
			artistJsons = spotify.artists(segment)['artists']

			for artistJson in artistJsons:
				artist = simplifyArtistJson(artistJson)
				results[artist['id']] = artist
			retry = False
		except spotipy.SpotifyException:
			print("Artist check failed at offset: " + str(offset))
			retry = False
		except requests.exceptions.ReadTimeout:
			print("Read time out encountered. Sleeping for 5.")
			time.sleep(5)
			retry = True
	
	return results

def divideToFiftyElemLists(s):
	result = []

	segmentStart = 0
	segmentEnd = 50

	while segmentStart < len(s):
		segment = s[segmentStart:segmentEnd]
		result.append(segment)
		segmentStart = segmentEnd
		segmentEnd += 50
	return result

def fetchArtistsFromAlbumQuery(query_param):
	logging.info("Fetching for album query parameters: " + query_param)

	p = Pool()

	offsetRange = list(range(0, 1000, query_limit))
	
	# Obtain incompleteArtists from hipster albums
	results = p.starmap(spotipyFetchArtistsFromAlbums, zip([query_param] * len(offsetRange), [query_limit] * len(offsetRange), offsetRange))
	allIncompleteArtists = set()
	for result in results:
		allIncompleteArtists.update(result)

	# complete artists using an artist query to Spotify	
	artistsTo50s = divideToFiftyElemLists(list(allIncompleteArtists))
	completedArtistsSegments = p.map(completeArtists, artistsTo50s)

	for segment in completedArtistsSegments:
		total_result.update(segment)

	logging.info("Total result so far: " + str(len(total_result)))
	logging.info("Current time: {time}".format(time=datetime.now()))
	return total_result

def fetchTop1000ArtistPerGenre(genres):
	# Fetching approximately top 1000 artists per year from latestYear to 1900
	query_param_fmt = "year:{year} genre:{genre}"
	for year in range(latestYear, earliestYear, -1):
		for genre in genres:
			artistQueryForParam(query_param_fmt.format(year=year, genre=genre))

def spotipyArtistQueryForParamFn(limit, offset, query_param):
	result = dict()
	retry = True
	while retry:
		try:
			query_result = spotify.search(query_param, limit=limit, offset=offset, type='artist', market='US')
			for item in query_result['artists']['items']:
				artist = simplifyArtistJson(item)
				result[artist['id']] = artist
			retry = False
		except spotipy.SpotifyException:
			print("Query failed at offset: " + str(offset))
			retry = False
		except requests.exceptions.ReadTimeout:
			print("Read time out encountered. Sleeping for 5.")
			time.sleep(5)
			retry = True
	return result

def artistQueryForParam(query_param):
	logging.info("Fetching for query parameters: " + query_param)
	p = Pool()
	offsetRange = list(range(0, 1000, query_limit))
	
	results = p.starmap(spotipyArtistQueryForParamFn, zip([query_limit] * len(offsetRange), offsetRange, [query_param] * len(offsetRange)))
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