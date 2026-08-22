import requests


def crawl_file(live, crawl_save=None):
    for url in live:
        try:
            r = requests.get(url.strip(), timeout=10)
        except requests.RequestException as e:
            print(f"could not fetch {url}: {e}")
            continue
        print(f"content of {r.url}, {r.text}")
        if crawl_save:
            with open(crawl_save, "a") as cs:
                cs.writelines(f"content of {r.url} , {r.text}")

        

           
