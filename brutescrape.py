import argparse
import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from crawler import crawl_file


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


def check_url(url, wordlist, file_name=None, filter=None, recursion=None, v=None):
    url = url_normalise(url)
    live = []
    status = []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    try:
        with open(wordlist, "r") as wl:
            for word in wl:
                redirect_url = None
                try:
                    r = requests.get(
                        (url + word).strip(), timeout=10, allow_redirects=False
                    )
                except Exception as e:
                    continue

                report["total"] += 1
                if r.status_code == 200:
                    report["live"] += 1
                elif r.status_code in (301, 302, 307, 308):
                    report["redirects"] += 1
                elif r.status_code in (401, 403):
                    report["dead"] += 1
                elif r.status_code >= 500:
                    report["errors"] += 1

                if r.status_code in (301, 302, 303, 307, 308):
                    redirect_url = r.headers.get("Location")
                if v:
                    if redirect_url:
                        print(f"{r.url},{r.status_code} redirected to {redirect_url}")
                    print(f"{r.url} , {r.status_code}")
                if filter and r.status_code == filter:
                    if redirect_url:
                        status.append(
                            f"{r.url} , {r.status_code} redirected to {redirect_url}"
                        )
                    else:
                        status.append(r.url)
                if r.status_code == 200:
                    live.append(r.url)
            if recursion:
                for link in live:
                    _, _, sub_report = check_url(
                        link, wordlist, file_name, filter, recursion, v
                    )
                    for k in report:
                        if k in sub_report:
                            report[k] += sub_report[k]
    except KeyboardInterrupt:
        print("\nscan interrupted")
        return live, status, report
    except Exception as e:
        print(e)

    if file_name:
        try:
            with open(file_name, "a") as f:
                saved = status if filter else live
                f.writelines(u + "\n" for u in saved)
        except Exception as e:
            print(e)

    return live, status, report


def threads(
    targets, wordlist, file_name=None, filter=None, workers=4, recursion=None, v=None
):
    all_live = []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(check_url, u, wordlist, file_name, filter, recursion, v)
            for u in targets
        ]
        for f in futures:
            found_live, found_status, f_report = f.result()
            all_live.extend(found_live)
            for k in report:
                if k in f_report:
                    report[k] += f_report[k]
            for u in found_live:
                print(200, u)
            if filter is not None:
                for u in found_status:
                    print(filter, u)
    return all_live, report


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
        nargs="?",
        const=True,
        default=None,
        metavar="FILE",
        help="crawl found URLs and print page content. Use alone (--crawl) "
        "to crawl scan results, or --crawl FILE to crawl a saved file",
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
    parser.add_argument(
        "-v",
        "--verbose",
        help="print every request with its status code",
        action="store_true",
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
            if args.crawl is True:
                print("crawling scan results")
            else:
                print(f"crawling urls from {args.crawl}")

        all_live = []
        total_report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
        if args.recursion:
            if args.threads:
                all_live, scan_report = threads(
                    [args.url],
                    args.wordlist,
                    args.file_name,
                    args.filter,
                    workers=args.threads,
                    recursion=True,
                    v=args.verbose,
                )
            else:
                live, status, scan_report = check_url(
                    args.url,
                    args.wordlist,
                    args.file_name,
                    args.filter,
                    recursion=True,
                    v=args.verbose,
                )
                all_live = live
                for u in live:
                    print(200, u)
                for u in status:
                    print(args.filter, u)
            for k in total_report:
                if k in scan_report:
                    total_report[k] += scan_report[k]
        elif args.threads:
            all_live, scan_report = threads(
                [args.url],
                args.wordlist,
                args.file_name,
                args.filter,
                workers=args.threads,
                v=args.verbose,
            )
            for k in total_report:
                if k in scan_report:
                    total_report[k] += scan_report[k]
        else:
            live, status, scan_report = check_url(
                args.url,
                args.wordlist,
                args.file_name,
                args.filter,
                v=args.verbose,
            )
            all_live = live
            for u in live:
                print(200, u)
            for u in status:
                print(args.filter, u)
            for k in total_report:
                if k in scan_report:
                    total_report[k] += scan_report[k]

        print("=" * 60)
        print(
            f"scan complete: {total_report['live']} found, "
            f"{total_report['redirects']} redirects, "
            f"{total_report['dead']} dead, "
            f"{total_report['errors']} errors"
        )
        print("=" * 60)

        if args.crawl:
            print("crawling found URLs")
            print("=" * 60)
            if args.crawl is True:
                crawl_file(all_live)
            else:
                try:
                    with open(args.crawl) as f:
                        urls = [line.strip() for line in f if line.strip()]
                    crawl_file(urls)
                except Exception as e:
                    print(e)

        end = time.time()
        print(f"time taken: {end - start:.2f}s")

    except KeyboardInterrupt:
        print("\nscan interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"something went wrong: {e}")
