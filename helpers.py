import requests


def correct_code(code):
    supported = [200, 301, 302, 307, 308, 401, 403]
    if code not in supported:
        raise ValueError(f"Unsupported status code. Choose from: {supported}")
    return code


def matches_code(status, code):
    return status == code


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


def url_normalise(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    url = url.strip()
    return url

def check_url(url):
    r = requests.get(url , timeout=10)
    return r