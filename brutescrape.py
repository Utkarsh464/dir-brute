import argparse
import requests
from crawl import crawll


def brute(url, wordlist, save=None):
    if save is not None:
        with open(wordlist) as urls:
            with open(save, "w") as live:
                r = None
                for i in urls:
                    try:
                        r = requests.get(url + i.strip(), timeout=10)
                        if r.status_code != 404:
                            print(r.status_code, r.url)
                    except Exception as e:
                        print("cant send request")
                    if r is not None and r.status_code == 200:
                        live.write(r.url + "\n")
        print(f"all live urls are saved in {save}")
        return save
    if save is None:
        with open(wordlist) as urls:
            r = None
            for i in urls:
                try:
                    r = requests.get(url + i.strip(), timeout=10)
                    print(r.status_code, r.url)
                except Exception as e:
                    print("cant send request")
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Brute-force directories on a target URL from a wordlist, "
        "optionally save live (HTTP 200) URLs and crawl their contents."
    )
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="save live (HTTP 200) URLs to FILE, one per line",
    )
    parser.add_argument(
        "url",
        help="target base URL, e.g. http://example.com/",
    )
    parser.add_argument(
        "wordlist_path",
        help="path to the wordlist file, one directory to check per line",
    )
    parser.add_argument(
        "--crawl",
        metavar="FILE",
        help="read saved live URLs from FILE (created with --save) and print "
        "the content of each page",
    )
    args = parser.parse_args()
    try:
        brute(args.url, args.wordlist_path, args.save)
    except Exception as e:
        print(f"some error occoured")
    if args.crawl is not None:
        try:
            crawll(args.crawl)
        except Exception as e:
            print(f"some error occoured")
