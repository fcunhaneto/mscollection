import os
import re
from urllib.request import urlopen
from unicodedata import normalize
from bs4 import BeautifulSoup


class AdoroCinemaSeriesScraping:
    def __init__(self, url):
        """
        This class scrapping series information from site Adoro Cinema
        (http://www.adorocinema.com/) base in given url.

        :param url: Url site Adoro Cinema where the info of the series are.
        """
        self.url = url
        self.http = urlopen(self.url)
        self.soup = BeautifulSoup(self.http, 'lxml')

        self.result = {
            'title': None,
            'original_title': None,
            'year': None,
            'poster': None,
            'summary': None,
            'categories': None,
            'director_creator': None,
            'cast': None
        }

    def get_values(self):
        """
        uses BeautifulSoup to extract the series info
        :return: dict who have the series info
        """
        # Title
        if self.soup.find('div', {'class': 'titlebar-title'}):
            self.result['title'] = self.soup.\
                find('div', {'class': 'titlebar-title'}).text

        # Year Categories
        if self.soup.find('div', {'class': 'meta-body-info'}):
            try:
                cats = self.soup.find('div', {'class': 'meta-body-info'})
                year = cats.text.split()

                if year[0] == 'Desde':
                    self.result['year'] = year[1]
                else:
                    self.result['year'] = year[0]


                categories = []
                for d in cats.children:
                    if d.name == 'span' and d.text != '/':
                        categories.append(d.text)

                self.result['categories'] = categories
            except AttributeError:
                self.result['year'] = ''
                self.result['categories'] = ''

        # Creator
        if self.soup.find('div', {'class': 'meta-body-direction'}):
            try:
                self.result['director_creator'] = self.soup.\
                    find('div', {'class': 'meta-body-direction'}).a.text
            except AttributeError:
                self.result['director_creator'] = ''

        if self.soup.find('div', {'class': 'content-txt'}):
            try:
                self.result['summary'] = self.soup.\
                    find('div', {'class': 'content-txt'}).text.strip()
            except AttributeError:
                self.result['summary'] = ''

        # Poster
        if self.soup.find('div', {'class': 'entity-card'}):
            thumbnail = self.soup.find('div', {'class': 'entity-card'}).find('img')
            thumbnail_url = thumbnail['src']

            name = self.result['title'].lower()
            char = [' ', '.', '/', '\\']

            file = ''
            for c in char:
                file = name.replace(c, '_')

            title = normalize('NFKD', file).encode('ASCII', 'ignore').decode(
                'ASCII')

            path = os.getcwd()
            poster = path + '/poster/' + title + '.jpg'

            with open(poster, 'wb') as f:
                f.write(urlopen(thumbnail_url).read())

            self.result['poster'] = poster

        # Cast
        if self.soup.findAll('div', {'class': 'person-card'}):
            names = self.soup.findAll('div', {'class': 'person-card'})

            casts = []
            for n in names:
                cast = []
                cast.append(n.a.text.strip())
                if n.findChildren('div', {'class': 'meta-sub'}):
                    cast.append(n.findChildren('div', {'class': 'meta-sub'})[0].
                                text.strip().replace('Personagem : ', ''))
                else:
                    cast.append('')

                casts.append(cast)

            self.result['cast'] = casts

        return self.result


