import requests


def crawll(save):
    with open(save, "r") as links:
        for link in links:
            link = link.strip()
            try:
                r = requests.get(link, timeout=10)
                print(f"content of this url : {r.url}")
                print(r.text)
            except Exception as e:
                print(f"cannot get content of this url : {link}")
