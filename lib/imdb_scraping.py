import os
import re

from urllib.request import urlopen
from unicodedata import normalize

from bs4 import BeautifulSoup

import texts


class ImdbScraping:
    def __init__(self, url, obj):
        """
        This class scrapping series information from site IMDB.
        (https://www.imdb.com/) base in given url.

        :param url: Url site IMDB where the info are.
        :param obj: Type object, movie or series, are scrapping.
        """
        self.http = urlopen(url)
        self.soup = BeautifulSoup(self.http, 'lxml')
        self.obj = obj
        self.result = {
            'title': None,
            'original_title': None,
            'year': None,
            'time': None,
            'poster': None,
            'summary': None,
            'categories': None,
            'director_creator': None,
            'cast': None
        }

    def get_values(self):
        # Title
        get_title = self.soup.find('div', {'class': 'title_wrapper'})
        if get_title:
            if self.obj == 'movie':
                self.result['title'] = get_title.h1.text[:-7].strip()
            elif self.obj == 'series':
                self.result['title'] = get_title.h1.text.strip()

        # Original Title
        get_original_title = get_title.find('div', {'class': 'originalTitle'})

        if get_original_title:
            original_title_text = get_original_title.text.split(' ')

            original_title = ''
            for o in original_title_text[:-2]:
                original_title = original_title + ' ' + o

            self.result['original_title'] = original_title.strip()

        # Year
        get_date = get_title.find('a', {'title': 'See more release dates'})
        if get_date:
            date = get_date.text.split()
            if self.obj == 'movie':
                self.result['year'] = date[2]
            elif self.obj == 'series':
                self.result['year'] = date[2][1:5]

        # Time
        get_time = self.soup.find('div', {'class': 'subtext'}).time.text
        self.result['time'] = get_time.strip()

        # Poster
        poster = self.soup.find('div', {'class': 'poster'}).a.img
        if poster:
            url = poster['src']
            title = poster['title'].lower()
            char = [' ', '.', '/', '\\']
            for c in char:
                title = title.replace(c, '_')
            title = normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
            path = os.getcwd()
            poster = path + '/poster/' + title + '.jpg'
            with open(poster, 'wb') as f:
                f.write(urlopen(url).read())

            self.result['poster'] = poster

        # Summary
        get_summary = self.soup.find('div', {'class': 'summary_text'})
        if get_summary:
            self.result['summary'] = get_summary.text.strip()

        # Categories
        a_categories = get_title.findAll('a')
        if a_categories:
            categories = []

            for c in a_categories:
                if '/search/title?genres' in c['href']:
                    imdb_category = c.text
                    categories.append(texts.imdb_categories[imdb_category])

            self.result['categories'] = categories

        # Director
        get_credits = self.soup.find('div', {
            'class': 'credit_summary_item'
        })
        director_creator = get_credits.h4
        str_director_creator = ''
        if director_creator:
            str_director_creator = director_creator.text.strip()

        if str_director_creator == 'Director:':
            director_find = self.soup.find(
                'h4', {'class': 'inline'}, text=re.compile('Director')). \
                find_next_sibling("a")
            if director_find:
                self.result['director_creator'] = director_find.text.strip()
        elif str_director_creator == 'Directors:':
            links = get_credits.findAll('a')
            director = links[0].text
            self.result['director_creator'] = director
        elif str_director_creator == 'Creator:':
            creator_find = self.soup.find(
                'h4', {'class': 'inline'}, text=re.compile('Creator')). \
                find_next_sibling("a")
            if creator_find:
                self.result['director_creator'] = creator_find.text
        elif str_director_creator == 'Creators:':
            creator_find = self.soup.find('div',
                                          {'class': 'credit_summary_item'})
            links = creator_find.findAll('a')
            creator = links[0].text

            self.result['director_creator'] = creator

        # Cast
        table = self.soup.find('table', {'class': 'cast_list'})
        if table:
            rows = table.findAll('tr')
            if rows:
                names = []
                for row in rows:
                    col = row.td.next_siblings
                    for c in col:
                        t = c.find('a')
                        if t and not isinstance(t, int):
                            s = t.text.strip()
                            names.append(s)
                actor_character = []
                cast = []
                for n in range(len(names)):
                    num = n % 2
                    if num == 0:
                        actor_character.append(names.pop(0))
                    else:
                        actor_character.append(names.pop(0))
                        cast.append(actor_character)
                        actor_character = []

                self.result['cast'] = cast

        return self.result
