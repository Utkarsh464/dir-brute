from bs4 import BeautifulSoup


def main_crawl(r,text=None):
    soup = BeautifulSoup(r.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            print(f"link in {r.url}: {href}")
        if text:
            all_text = soup.get_text(" ", strip=True)
            print(f"text content of {r.url} , {all_text} ")
