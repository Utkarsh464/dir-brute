from bs4 import BeautifulSoup


def crawl(name, html):
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            print(f"link in {name}: {href}")
