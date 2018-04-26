import re
from concurrent import futures
import argparse
import json
from time import sleep, time
from numpy.random import randint

import requests
from bloom_filter import BloomFilter

urls_seen = BloomFilter(max_elements=500000, error_rate=0.1)
urls_to_do = set()
processed = 0
offset = 0

def initialize():
    response = requests.get(SEED_URL)
    global hyperrefs_re
    hyperrefs_re = re.compile('(?<=href=")%s[A-Za-z0-9_/-]*[.]html(?=")' % SEED_URL)
    #hyperrefs_re = re.compile(SEED_URL+'[a-zA-Z0-9/_-]*[.]html')
    global filename
    filename = filename_gen()
    if response.status_code == 200:
        html = response.text
        urls = hyperrefs_re.findall(html)
        print("[initialize] Seeding with %i urls found via %s." % (len(set(urls))+1,SEED_URL))
        urls_to_do.update(urls)
        urls_to_do.update([SEED_URL])
    else:
        print("[initialize] Failed. Code: %i %s" % (response.status_code,SEED_URL))
        

def process_one(url):
    """
    Takes:
    url [str]
    
    From global name space:
    file [file object]
    hyperrefs_re [regex]
    """
    global urls_to_do
    try:
        urls_seen.add(url)
        response = requests.get(url)

        if response.status_code == 200:
            html = response.text
            item = json.dumps({'url':url,'html':html})+"\n"
            urls_found = hyperrefs_re.findall(html)
            for url_found in urls_found:
                if not url_found in urls_seen:
                    urls_to_do.update([url_found])
            global file
            file.write(item)
            global processed
            processed += 1
            urls_to_do.remove(url)
            print('[process_one] %i downloaded %i to go.' % (processed,len(urls_to_do)),end = '\r')
        elif response.status_code != 429 and response.status_code != 503:
            urls_to_do.remove(url)
            print('[process_one] [removed] Code: %i %s' % (response.status_code,url))
        else:
            print('[process_one] [sleeping] Code: %i [processed %i] %s' % (response.status_code,processed,url))
            global offset
            offset += 0
            offset = min(5*60,offset)
            sleep(offset + randint(MAX_WORKERS))
            
    except:
        print('[process_one] [exception] %s' % url)


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
        global av_time
        av_time = processed/(time()-t0)
        global file
        global filename
        file = open(next(filename),'w')
        print('\n[process_many] Starting next batch. (Avg. freq.: %1.3fHz)' % av_time)
        workers = min(MAX_WORKERS,len(urls_to_do))
        with futures.ThreadPoolExecutor(workers) as executor:
            list(executor.map(process_one,list(urls_to_do)[:1000]))
        file.close()
    print("Crawl complete. (you are unlikely to ever see this message...")

def filename_gen():
    i = 0
    global FILENAME
    path, filetype = FILENAME.split('.')
    while True:
        filename = path+str(i)+'.'+filetype
        yield filename
        i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl some website.')
    parser.add_argument('seed_url',metavar='u',type=str,help='seed url for the crawler')
    parser.add_argument('filename',metavar='d',type=str,help='path and filename')
    
    args = parser.parse_args()
    MAX_WORKERS = 50
    SEED_URL = args.seed_url
    FILENAME = args.filename

    initialize()
    t0 = time()
    process_many()
