# Various scripts and files

## github-json-stata
`jsonToCsv.py` extracts specific fields from Github API json output and writes them to .csv files. `stata-commands.txt` contains lines that can be copied and pasted into STATA to convert date and time strings to STATA datetime fields. 

## trends-scraper
`scrape.py` uses a modified version of [unofficial-google-trends-api](https://github.com/suryasev/unofficial-google-trends-api) to grab data for a list of terms in `words-list.txt`. Currently, it crashes when it hits the Google rate limit or when there isn't enough search volume for Trends to return data. 
