import requests


def crawl_file(live,crawl_save=None):
    for url in live:
        r = requests.get(url.strip())
        print(f"content of {r.url}, {r.text}")
        if crawl_save:
            with open(crawl_save , 'a')as cs:
                cs.writelines(f"content of {r.url} , {r.text}")

        

           
