import argparse
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from helpers import correct_code, matches_code, crawl_file, url_normalise, check_url


def try_url(base_url, word, code, lock, saved_file):
    """Single request — runs inside thread pool."""
    try:
        r = check_url(base_url + word.strip())
        if code is None or matches_code(r.status_code, code):
            print(r.status_code, r.url)
            if saved_file:
                with lock:
                    saved_file.write(r.url + "\n")
            return r
    except Exception:
        print("request failed")
    return None


def default_brute(
    url, wordlist, code=None, file_name=None, recursion=False, max_workers=10
):
    url = url_normalise(url)
    saved = None
    if file_name:
        saved = open(file_name, "w")

    with open(wordlist) as f:
        words = f.readlines()

    lock = threading.Lock()
    found_200s = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(try_url, url, word, code, lock, saved) for word in words]
        for future in futures:
            result = future.result()
            if result and result.status_code == 200:
                found_200s.append(result.url)

    if saved:
        saved.close()
        print(f"urls saved in {file_name}")

    if recursion:
        for found_url in found_200s:
            default_brute(
                found_url, wordlist, code=None, recursion=False, max_workers=max_workers
            )


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
        "wordlist_path",
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
        help="number of concurrent threads (default 10)",
        type=int,
        default=10,
    )

    args = parser.parse_args()
    start = time.time()
    print(f"starting brute force on {args.url}")
    if args.filter is not None:
        print(f"filtering for status code {args.filter}")
    if args.file_name is not None:
        print(f"saving matches to {args.file_name}")
    if args.crawl:
        print(f"crawling urls from {args.crawl}")
    if args.filter is not None:
        try:
            correct_code(args.filter)
        except ValueError as e:
            print(e)

    try:
        default_brute(
            args.url,
            args.wordlist_path,
            args.filter,
            args.file_name,
            args.recursion,
            args.threads,
        )
        if args.crawl:
            crawl_file(args.crawl)
        end = time.time()
        print(f"time taken: {end - start:.2f}s")
    except Exception as e:
        print("something went wrong")
