# Discz Artist Scraper

## Run Instructions

```
# Needed to authorize Spotipy python library
export SPOTIPY_CLIENT_ID=2167953908b245d59213726d4d311d6e
export SPOTIPY_CLIENT_SECRET=3f0a5cbbc123469fa0f55be9ef61df2e
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback

pip install spotipy --upgrade
# or install spotipy in general

rm .cache && python3 main.py
# have to clear cache due to Spotipy bug re: querying artists' related artist
```

## Total amount of artists projected to be fetched

```
989 (C) + 99,138 (B) + 346,983 (D) + 1,627,290 (A) = 2,074,410 artists
```

## Speed Optimizations

Speed optimizations were done by utilizing the `multiprocessing` python library:
- queries that has an offset parameter (e.g. the artists query and the albums query utilized in Query Stages B and A) are executed in parallel along the whole range of possible offset.
```
query, parallelized:
	-> query(offset=0)
	-> query(offset=50)
	-> query(offset=100)
	...
	-> query(offset=950)
	-> query(offset=1000)
```
- queries in stage D (fetch artists related to currently collected artists) are parallelized for each artist

## Queries Breakdown

### Query Stage C - Query for artists for the year range 0-1899
Querying for artists in the year range 0-1899 returns a finite, <1000 result. So we can execute this simple query on its own, separate from the other query stages.

#### Actual result: 989 artists

### Query Stage B - Collect artists from hipster albums from 2023 to 1900.
Query "hipster" albums for every year from 2023 to 1900. Then, aggregate all artists from these albums.
- There are settings in Spotify's search API that can allow us to look for albums with less than 10% popularity, the parameter `tag:hipster`.
- Utilizing this query in addition to Query A does mean that we essentially have results that consist of the most popular artists and least popular artists per year, with artists that have middle popularity being missing.

#### Result projection: 99,138 artists

##### Script Logs
- We run this stage for partially and make some projections with the result:
```
INFO:root:Start time: 2023-04-16 16:57:24.423299
INFO:root:Fetching for album query parameters: tag:hipster year:2023
INFO:root:Total result so far: 733
...
INFO:root:Current time: 2023-04-16 16:59:50.166898
INFO:root:Fetching for album query parameters: tag:hipster year:1980
INFO:root:Total result so far: 34395
# Script interrupted here
```
- Calculations:
	- 43 years covered in this run.
	- 34653 artists discovered in this run.
	- Every query discovers 34653 / 43 ~= 806 artists
	- Total number of queries if we execute a query for every year from 2023 to 1900: (2023 - 1900) = 123 queries
	- Projected total of artists to be discovered: 123 queries * 806 artists = **99,138 artists**

### Query Stage D - Query for related artists for all unpopular artists found so far
- This is done after only stage B and C and not A because it's more likely we'll discover more unique artists from less popular artists - popular artists are more likely to be related to other popular artists. For example, searching for Taylor Swift lead to related artists such as Demi Lovato and Selena Gomez, all of which can be considered to be popular artists.
#### Result projection: 693,966 artists

##### Script Logs
- We run this stage using only the results of Stage C 0-1899 and make some projections with the result:
```
INFO:root:Start time: 2023-04-16 13:04:25.011552
INFO:root:Fetching for query parameters: year:0-1899
INFO:root:Total result so far: 991
INFO:root:Fetching related artists from currently collected artists
...
INFO:root:-- Found related artists: 20
INFO:root:Total result so far: 7515
INFO:root:Current time: 2023-04-16 13:06:36.598839
INFO:root:End time: 2023-04-16 13:06:36.633515
INFO:root:Total time spent: 0:02:11.621963
```
- Calculations:
	- 991 artists from 0-1899
	- 7515 artists obtained at the end
	- 7515 artists / 991 artist ~= 8 multiplicative factor
	- 99138 * (8 - 1) * 0.50 (to minimize projection) = 346,983 additional artists

### Query Stage A - Query for top ~1000 artist for every genre, for every year from 2023 to 1900

Fetch genre seeds from Spotify. Query for the top ~1000 artist for every genre, for every year from 2023 to 1900
- (Not always 1000 - the API sometimes quits after ~700 offset, even though API limit is 1000)
#### Result projection: 1,627,290 artists projected

##### Script Logs
```
...
INFO:root:Fetching for query parameters: year:2021 genre:emo
INFO:root:Total result so far: 60321
INFO:root:Fetching for query parameters: year:2021 genre:folk
INFO:root:Total result so far: 60368
INFO:root:Fetching for query parameters: year:2021 genre:forro
# Script interrupted here
```

- We run this stage partially and make some projections using the results:
	- By 20 minutes, we collected 60368 results and we've hit the specific query `year 2021, genre "forro"`
	- Total count of genre seeds in spotify: 126 genres
	- Total number of queries that contributed to the result of this run:
		- Query for 2023 and 2022 finished = 2 years queried for all genres
		- (126 genres * 2 years done) + 36 genres (number of genres before forro) = 288 queries contributed to the final result count
	- Number of artist contributed per query:
		- 60368 / 288 ~= 210 artists / query
	- Total number of queries if we execute a query for every genre for every year from 2023 to 1900:
		- 126 genres * (2023 - 1900) = 126 genres * 123 years = 15498 queries.
	- Using the results we've obtained from the interrupted run and the number of queries we project to do in total using this stage, while also halving the results in case the queries results get smaller as we get to the older years:
		- 15498 queries * 210 artist / query * 0.5 reduction factor = **1,627,290 artists fetched**