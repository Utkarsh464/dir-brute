<div align="center">

# **bustit**

### A directory brute-forcer & crawler

**`probe → filter → collect → crawl`** — throw a wordlist at a target URL, keep the hits that matter, then read back what you found.

<br>

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)
[![aiohttp ≥ 3.9](https://img.shields.io/badge/aiohttp-%3E%3D%203.9-2C6EBD)](https://pypi.org/project/aiohttp/)
[![for authorized testing only](https://img.shields.io/badge/for-authorized%20testing-6f42c1)](#disclaimer)

</div>

**bustit** is a small security tool built while learning how directory enumeration works. It brute-forces hidden paths on a target from a wordlist, prints every response (or only the status code you care about with `-f`), and — with a flag — either saves the matching URLs to a file or crawls them to dump page contents.

> **Try it in the lab:** a full walkthrough of using this tool against a local test server (and fixing bugs found along the way) lives in the [labs repo — dir-brute Directory Enumeration](https://github.com/Utkarsh464/labs/tree/main/web-apps/dir-brute).

---

## How it works

```
         wordlist.txt
              │
              ▼
      ┌─────────────────┐
      │  bustit.py      │   prints: status + URL for every hit
      └────────┬────────┘
               │
        ┌──────┴───────┐
    -f/--filter       -s/--file
        │                │
        ▼                ▼
  only matching    saved URL list
  statuses print
                         │
                    --crawl
                         ▼
                  page links (+ text)
```

## ✨ Features

- **Concurrent** — `-t N` (default `4`) runs N requests in parallel across every word in a single scan, throttled by a shared `aiohttp` session and connection pool; raise the ceiling, not the wall-time
- **Filterable** — `-f CODE` shows only responses matching a status code (`200`, `301`, `302`, `303`, `307`, `308`, `401`, `403`, `404`, `500`)
- **Recursive** — `-R` re-scans every `200` URL it finds, descending up to `--max-depth` levels (default `3`); a `seen` set prevents re-scanning the same path
- **Status-visible output** — every response prints as `status URL` in verbose mode, so dead ends (404s) are easy to spot by eye
- **Verbose** — `-v` prints every request with its status code (and the redirect target for 3xx), so you see the full probe stream instead of just the hits
- **URL normalization** — missing `http://` and trailing `/` are added automatically, so `example.com` works the same as `http://example.com/`
- **`-s` / `--file`** — writes the matching URLs to a file, one per line; with `-f` it saves only that status code
- **`--crawl`** — prints the links found on every `200` page it discovers; combine with `-R` to crawl deeper
  - **Text dump** — add `--text` to also print the text content of each crawled page (`--text` implies `--crawl`)
- **Timed** — prints total elapsed time at the end
- **Scan summary** — prints a one-line tally at the end (`scan complete: X found, Y redirects, Z dead, W errors`), wrapped in `====` separators
  - **Minimal deps** — Python 3.8+, [`aiohttp`](https://pypi.org/project/aiohttp/) `>= 3.9`, and [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) for the crawler

## 🧰 Tools

| File                       | Role                                                                                 | How to run                    |
| -------------------------- | ------------------------------------------------------------------------------------ | ----------------------------- |
| [`bustit.py`](bustit.py)   | Main entry point — brute-forces directories from a wordlist, optionally saves/crawls | `bustit` / `python bustit.py` |
| [`crawler.py`](crawler.py) | Page crawler used by `--crawl` / `--text`                                            | imported by `bustit.py`       |

## 🚀 Quick Start

```bash
git clone https://github.com/Utkarsh464/dir-brute.git
cd dir-brute
pip install .
# or, with uv:
uv tool install .
```

This installs the `bustit` command on your PATH (it works with `pip`/`uv` and Python 3.8+). After that you can run `bustit` from anywhere.

## 🛠️ Usage

> All examples assume a wordlist with one path per line — e.g. `admin`, `login`, `api`. Bring your own, or grab a list from [SecLists](https://github.com/danielmiessler/SecLists).

### Brute-force directories

```bash
bustit http://example.com/ wordlist.txt
# 200 http://example.com/admin
# 301 http://example.com/login
# 200 http://example.com/api
# ...
# ============================================================
# scan complete: 2 found, 1 redirects, 0 dead, 0 errors
# ============================================================
# time taken: 0.42s
```

Live `200` pages print as `200 URL`; a compact summary shows the final tally.

### Verbose mode

Add `-v` to see every request, not just the hits:

```bash
bustit http://example.com/ wordlist.txt -v
# http://example.com/.bash_history , 404
# http://example.com/admin , 200
# http://example.com/login , 301 redirected to /login.php
# http://example.com/nothere , 404
# ...
```

### Filter by status code

```bash
bustit http://example.com/ wordlist.txt -f 200
# 200 http://example.com/admin
# 200 http://example.com/api
```

Only the status codes you ask for are printed — useful for finding live paths or dead ends.

### Save URLs

```bash
bustit http://example.com/ wordlist.txt -s live_urls.txt
# all urls are saved in live_urls.txt
```

The matching URLs (`200`s, or the `-f` status code when one is set) are written one per line, ready to crawl.

### Recursive brute

```bash
bustit http://example.com/ wordlist.txt -R --max-depth 5
```

Every `200` URL gets re-scanned against the wordlist, descending up to `--max-depth` levels (default `3`). A `seen` set stops already-visited paths from being scanned twice.

### Crawl found pages

Add `--crawl` to print the links found on every `200` page the scan discovers:

```bash
bustit http://example.com/ wordlist.txt --crawl
# link in http://example.com/admin: /dashboard
# link in http://example.com/admin: /settings
```

Add `--text` to also print the text content of each crawled page (`--text` implies `--crawl`, so you don't need both flags):

```bash
bustit http://example.com/ wordlist.txt --text
# link in http://example.com/admin: /dashboard
# text content of http://example.com/admin , Dashboard Welcome to your admin panel ...
```

### Options

| Argument            | Description                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| `url`               | Target base URL, e.g. `http://example.com/`                            |
| `wordlist`          | Path to the wordlist — one path to check per line                      |
| `-f, --filter CODE` | Only print responses matching this status code                         |
| `-R, --recursion`   | Re-scan every `200` URL found, descending each                         |
| `--max-depth N`     | Max recursion depth (default `3`)                                      |
| `-s, --file FILE`   | Save matching URLs to `FILE`, one per line                             |
| `-t, --workers N`   | Concurrent requests (default `4`)                                      |
| `--crawl`           | Print links found on every `200` page (boolean)                        |
| `--text`            | Also print the text content of each crawled page (implies `--crawl`)   |
| `-v, --verbose`     | Print every request with its status code (and redirect target for 3xx) |

## 📦 Requirements

- **Python 3.8+**
- [`aiohttp`](https://pypi.org/project/aiohttp/) `>= 3.9` — pinned in `pyproject.toml` / `requirements.txt`
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) `>= 4.11` — used by the crawler (`--crawl` / `--text`)

## 🤝 Contributing

Feel free to fork this repo and open a pull request if you have ideas — better wordlists, new features, bug fixes, anything. This is a learning project, so PRs are welcome.

## ⚠️ Disclaimer

These tools are provided **for educational and authorized testing purposes only**. Unauthorized use of security tools against systems you do not own or have explicit permission to test is illegal. The author is not responsible for any misuse of these tools.

## 📄 License

Released under the [MIT License](LICENSE).

<br>

<div align="center">

**Utkarsh S.** — Cybersecurity Student

[GitHub](https://github.com/Utkarsh464) · [LinkedIn](https://linkedin.com/in/utkarsh-solanki-337806252)

</div>
