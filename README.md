# Discz Artist Scraper

## Run Instructions

```
# Needed to authorize Spotipy python library
export SPOTIPY_CLIENT_ID=d44c1b8a65604265a5abc858294aa830
export SPOTIPY_CLIENT_SECRET=09ff84f3e5774851858751621647985e
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback

python3 main.py
```

## Total amount of artists projected to be fetched

```
99,138 (B) + 1,627,290 (A) + 989 (C) = 1,727,417 artists
```

## Queries Breakdown

### Query Stage C - Query for artists for the year range 0-1899
- Querying for artists in the year range 0-1899 returns a finite, <1000 result. So we can execute this simple query on its own, separate from the other query stages.

#### Actual result: 989 artists

### Query Stage B - Collect artists from hipster albums from 2023 to 1900.
- General idea: Query "hipster" albums for every year from 2023 to 1900. Then, aggregate all artists from these albums.
	- There are settings in Spotify's search API that can allow us to look for albums with less than 10% popularity, the parameter `tag:hipster`.
	- Utilizing this query in addition to Query A does mean that we essentially have results that consist of the most popular artists and least popular artists per year, with artists that have middle popularity being missing.

#### Result projection: 99,138 artists

##### Script Logs
```
INFO:root:Start time: 2023-04-14 21:30:12.306595
INFO:root:Fetching for album query parameters: tag:hipster year:2023
INFO:root:Album query offset maximum hit at: 1000
INFO:root:Total result so far: 769
...
INFO:root:Fetching for album query parameters: tag:hipster year:1980
INFO:root:Album query offset maximum hit at: 1000
INFO:root:Total result so far: 34356
INFO:root:Current time: 2023-04-14 21:42:15.922796
# Script interrupted here
```

- We run this stage for ~12 minutes and make some projections with the result:
	- 43 years covered in this run.
	- 34653 artists discovered in this run.
	- Every query discovers 34653 / 43 ~= 806 artists
	- Total number of queries if we execute a query for every year from 2023 to 1900: (2023 - 1900) = 123 queries
	- Projected total of artists to be discovered: 123 queries * 806 artists = **99,138 artists**



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

- We run this stage for ~20 minutes and make some projections using the results:
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