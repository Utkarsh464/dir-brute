import argparse
import asyncio
import inspect
import sys
import time
from urllib.parse import urljoin

import aiohttp

from crawler import main_crawl


SUPPORTED_CODES = {200, 301, 302, 303, 307, 308, 401, 403, 404, 500}
REDIRECT_CODES = {301, 302, 303, 307, 308}


def correct_code(code):
    if code not in SUPPORTED_CODES:
        raise ValueError(f"Unsupported status code. Choose from: {sorted(SUPPORTED_CODES)}")
    return code


def url_normalise(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url if url.endswith("/") else url + "/"


class _Resp:
    __slots__ = ("status", "url", "text", "location")

    def __init__(self, status, url, text, location):
        self.status = status
        self.url = url
        self.text = text
        self.location = location


async def fetch_url(session, url, semaphore=None):
    async def request():
        async with session.get(url, allow_redirects=False) as response:
            return _Resp(response.status, str(response.url), await response.text(), response.headers.get("Location"))

    try:
        if semaphore is None:
            return await request()
        async with semaphore:
            return await request()
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None


def format_result(response):
    if response.location:
        return f"{response.url}, {response.status} redirected to {response.location}"
    return response.url


async def check_url(url, words, session, status_filter=None, recurse=False,
                    max_depth=3, verbose=False, crawl=False, text=False,
                    seen=None, depth=0, semaphore=None):
    """Scan one base URL and, optionally, its discovered 200-response directories."""
    base_url = url_normalise(url)
    seen = seen if seen is not None else set()
    if base_url in seen:
        return [], [], {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    seen.add(base_url)

    live, matches = [], []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    targets = [urljoin(base_url, word.lstrip("/")) for word in words]
    responses = await asyncio.gather(*(fetch_url(session, target, semaphore) for target in targets))
    for target, response in zip(targets, responses):
        report["total"] += 1
        if response is None:
            report["errors"] += 1
            if verbose:
                print(f"{target}, request failed")
            continue
        if response.status == 200:
            report["live"] += 1
            live.append(response.url)
            if crawl:
                result = main_crawl(response, text)
                if inspect.isawaitable(result):
                    await result
        elif response.status in REDIRECT_CODES:
            report["redirects"] += 1
        elif 400 <= response.status < 500:
            report["dead"] += 1
        elif response.status >= 500:
            report["errors"] += 1

        if verbose:
            if response.location:
                print(format_result(response))
            else:
                print(f"{response.url}, {response.status}")
        if status_filter is not None and response.status == status_filter:
            matches.append(format_result(response))

    if recurse and depth < max_depth:
        for link in list(live):
            sub_live, sub_matches, sub_report = await check_url(
                link, words, session, status_filter, recurse, max_depth, verbose,
                crawl, text, seen, depth + 1, semaphore
            )
            live.extend(sub_live)
            matches.extend(sub_matches)
            for key in report:
                report[key] += sub_report[key]
    return live, matches, report


async def scan_targets(targets, words, session, **kwargs):
    results = await asyncio.gather(*(check_url(target, words, session, **kwargs) for target in targets))
    all_live, all_matches = [], []
    report = {"total": 0, "live": 0, "redirects": 0, "dead": 0, "errors": 0}
    for live, matches, partial in results:
        all_live.extend(live)
        all_matches.extend(matches)
        for key in report:
            report[key] += partial[key]
    return all_live, all_matches, report


def positive_int(value):
    integer = int(value)
    if integer < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return integer


def build_parser():
    parser = argparse.ArgumentParser(description="Scan URL paths from a wordlist.")
    parser.add_argument("url", help="target base URL, e.g. http://example.com/")
    parser.add_argument("wordlist", help="path to a wordlist; one path per line")
    parser.add_argument("-s", "--file-name", "--file_name", dest="file_name", metavar="FILE", help="save matching URLs")
    parser.add_argument("--crawl", action="store_true", help="crawl each found 200-response URL")
    parser.add_argument("-f", "--filter", type=int, help="only show this status code")
    parser.add_argument("-R", "--recursion", action="store_true", help="scan found URLs recursively")
    parser.add_argument("--max-depth", type=positive_int, default=3, help="maximum recursion depth (default: 3)")
    parser.add_argument("-t", "--workers", type=positive_int, default=4, help="concurrent requests (default: 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print every request")
    parser.add_argument("--text", action="store_true", help="print text while crawling (implies --crawl)")
    return parser


async def _scan(args):
    if args.filter is not None:
        correct_code(args.filter)
    with open(args.wordlist, encoding="utf-8") as wordlist:
        words = [line.strip() for line in wordlist if line.strip()]
    if not words:
        raise ValueError("wordlist contains no paths")

    print(f"starting scan on {args.url}")
    start = time.monotonic()
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(limit=args.workers)
    semaphore = asyncio.Semaphore(args.workers)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        live, matches, report = await scan_targets(
            [args.url], words, session, status_filter=args.filter,
            recurse=args.recursion, max_depth=args.max_depth, verbose=args.verbose,
            crawl=args.crawl or args.text, text=args.text, semaphore=semaphore,
        )

    shown = matches if args.filter is not None else live
    for result in shown:
        print(args.filter if args.filter is not None else 200, result)
    if args.file_name:
        with open(args.file_name, "w", encoding="utf-8") as output:
            output.writelines(f"{result}\n" for result in shown)

    print("=" * 60)
    print(f"scan complete: {report['live']} found, {report['redirects']} redirects, {report['dead']} dead, {report['errors']} errors")
    print("=" * 60)
    print(f"time taken: {time.monotonic() - start:.2f}s")


def main():
    args = build_parser().parse_args()
    try:
        asyncio.run(_scan(args))
    except KeyboardInterrupt:
        print("\nscan interrupted")
        sys.exit(1)
    except (OSError, ValueError) as error:
        print(f"something went wrong: {error}")
        sys.exit(2)


if __name__ == "__main__":
    main()
