import requests
from bs4 import BeautifulSoup


def fetch_metadata_from_page(url: str) -> dict:
    """
    Skeleton: fetch page & parse site-specific metadata.

    Implement site-specific selectors here.

    Return a dictionary containing:
      - title
      - slug
      - ani_id
      - episodes
      - default_quality
      - source
      - season
    """

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Example placeholder selector
    title_node = soup.select_one("h1")
    title = title_node.get_text(strip=True) if title_node else ""

    return {
        "title": title,
        "slug": "",
        "ani_id": "",
        "episodes": None,
        "default_quality": "",
        "source": url,
        "season": 1,
    }