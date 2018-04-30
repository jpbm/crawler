# crawler
Program designed to crawl and download HTML content from websites based on a seed link, then by following hyperreferences.

# usage
From the commandline, run the crawler with the following format for a seed URL and a destination file:

    ``$ python crawler.py 'https://www.nytimes.com' 'data/nytimes.json'``

The number of hyperrefs found on the seed URL will be printed. If the number is '1' then the automatically generated regular expression that is supposed to find hyperlinks is not working for the format of the seed url. Right now, this means that the script has to be modified manually so that hyperreferences are found.

# how it works
   1. Creates a regular expression that is used to extract hyperreferences to html files under the seed domain:

        ``hyperref_re = re.compile(SEED_URL+'[A-Za-z0-9_-]*[.]html)``

   2. Access and download seed url and extract all the hyperreferences found there, creating a first list of urls to work with.

   3. Recursively download HTMLs, each time extracting hyperreferences pointing towards more HTMLs and adding them to the queue as long as they haven't been 'seen' before. A bloom filter is used to check whether a url has been seen. Downloading is done using a threadpool with 20 workers.


# specialized crawlers
``crawler.py`` is a template that happens to work for the New York Times. Other outlets will require some customization. Most commonly, the method for extracting hyperreferences needs to be modified. Sometimes the crawler has to be deliberately slowed down to avoid rate limits (c.f. ``chicagotribune_crawler.py``)

# scraping works well for...
    - New York Times (145,494 documents, crawler converged)
    - New York Daily News (155,323 documents, crawler did not converge)
    - New York Post (759,727 documents, crawler converged)
    - Washington Post (57,700 documents, crawler did not converge)
    - Wall Street Journal (46,722 documents, crawler converged)

# scraping doesn't work so well for...
    - Chicago Tribune (aggressive rate limit)
    - Huffington Post (1600+ documents, appears to scrape correctly, then stalls)
    - Slate (crawler converges with only 516 documents)
    - The Onion (crawler converges with 27 documents)
