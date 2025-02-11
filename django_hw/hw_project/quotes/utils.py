import requests
from bs4 import  BeautifulSoup
from pymongo import MongoClient
from .models import Quote, Author, Tag

from hw_project.settings import MONGO_URI, MONGO_DB_NAME


def get_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db


def scrape_and_save_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Failed to fetch data. Status code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')

    quotes_data = soup.select('.quote')
    for quote_item in quotes_data:
        text = quote_item.select_one('.text').get_text(strip=True)
        author_name = quote_item.select_one('.author').get_text(strip=True)
        tag_elements = quote_item.select('.tag')

        author, created = Author.objects.get_or_create(fullname=author_name)

        quote, created = Quote.objects.get_or_create(quote=text, author=author)

        for tag_elem in tag_elements:
            tag_name = tag_elem.get_text(strip=True)
            tag, created = Tag.objects.get_or_create(name=tag_name)
            quote.tags.add(tag)

    return "Data successfully scraped and saved!"