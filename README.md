# dir-brute

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

A directory brute-forcer and crawler built with Python — discover hidden paths on a target from a wordlist, save live URLs, and crawl their contents.

Designed for learning, lab practice, and authorized security testing only.

## Tools

| File                               | Description                                                                                         |
| ---------------------------------- | --------------------------------------------------------------------------------------------------- |
| [`brutescrape.py`](brutescrape.py) | Main entry point — brute-forces directories from a wordlist, optionally saves live (HTTP 200) URLs. |
| [`crawl.py`](crawl.py)             | Crawler — fetches and prints the content of saved live URLs.                                        |

## Installation

```bash
git clone https://github.com/Utkarsh464/dir-brute.git
cd dir-brute
pip install -r requirements.txt
```

## Usage

### Brute-force directories

```bash
python brutescrape.py http://example.com/ wordlist.txt
# 200 http://example.com/admin
# ...

# save live (HTTP 200) URLs to a file
python brutescrape.py http://example.com/ wordlist.txt --save live_urls.txt
# all live urls are saved in live_urls.txt
```

### Crawl saved live URLs

```bash
python brutescrape.py http://example.com/ wordlist.txt --crawl live_urls.txt
# content of this url : http://example.com/admin
# <html>...
```

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/) (included in `requirements.txt`)

## Disclaimer

These tools are provided **for educational and authorized testing purposes only**. Unauthorized use of security tools against systems you do not own or have explicit permission to test is illegal. The author is not responsible for any misuse of these tools.

## License

Licensed under the [MIT License](LICENSE).

---

**Utkarsh S.** — Cybersecurity Student
