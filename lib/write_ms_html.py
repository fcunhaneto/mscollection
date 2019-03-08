import os
from unicodedata import normalize

from PyQt5.QtWidgets import QApplication

from sqlalchemy import or_

from db.db_model import Media, MovieCast, SeriesCast


# Write Html Movies Series
def write_html(session, ms, type):
    """
    Writing html page for view movie or series.

    :param session: Sqlalchemy orm session.
    :param ms: The object that can be movie or series.
    :param type: String that identifies the type of obj whether movie or series.
    :return: The view url.
    """
    QApplication.processEvents()
    view_css = os.path.abspath('styles/views.css')

    year = ''
    media = ''

    html_summary = ''
    html_categories = ''
    html_actors = ''
    html_director_creator = ''
    html_original_name = ''

    if ms.year:
        year = ms.year
    if ms.media_id:
        query = session.query(Media).filter(Media.id == ms.media_id).first()
        media = query.name
    if ms.summary:
        html_summary = '\t\t\t<p class="summary">' + ms.summary + '</p>\n'
    if ms.categories:
        categories = ''
        total = len(ms.categories)
        if total == 1:
            categories = ms.categories[0].category.name
        elif total == 2:
            categories = ms.categories[0].category.name + ', ' + \
                         ms.categories[1].category.name
        html_categories = '<p class="fields"><span>Categorias:&nbsp;&nbsp;' \
                          '</span>'+ categories + '</p>\n'

    if type == 'movie':
        if ms.movie_cast:
            actors_list = []
            val = session.query(MovieCast). \
                filter(MovieCast.movie_id == ms.id,
                       MovieCast.star.is_(True)).all()

            if len(val) != 0:
                for a in ms.movie_cast:
                    if a.star:
                        actors_list.append([a.cast.actors.name,
                                            a.cast.characters.name])
            else:
                actors = session.query(MovieCast). \
                    filter(MovieCast.movie_id == ms.id, MovieCast.order < 4).\
                    all()

                for a in actors:
                    actors_list.append([a.cast.actors.name,
                                        a.cast.characters.name])

            html_actors = '<p class="fields">' \
                          '<span>Elenco:&nbsp;&nbsp;</span></p>\n<ul>'

            for a, c in actors_list:
                html_actors += '<li>' + a + ':  ' + c + '</li>\n'

            html_actors += '</ul>'

    if type == 'series':
        if ms.series_cast:
            actors_list = []
            val = session.query(SeriesCast).\
                filter(SeriesCast.series_id == ms.id,
                       SeriesCast.star.is_(True)).all()

            if len(val) != 0:
                for a in ms.series_cast:
                    if a.star:
                        actors_list.append([a.cast.actors.name,
                                            a.cast.characters.name])
            else:
                actors = session.query(SeriesCast).\
                    filter(SeriesCast.series_id == ms.id, SeriesCast.order < 4)\
                    .all()
                for a in actors:
                    actors_list.append([a.cast.actors.name,
                                        a.cast.characters.name])

            html_actors = '<p class="fields">' \
                          '<span>Elenco:&nbsp;&nbsp;</span></p>\n<ul>'

            for a, c in actors_list:
                html_actors += '<li>' + a + ' / ' + c + '</li>\n'

            html_actors += '</ul>'

    if type == 'movie':
        director = ''
        if ms.directors:
            total = len(ms.directors)
            end = total - 1
            for i in range(total):
                if i < end:
                    director += ms.directors[i].director.name + ', '
                    continue
                director += ms.directors[i].director.name

            if total == 1:
                html_director_creator = '\t\t\t<p class="fields"><span>' \
                                        'Diretor:&nbsp;&nbsp;</span>' + \
                                        director + '</p>\n'
            elif total > 1:
                html_director_creator = '\t\t\t<p class="fields"><span>' \
                                        'Diretores:&nbsp;&nbsp;</span>' \
                                        + director + '</p>\n'
    if type == 'series':
        creator = ''
        if ms.creators:
            total = len(ms.creators)
            end = total - 1
            for i in range(total):
                if i < end:
                    creator += ms.creators[i].creator.name + ', '
                    continue
                creator += ms.creators[i].creator.name

            if total == 1:
                html_director_creator = '\t\t\t<p class="fields">' \
                                        '<span>Criador:&nbsp;&nbsp;' \
                                        '</span>' + creator + '</p>\n'
            elif total > 1:
                html_director_creator = '\t\t\t<p class="fields">' \
                                        '<span">' \
                                        'Criadores:&nbsp;&nbsp;' \
                                        '</span>' + creator + '</p>\n'

    if ms.original_name:
        html_original_name = '\t\t\t<p class="fields"><span>' \
                             'Título Original:&nbsp;&nbsp;</span>' +  \
                             ms.original_name + '</p>\n'

    html_ini = '' \
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN http://www.w3.org/TR/html4/loose.dtd">\n' \
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-br" lang="pt-br">\n' \
        '<head>\n' \
        '\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n' \
        '\t<link rel="stylesheet" type="text/css" href="' + view_css + '" media="all">\n' \
        '</head>\n' \
        '<body>\n' \
        '\t<div id="wrap">\n' \
        '\t\t<h2>' + ms.name + '</h2>\n' \
        '\t\t<p class="year"><span>Ano:&nbsp;&nbsp;</span>' + year + \
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>' \
        'Mídia:&nbsp;&nbsp;</span>' + media + '</p>\n' \
        '\t\t<div class="poster">\n' \
        '\t\t\t<img src="' + ms.poster + '" >\n' \
        '\t\t</div>\n' \
        '\t\t<div class="movie">\n' \


    html_end = '' \
        '\t\t</div>\n' \
        '\t</div>\n' \
        '</body>\n' \
        '</html>\n'

    html = html_ini + html_summary + html_categories + html_director_creator + \
           html_original_name + html_actors + html_end

    title = ms.name.lower()
    char = [' ', '.', '/', '\\']
    for c in char:
        title = title.replace(c, '_')
    title = normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
    path = os.getcwd()
    view = path + '/views/' + title + '.html'

    with open(view, 'w') as f:
        f.write(html)

    url = 'file://' + view
    return url