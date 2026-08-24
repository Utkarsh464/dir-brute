<div align="center">

# **dir-brute**

### A directory brute-forcer & crawler

**`probe → filter → collect → crawl`** — throw a wordlist at a target URL, keep the hits that matter, then read back what you found.

<br>

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)
[![requests ≥ 2.28](https://img.shields.io/badge/requests-%3E%3D%202.28-0A7EA4)](https://pypi.org/project/requests/)
[![for authorized testing only](https://img.shields.io/badge/for-authorized%20testing-6f42c1)](#disclaimer)

</div>

**dir-brute** is a small security tool built while learning how directory enumeration works. It brute-forces hidden paths on a target from a wordlist, prints every response (or only the status code you care about with `-f`), and — with a flag — either saves the matching URLs to a file or crawls them to dump page contents.

> **Try it in the lab:** a full walkthrough of using this tool against a local test server (and fixing bugs found along the way) lives in the [labs repo — dir-brute Directory Enumeration](https://github.com/Utkarsh464/labs/tree/main/web-apps/dir-brute).

---

## How it works

```
         wordlist.txt
              │
              ▼
      ┌─────────────────┐
      │  brutescrape.py │   prints: status + URL for every hit
      └────────┬────────┘
               │
        ┌──────┴───────┐
    -f/--filter      -s/--file_name
        │                │
        ▼                ▼
  only matching    saved URL list
  statuses print
                        │
                   --crawl
                        ▼
                 page contents
```

## ✨ Features

- **Filterable** — `-f CODE` shows only responses matching a status code (`200`, `301`, `302`, `307`, `308`, `401`, `403`)
  - **Recursive** — `-R` re-scans every `200` URL it finds, descending into each (no depth limit)
- **Status-visible output** — every response prints as `status URL`, so dead ends (404s) are easy to spot by eye; there is no automatic 404-detection logic
- **Verbose** — `-v` prints every request with its status code (and the redirect target for 3xx), so you see the full probe stream instead of just the hits
- **URL normalization** — missing `http://` and trailing `/` are added automatically, so `example.com` works the same as `http://example.com/`
- **`-s` / `--file_name`** — writes every response URL to a file, one per line; combine with `-f` to save only matching statuses
- **`--crawl`** — prints the contents of every found page. Use it alone to crawl the scan's own results, or pass a file (`--crawl urls.txt`) to crawl a saved list
  - **Concurrent** — `-t N` runs N requests in parallel; combine with `-R` for threaded recursion
- **Timed** — prints total elapsed time at the end
- **Scan summary** — prints a one-line tally at the end (`scan complete: X found, Y redirects, Z dead, W errors`), wrapped in `====` separators
- **Minimal deps** — Python 3.8+ and [`requests`](https://pypi.org/project/requests/), that's it

## 🧰 Tools

| File                               | Role                                                                                 | How to run              |
| ---------------------------------- | ------------------------------------------------------------------------------------ | ----------------------- |
| [`brutescrape.py`](brutescrape.py) | Main entry point — brute-forces directories from a wordlist, optionally saves/crawls | `python brutescrape.py` |

    | [`crawler.py`](crawler.py)         | Page crawler used by `--crawl`                                                          | imported by `brutescrape.py` |

## 🚀 Quick Start

```bash
git clone https://github.com/Utkarsh464/dir-brute.git
cd dir-brute
pip install -r requirements.txt
```

## 🛠️ Usage

> All examples assume a wordlist with one path per line — e.g. `admin`, `login`, `api`. Bring your own, or grab a list from [SecLists](https://github.com/danielmiessler/SecLists).

### Brute-force directories

```bash
python brutescrape.py http://example.com/ wordlist.txt
# 200 http://example.com/admin
# 301 http://example.com/login
# 200 http://example.com/api
# 404 http://example.com/nothere
# ...
```

### Verbose mode

Add `-v` to see every request, not just the hits:

```bash
python brutescrape.py http://example.com/ wordlist.txt -v
# http://example.com/.bash_history , 404
# http://example.com/admin , 200
# http://example.com/login , 301 redirected to /login.php
# ...
```

### Filter by status code

```bash
python brutescrape.py http://example.com/ wordlist.txt -f 200
# 200 http://example.com/admin
# 200 http://example.com/api
```

Only the status codes you ask for are printed — useful for finding live paths or dead ends.

### Save URLs

```bash
python brutescrape.py http://example.com/ wordlist.txt -s live_urls.txt
# all urls are saved in live_urls.txt
```

Every response URL is written (only the `-f` status code when one is set) — one URL per line, ready to crawl. Note: without `-f`, `-s` saves _all_ responses, 404s included.

### Recursive brute

```bash
python brutescrape.py http://example.com/ wordlist.txt -R -s found.txt
# console (top level only):
# 200 http://example.com/admin
# 200 http://example.com/login
# found.txt (nested paths discovered by recursion):
# http://example.com/admin/users
# http://example.com/admin/users/profile
# ...
```

Every `200` URL gets re-scanned against the wordlist, descending into each level with **no depth limit**. Deeper levels are written to the `-s` file when given; only the top level prints to the console. Combine with `-t N` for threaded recursion.

> **Redirects are not followed.** A `301`/`302`/`307`/`308` is reported as-is (with its `Location` header shown when you use `-f`), so `-f 301` and friends match correctly instead of collapsing to the target.

### Crawl found pages

`--crawl` works two ways:

**On the scan's own results** — no file needed, just add `--crawl`:

```bash
python brutescrape.py http://example.com/ wordlist.txt --crawl
# the content of http://example.com/admin
# <!doctype html>
# <html>...
```

**On a saved list** — pass the file you wrote with `-s`:

```bash
python brutescrape.py http://example.com/ wordlist.txt -s live_urls.txt --crawl live_urls.txt
# the content of http://example.com/admin
# <!doctype html>
# <html>...
```

Combine with `-R` or `-t` to crawl a larger set of discovered pages.

### Options

| Argument | Description                                 |
| -------- | ------------------------------------------- |
| `url`    | Target base URL, e.g. `http://example.com/` |

    | `wordlist`        | Path to the wordlist — one directory to check per line        |

| `-f, --filter CODE` | Only print responses matching this status code |
| `-R, --recursion` | Re-scan every `200` URL found, descending into each (no depth limit) |
| `-s, --file_name FILE` | Save matching URLs to `FILE`, one per line |
| `-t, --threads N` | Run N requests in parallel; combine with `-R` for threaded recursion |
| `--crawl [FILE]` | Print page contents of found URLs. No file = crawl the scan results; with a file = crawl that saved list |
| `-v, --verbose` | Print every request with its status code (and redirect target for 3xx) |

## 📦 Requirements

- **Python 3.8+**
- [`requests`](https://pypi.org/project/requests/) `>= 2.28` — pinned in [`requirements.txt`](requirements.txt)

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
