import argparse
import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from helpers import crawl_file


def correct_code(code):
    supported = [200, 301, 302, 307, 308, 401, 403]
    if code not in supported:
        raise ValueError(f"Unsupported status code. Choose from: {supported}")
    return code


def url_normalise(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    url = url.strip()
    return url


def check_url(url, wordlist, file_name=None, filter=None, recursion=None):
    url = url_normalise(url)
    live = []
    status = []
    with open(wordlist, "r") as wl:
        for word in wl:
            r = requests.get((url + word).strip(), timeout=10)
            if filter and r.status_code == filter:
                status.append(r.url)
            if filter == None and r.status_code == 200:
                live.append(r.url)
        if recursion:
            for link in live:
                check_url(link, wordlist, file_name, filter, recursion)

        if file_name:
            with open(file_name, "a") as f:
                saved = status if filter else live
                f.writelines(u + "\n" for u in saved)

    return live, status


def threads(targets, wordlist, file_name=None, filter=None, workers=4, recursion=None):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(check_url, u, wordlist, file_name, filter, recursion)
            for u in targets
        ]
        for f in futures:
            found_live, found_status = f.result()
            for u in found_live:
                print(200, u)
            if filter is not None:
                for u in found_status:
                    print(filter, u)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Brute-force directories on a target URL from a wordlist, "
        "optionally save matching URLs and crawl their contents."
    )
    parser.add_argument(
        "--file_name",
        "-s",
        metavar="FILE",
        help="save matching URLs to FILE, one per line",
    )
    parser.add_argument(
        "url",
        help="target base URL, e.g. http://example.com/",
    )
    parser.add_argument(
        "wordlist",
        help="path to the wordlist file, one directory to check per line",
    )
    parser.add_argument(
        "--crawl",
        metavar="FILE",
        help="read URLs from FILE (saved with -s/--file_name) and print "
        "the content of each page",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="status code to filter",
        type=int,
    )

    parser.add_argument(
        "-R",
        "--recursion",
        help="recursive brute",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--threads",
        help="number of worker threads for parallel scan",
        type=int,
    )

    args = parser.parse_args()
    start = time.time()
    try:
        if args.filter is not None:
            try:
                correct_code(args.filter)
            except ValueError as e:
                print(e)
                sys.exit(1)

        print(f"starting brute force on {args.url}")
        if args.filter is not None:
            print(f"filtering for status code {args.filter}")
        if args.file_name is not None:
            print(f"saving matches to {args.file_name}")
        if args.crawl:
            print(f"crawling urls from {args.crawl}")

        if args.recursion:
            if args.threads:
                threads(
                    [args.url],
                    args.wordlist,
                    args.file_name,
                    args.filter,
                    workers=args.threads,
                    recursion=True,
                )
            else:
                check_url(
                    args.url, args.wordlist, args.file_name, args.filter, recursion=True
                )
        elif args.threads:
            threads(
                [args.url],
                args.wordlist,
                args.file_name,
                args.filter,
                workers=args.threads,
            )
        else:
            live, status = check_url(
                args.url, args.wordlist, args.file_name, args.filter
            )
            for u in live:
                print(200, u)
            for u in status:
                print(args.filter, u)

        if args.crawl:
            crawl_file(args.crawl)

        end = time.time()
        print(f"time taken: {end - start:.2f}s")
    except Exception as e:
        print(f"something went wrong: {e}")
