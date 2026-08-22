import requests

def crawl_file(file):
    with open(file, "r") as urls:
        for url in urls:
            url = url.strip()
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    print(f"the content of {r.url}: {r.text}")
            except Exception as e:
                print(f"could not fetch {url}")



