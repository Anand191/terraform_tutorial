from typing import Dict

import bs4
import requests


def parse_wiki(URL: str) -> Dict:
    response = requests.get(url=URL)
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    parsed = {}
    p_counter = 0
    all_titles = soup.find_all("h2")[1:]
    for title in all_titles:
        header = title.span["id"].strip()
        textContent = {}
        for para in title.find_next_siblings("p"):
            if header in para.find_previous_siblings("h2")[0].span["id"].strip():
                textContent[p_counter] = para.text.strip()
                p_counter += 1
        if textContent:
            parsed[header] = textContent
    return parsed
