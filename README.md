<div align="center">

# **dir-brute**

### A threaded directory brute-forcer & crawler

**`probe → collect → crawl`** — throw a wordlist at a target URL, keep the live hits, then read back what you found.

<br>

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)
[![requests ≥ 2.28](https://img.shields.io/badge/requests-%3E%3D%202.28-0A7EA4)](https://pypi.org/project/requests/)
[![for authorized testing only](https://img.shields.io/badge/for-authorized%20testing-6f42c1)](#disclaimer)

</div>

**dir-brute** is a small security tool built while learning how directory enumeration works. It brute-forces hidden paths on a target from a wordlist, prints every response that isn't a `404`, and — with a single flag — either saves the live (HTTP `200`) URLs to a file or crawls them to dump page contents.

---

## How it works

```
         wordlist.txt
              │
              ▼
      ┌─────────────────┐
      │  brutescrape.py │   prints: status + URL for every non-404 hit
      └────────┬────────┘
               │
        ┌──────┴──────┐
   --save            --crawl
        │              │
        ▼              ▼
  live_urls.txt   page contents
```

## ✨ Features

- **Threaded** — brute-forcing and crawling run side-by-side in separate threads
- **404-smart** — dead ends are skipped; everything else prints as `status URL`
- **`--save`** — writes every HTTP `200` URL to a file, one per line
- **`--crawl`** — reads a saved URL list and prints the contents of each page
- **Minimal deps** — Python 3.8+ and [`requests`](https://pypi.org/project/requests/), that's it

## 🧰 Tools

| File                               | Role                                                                                    | How to run                   |
| ---------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------- |
| [`brutescrape.py`](brutescrape.py) | Main entry point — brute-forces directories from a wordlist, optionally saves live URLs | `python brutescrape.py`      |
| [`crawl.py`](crawl.py)             | Crawler module — reads a saved URL file and prints each page's content                  | imported by `brutescrape.py` |

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
# ...
```

### Save live URLs

```bash
python brutescrape.py http://example.com/ wordlist.txt --save live_urls.txt
# all live urls are saved in live_urls.txt
```

Only HTTP `200` responses make it into the file — one URL per line, ready to crawl.

### Crawl saved URLs

```bash
python brutescrape.py http://example.com/ wordlist.txt --crawl live_urls.txt
# content of this url : http://example.com/admin
# <!doctype html>
# <html>...
```

### Options

| Argument        | Description                                                          |
| --------------- | -------------------------------------------------------------------- |
| `url`           | Target base URL, e.g. `http://example.com/`                          |
| `wordlist_path` | Path to the wordlist — one directory to check per line               |
| `--save FILE`   | Save live (HTTP 200) URLs to `FILE`, one per line                    |
| `--crawl FILE`  | Crawl URLs from a file created with `--save` and print page contents |

## 📦 Requirements

- **Python 3.8+**
- [`requests`](https://pypi.org/project/requests/) `>= 2.28` — pinned in [`requirements.txt`](requirements.txt)

## ⚠️ Disclaimer

These tools are provided **for educational and authorized testing purposes only**. Unauthorized use of security tools against systems you do not own or have explicit permission to test is illegal. The author is not responsible for any misuse of these tools.

## 📄 License

Released under the [MIT License](LICENSE).

<br>

<div align="center">

**Utkarsh S.** — Cybersecurity Student

[GitHub](https://github.com/Utkarsh464) · [LinkedIn](https://linkedin.com/in/utkarsh-solanki-337806252)

</div>
