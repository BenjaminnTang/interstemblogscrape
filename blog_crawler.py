from collections import defaultdict
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


class BlogCrawler:

    def __init__(self, *args, **kwargs):
        self.BASE_URL = 'https://interstem.us'
        self.articles_by_author = defaultdict(list)
        self.latest_article = None

    def _add_article(self, article):
        """
        Takes a dictionary representation of an article and adds to self.articles_by_author if
        no other articles with the same author and title are already stored.

        Also checks this article against self.latest_article and replaces it if this article
        is more recent.
        """

        author_articles = self.articles_by_author[article['author']]
        title_match = False
        for existing_article in author_articles:
            if article['title'] == existing_article['title']:
                title_match = True
                break

        if not title_match:
            self.articles_by_author[article['author']].append(article)

            if not self.latest_article or article['date_obj'] > self.latest_article['date_obj']:
                self.latest_article = article

    def _extract_articles_from_soup(self, soup):
        """Parses the soup to look for each article and save title, author, date, description, and url"""

        cards = soup.find_all('div', {'class': 'card'})
        for card in cards:
            author = card.find('a', {'class': 'author'}).text.strip()
            raw_date = card.find('span', {'class': 'date'}).text.strip()
            description = card.find('p', {'class': 'description'}).text.strip().replace('&nbsp', '')
            title = card.find('h1', {'class': 'title'}).text.strip()

            article = {
                'author': author,
                'raw_date': raw_date,
                'date_obj': datetime.strptime(raw_date, "%B %d, %Y").date(),
                'title': title,
                'description': description
            }

            href = None
            try:
                href = urljoin(self.BASE_URL, card.get('onclick').split("'")[1])
            except Exception:
                pass

            if href:
                article['url'] = href

            self._add_article(article)

    def crawl(self):
        """Hits interstem blog page and crawls links to depth 1 looking for articles"""

        print(f'{datetime.now()}: Crawling for new articles...')

        self.articles_by_author = defaultdict(list)
        self.latest_article = None

        start = f'{self.BASE_URL}/blogs/blogs.html'

        resp = requests.get(start)
        if resp.ok:
            soup = BeautifulSoup(resp.content, 'html.parser')
            self._extract_articles_from_soup(soup)
            urls = {urljoin(self.BASE_URL, x.get('href')) for x in soup.find_all('a')}

            for url in urls:
                if not url or url == '#':
                    continue

                resp = requests.get(url)
                if not resp.ok:
                    continue

                soup = BeautifulSoup(resp.content, 'html.parser')
                self._extract_articles_from_soup(soup)
        else:
            raise Exception(f'Failed to connect to {self.BASE_URL}')

    def get_articles(self, author=None):
        """Gets articles filtered by author name if provided, otherwise returns all"""

        if not self.articles_by_author:
            self.crawl()

        articles = []

        if author:
            all_authors = set(self.articles_by_author.keys())
            matching_authors = [a for a in all_authors if author.lower() in a.lower()]

            for a in matching_authors:
                articles += self.articles_by_author[a]
        else:
            for k, v in self.articles_by_author.items():
                articles += v

        return articles

    def get_latest_article(self):

        if not self.articles_by_author:
            self.crawl()

        return self.latest_article

    @staticmethod
    def format_article(article):
        """Takes an article in the form of a dictionary and formats it nicely for discord messaging"""

        out = '```'
        out += f'Title: {article["title"]}\n'
        out += f'Author: {article["author"]}\n'
        out += f'Date: {article["raw_date"]}\n'
        out += f'Description: {article["description"]}'
        out += '```'

        return out
