from typing import Optional

from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocketEntry:
    case_signature: str
    date_time: datetime
    department: str
    room: str
    chair: str
    lay_judges: list[str]


def get_page(url) -> Optional[BeautifulSoup]:
    response = requests.get(url, allow_redirects=False)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def scrape_page(page: BeautifulSoup) -> DocketEntry:
    description = page.find('dl', class_='case-description-list')
    properties = [dd.text for dd in description.find_all('dd')]
    if len(properties) == 6:
        properties.append("")
    case_signature, department, date, room, time, chair, lay_judges = properties
    date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
    lay_judges = [] if lay_judges == "" else lay_judges.split(', ')
    return DocketEntry(case_signature, date_time, department, room, chair, lay_judges)


def scrape_all(main_url) -> list[DocketEntry]:
    index = 1
    pages = []
    while page := get_page(f'{main_url}wokanda,{index}'):
        try:
            pages.append(scrape_page(page))
        except Exception as e:
            print(f'Error on page {index}: {e}')
        index += 1
    return pages


def main():
    main_url = 'https://lublin.sa.gov.pl/'
    entries = scrape_all(main_url)
    print("\n".join(map(str, entries)))


if __name__ == '__main__':
    main()
