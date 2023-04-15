# Discz Artist Scraper

## V2 - Query for top ~1000 artist for every genre, for every year from 2023 to 1900
- Attempt to grab top ~1000 artist for every genre, for every year from 2023 to 0
- This was implemented by splitting the queries into two types: query for each genre per year from 2023 to 1899, and one single query for the year 0 to 1899. This is done because if you do a query for artists in the year range 0-1899, this query returns a finite, <1000 result. So we can just add it separately.
- One run was interrupted at ~20 minutes, but we can make some projections using the results:
	- We collected 60368 results by the time we've hit the specific query (year 2021, genre "forro") the script was doing when it was interrupted
	- Total count of genre seeds in spotify: 126 genres
	- Query for 2023 and 2022 finished = 2 years queried for all genres
	- (126 genres * 2 years done) + 36 genres (number of genres before forro) = 288 queries contributed to the final result count
	- every query produced 60368 / 288 ~= 210 artists / query
	- If we query for every genre for every year from 2023 to 1900, this is in total 126 * (2023 - 1900) = 126 genres * 123 years = 15498 queries.
	- Using the result we've obtained and the number of queries we project to do in total using this stage, while also halving the results in case the queries results get smaller as we get to the older years:
		- 15498 queries * 210 artist / query * 0.5 reduction factor = 1,627,290 artists fetched

## V1 - Query top 1000 artist for every year from 2023 to 1900
- April 11th
- Attempt to grab top ~1000 artist per year from 2023 to 1900
	- (Not always 1000 - the API sometimes quits after ~700 offset, even though limit is 1000)
	- In the case where we always have 1000 unique artists per year, if we go back to 1900 and have 1 kilobyte per artist, that will be 123 years * 1000 * 1000 bytes = 123000000, 123 megabyte - containable in memory
- Running it once, we're able to collect 19029 artists