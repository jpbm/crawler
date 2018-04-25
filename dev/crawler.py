import sys
import re
from concurrent import futures
import argparse

import requests
from bloom_filter import BloomFilter

sys.path.append('../data/raw/')

urls_seen = BloomFilter(max_elements=500000, error_rate=0.1)
urls_to_do = set()

def initialize():
    response = requests.get(SEED_URL)
    global hyperrefs_re
    hyperrefs_re = re.compile(SEED_URL+'[a-zA-Z0-9/_-]*[.]html')
    global file
    file = open(FILENAME,'w')
    global file_length
    file_length = 0
    if response.status_code == 200:
        html = response.text
        urls = hyperrefs_re.findall(html)
        print("[initialize] Seeding with %i urls found via %s." % (len(set(urls))+1,SEED_URL))
        urls_to_do.update(urls)
        urls_to_do.update([SEED_URL])
    else:
        print("[initialize] Failed. Code: %i %s" % (response.status_code,SEED_URL))
        
def urls_gen():
    url = urls_to_do.pop()
    return url

def process_one(url):
    """
    Takes:
    url [str]
    
    From global name space:
    file [file object]
    hyperrefs_re [regex]
    file_length [int]
    """
    
    urls_seen.add(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        html = response.text
        item = "{'url': %s, 'html': %s}\n" % (url,html)
        urls_found = hyperrefs_re.findall(html)
        for url_found in urls_found:
            if not url_found in urls_seen:
                urls_to_do.update([url_found])
        global file
        file.write(item)
        global file_length
        file_length += 1
        print('[process_one] %i processed %i to go.' % (file_length,len(urls_to_do)),end = '\r')
    elif response.status_code == 503:
        urls_to_do.update([url])
    else:
        print('[process_one] Code: %i %s' % (response.status_code,url))


def process_many():
    """
    0. Checks if urls_do_do has content
    1. Creates copy of urls_to_do
    2. Uses threadpool to process all entires in the copy of urls_to_do
    3. process one updates the original copy of urls_do_do with new-found urls. Whether a urls is new or not is checked against the bloom filter `urls_seen`.
    
    Takes:
    
    From global name space:
    urls_to_do
    """
    print('[process_many] Writing to %s' % FILENAME, end = '\r')
    while len(urls_to_do) != 0:
        print('[process_many] Starting loop...')
        workers = min(MAX_WORKERS,len(urls_to_do))
        with futures.ThreadPoolExecutor(workers) as executor:
            list(executor.map(process_one,list(urls_to_do)))
    file.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl some website.')
    parser.add_argument('seed_url',metavar='u',type=str,help='seed url for the crawler')
    parser.add_argument('filename',metavar='d',type=str,help='path and filename')
    
    args = parser.parse_args()
    MAX_WORKERS = 20
    SEED_URL = args.seed_url
    FILENAME = args.filename

    initialize()
    process_many()
