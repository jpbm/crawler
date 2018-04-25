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
