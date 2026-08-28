import argparse
import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from crawler import main_crawl


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


def fetch_url(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=False)
        return r
    except Exception:
        return None


def check_url(
    url,
    wordlist,
    file_name=None,
    filter=None,
    recursion=None,
    v=None,
    crawl=None,
    text=None,
):
    url = url_normalise(url)
    live = []
    status = []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}

    try:
        with open(wordlist, "r") as wl:
            for word in wl:
                r = fetch_url(url + word)
                if r is None:
                    continue

                report["total"] += 1
                redirect_url = None

                if r.status_code == 200:
                    report["live"] += 1
                    live.append(r.url)
                    if crawl:
                        main_crawl(r, text)
                elif r.status_code in (301, 302, 303, 307, 308):
                    report["redirects"] += 1
                    redirect_url = r.headers.get("Location")
                elif r.status_code in (401, 403):
                    report["dead"] += 1
                elif r.status_code >= 500:
                    report["errors"] += 1

                if v:
                    if redirect_url:
                        print(f"{r.url}, {r.status_code} redirected to {redirect_url}")
                    print(f"{r.url} , {r.status_code}")

                if filter is not None and r.status_code == filter:
                    if redirect_url:
                        status.append(
                            f"{r.url} , {r.status_code} redirected to {redirect_url}"
                        )
                    else:
                        status.append(r.url)

            if recursion:
                for link in live:
                    _, _, sub = check_url(
                        link,
                        wordlist,
                        file_name,
                        filter,
                        recursion,
                        v,
                        crawl,
                        text,
                    )
                    for k in report:
                        if k in sub:
                            report[k] += sub[k]
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
    targets,
    wordlist,
    file_name=None,
    filter=None,
    workers=4,
    recursion=None,
    v=None,
    crawl=None,
    text=None,
):
    all_live = []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                check_url, u, wordlist, file_name, filter, recursion, v, crawl, text
            )
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
    parser.add_argument("url", help="target base URL, e.g. http://example.com/")
    parser.add_argument(
        "wordlist", help="path to the wordlist file, one directory to check per line"
    )
    parser.add_argument(
        "-s", "--file_name", metavar="FILE", help="save matching URLs to FILE"
    )
    parser.add_argument(
        "--crawl",
        nargs="?",
        const=True,
        default=None,
        help="crawl found URLs and print their links. Use alone (--crawl) "
        "to crawl the scan's own results",
    )
    parser.add_argument(
        "-f", "--filter", type=int, help="only show results with this status code"
    )
    parser.add_argument(
        "-R", "--recursion", action="store_true", help="recurse into found directories"
    )
    parser.add_argument(
        "-t", "--threads", type=int, help="number of worker threads for parallel scan"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print every request"
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="print the text content of each found page (implies --crawl)",
    )
    args = parser.parse_args()

    # --text implies --crawl: dumping page text only makes sense while crawling
    crawl = args.crawl or args.text

    start = time.time()
    try:
        # make sure the filter value is one we actually support
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
        if crawl:
            if crawl is True:
                print("crawling scan results")
            else:
                print(f"crawling urls from {crawl}")

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
                    crawl=crawl,
                    text=args.text,
                )
            else:
                live, status, scan_report = check_url(
                    args.url,
                    args.wordlist,
                    args.file_name,
                    args.filter,
                    recursion=True,
                    v=args.verbose,
                    crawl=crawl,
                    text=args.text,
                )
                all_live = live
                for u in live:
                    print(200, u)
                for u in status:
                    print(args.filter, u)
        elif args.threads:
            all_live, scan_report = threads(
                [args.url],
                args.wordlist,
                args.file_name,
                args.filter,
                workers=args.threads,
                v=args.verbose,
                crawl=crawl,
                text=args.text,
            )
        else:
            live, status, scan_report = check_url(
                args.url,
                args.wordlist,
                args.file_name,
                args.filter,
                v=args.verbose,
                crawl=crawl,
                text=args.text,
            )
            all_live = live
            for u in live:
                print(200, u)
            for u in status:
                print(args.filter, u)

        # fold the per-scan report into the totals
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

        end = time.time()
        print(f"time taken: {end - start:.2f}s")

    except KeyboardInterrupt:
        print("\nscan interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"something went wrong: {e}")
