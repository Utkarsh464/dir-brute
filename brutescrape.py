import argparse
import requests
from helpers import correct_code, matches_code, crawl_file


def default_brute(url, wordlist, code=None, file_name=None):
    saved = None
    if file_name is not None:
        saved = open(file_name, "w")
    with open(wordlist) as urls:
        for i in urls:
            try:
                r = requests.get(url + i.strip(), timeout=10)
                if code is None or matches_code(r.status_code, code):
                    print(r.status_code, r.url)
                    if saved is not None:
                        saved.write(r.url + "\n")
            except Exception as e:
                print("cant send request")
    if saved is not None:
        saved.close()
        print(f"all urls are saved in {file_name}")


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

    args = parser.parse_args()
    if args.filter is not None:
        try:
            correct_code(args.filter)
        except ValueError as e:
            print(e)

    try:
        default_brute(args.url, args.wordlist_path, args.filter, args.file_name)
        if args.crawl:
            crawl_file(args.crawl)

    except Exception as e:
        print(f"some error occoured")
