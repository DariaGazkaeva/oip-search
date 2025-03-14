from collections import deque
import sys
import logging
from typing import Optional, Tuple, List, Set
import time

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, unquote, urlparse


DEFAULT_STARTING_URL = "https://ru.wikipedia.org/wiki/Матроид"
DEFAULT_MAX_PAGES = 100
SLEEP_TIME = 2

logger = logging.getLogger("__main__")


def get_page_content(url: str) -> Optional[str]:
    logger.info("Requesting %s", url)
    response = requests.get(url)
    if not response.ok:
        logger.warning("Could not make request to %s", url)
        return None
    return response.text


def parse_webpage_content(content: str, original_url: str) -> Tuple[str, Set[str]]:
    soup = BeautifulSoup(content, "html.parser")

    body = soup.find(
        "div",
        attrs={"id": "bodyContent"},
    )
    # Remove edit sections (ms-editsection)
    for section in body.find_all("span", attrs={"class": "ms-editsection"}):
        section.decompose()

    # Remove edit sections (mw-editsection)
    for section in body.find_all("span", attrs={"class": "mw-editsection"}):
        section.decompose()

    # Remove category links
    catlinks = body.find("div", attrs={"id": "catlinks"})
    if catlinks is not None:
        catlinks.decompose()

    # Remove contents table
    contents_table = body.find("div", attrs={"id": "toc"})
    if contents_table is not None:
        contents_table.decompose()

    # Remove JavaScript (<script> tags)
    for script in body.find_all("script"):
        script.decompose()

    # Remove CSS (<style> tags and style attributes)
    for style in body.find_all("style"):
        style.decompose()

    for tag in body.find_all(style=True):
        del tag["style"]

    # Remove Images (<img> tags)
    for img in body.find_all("img"):
        img.decompose()

    # Find links to same URL
    links = set()
    for anchor in body.find_all("a", href=True):
        href = anchor["href"]
        parsed_url = urlparse(href)
        # 1. Only relative paths
        # 2. No fragments of current page
        # 3. No action
        # 4. If additional links (служебные)
        # 5. If file link
        unquoted_path = unquote(parsed_url.path)
        if (
            parsed_url.netloc != ""
            or (href.startswith("#"))
            or "action" in parsed_url.query
            or unquoted_path == "/w/index.php"
            or unquoted_path == "/w/index.php/"
            or unquoted_path.startswith("/wiki/Служебная:")
            or unquoted_path.startswith("/wiki/Шаблон:")
            or (anchor.has_attr("class") and "mw-file-description" in anchor["class"])
        ):
            continue
        # Join the relative URL with the base URL
        full_url = urljoin(original_url, anchor["href"])

        links.add(full_url)

    return body.prettify(), links


def save_webpage(content: str, page_dir: str, page_id: int) -> None:
    file_path = f"{page_dir}/{page_id}.html"
    with open(file_path, "w+") as f:
        f.write(content)


def save_index(index: List[str]) -> None:
    with open("index.txt", "w+") as f:
        for i, url in enumerate(index):
            f.write(f"{i} {url}\n")


def main():
    logging.basicConfig(level=logging.INFO)
    starting_url = DEFAULT_STARTING_URL
    max_pages = DEFAULT_MAX_PAGES

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        starting_url = sys.argv[1]
    elif len(sys.argv) == 3:
        if sys.argv[1] != "-":
            starting_url = sys.argv[1]
        max_pages = int(sys.argv[2])
    else:
        logger.error("Error! You can specify exactly one argument - starting URL")
        exit(1)
    logger.info("Starting URL: %s", unquote(starting_url))
    logger.info("Max page: %d", max_pages)

    urls = deque()
    urls.append(starting_url)

    # page urls
    index: List[str] = []
    visited_urls = set()

    while urls and len(index) < max_pages:
        url = unquote(urls.popleft())
        if url in visited_urls:
            continue
        content = get_page_content(url)
        if content is None:
            continue
        text, new_urls = parse_webpage_content(content, original_url=starting_url)
        visited_urls.add(url)

        urls.extend(new_urls)

        page_id = len(index)
        save_webpage(text, "pages", page_id=page_id)
        index.append(url)

        logger.info("%d) Parsed %s; sleeping %d seconds", page_id, url, SLEEP_TIME)
        time.sleep(SLEEP_TIME)

    save_index(index)
    logger.info("Saved index. Finished crawling")


if __name__ == "__main__":
    main()
