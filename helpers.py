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
                print(f"the content of {r.url}: {r.text}")
            except Exception as e:
                print(f"cant get content of {url}")
