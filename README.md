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
- **Recursive** — `-R` re-scans every `200` URL it finds, one level deep
- **Status-visible output** — every response prints as `status URL`, so dead ends (404s) are easy to spot by eye; there is no automatic 404-detection logic
- **URL normalization** — missing `http://` and trailing `/` are added automatically, so `example.com` works the same as `http://example.com/`
- **`-s` / `--file_name`** — writes every response URL to a file, one per line; combine with `-f` to save only matching statuses
- **`--crawl`** — reads a saved URL list and prints the contents of each page
- **Sequential** — brute-force first, then crawl the saved list; no races
- **Minimal deps** — Python 3.8+ and [`requests`](https://pypi.org/project/requests/), that's it

## 🧰 Tools

| File                               | Role                                                                                 | How to run                   |
| ---------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------- |
| [`brutescrape.py`](brutescrape.py) | Main entry point — brute-forces directories from a wordlist, optionally saves/crawls | `python brutescrape.py`      |
| [`helpers.py`](helpers.py)         | Status-code validation, response matching, and the crawler                           | imported by `brutescrape.py` |

## 🚀 Quick Start

```bash
git clone https://github.com/Utkarsh464/dir-brute.git
cd dir-brute
pip install -r requirements.txt
```

## 🛠️ Usage

> All examples assume a wordlist with one path per line — e.g. `admin`, `login`, `api`.

### Brute-force directories

```bash
python brutescrape.py http://example.com/ wordlist.txt
# 200 http://example.com/admin
# 301 http://example.com/login
# 200 http://example.com/api
# 404 http://example.com/nothere
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
python brutescrape.py http://example.com/ wordlist.txt -R
# 200 http://example.com/admin
# 200 http://example.com/admin/users
# 200 http://example.com/login
# ...
```

Every `200` URL gets re-scanned against the wordlist, one level deep, so you can find nested directories too. Note: the recursive pass currently ignores `-f` and `-s` — it always runs unfiltered.

### Crawl saved URLs

```bash
python brutescrape.py http://example.com/ wordlist.txt --crawl live_urls.txt
# the content of http://example.com/admin
# <!doctype html>
# <html>...
```

### Options

| Argument               | Description                                                   |
| ---------------------- | ------------------------------------------------------------- |
| `url`                  | Target base URL, e.g. `http://example.com/`                   |
| `wordlist_path`        | Path to the wordlist — one directory to check per line        |
| `-f, --filter CODE`    | Only print responses matching this status code                |
| `-R, --recursion`      | Re-scan every `200` URL found, one level deep                 |
| `-s, --file_name FILE` | Save matching URLs to `FILE`, one per line                    |
| `--crawl FILE`         | Read URLs from a file saved with `-s` and print page contents |

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
