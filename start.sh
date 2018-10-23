SEED_URLS=$(cat SEED_URLS.txt)

for url in $SEED_URLS
do 
    python crawler.py $url 
done
