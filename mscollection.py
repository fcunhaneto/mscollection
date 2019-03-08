#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
#!/home/francisco/Projects/Pycharm/mscollection_qt12/venv/bin/python
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QMenu, QMenuBar, \
    QStatusBar, QAction, QDesktopWidget, QApplication

import texts

from subwindows.insert.insert_movie import InsertMovie
from subwindows.insert.insert_series import InsertSeries
from subwindows.insert.insert_season import InsertSeason

from subwindows.edit.edit_movie import EditMovie
from subwindows.edit.edit_series import EditSeries
from subwindows.edit.edit_season import EditSeason
from subwindows.edit.edit_cast import EditCast
from subwindows.edit.edit_others import  EditOthers
from subwindows.edit.edit_director import EditDirector
from subwindows.edit.edit_creator import EditCreator
from subwindows.edit.edit_season_cast import EditSeasonCast

from subwindows.delete_orphans.delete_orphans_cast import DeleteOrphansCast
from subwindows.delete_orphans.delete_orphans_category import \
    DeleteOrphansCategory
from subwindows.delete_orphans.delete_orphans_director import \
    DeleteOrphansDirector
from subwindows.delete_orphans.delete_orphans_creator import \
    DeleteOrphansCreator
from subwindows.delete_orphans.delete_orphans_actor import DeleteOrphansActor
from subwindows.delete_orphans.delete_orphans_character import \
    DeleteOrphansCharacter
from subwindows.delete_orphans.delete_orphans_box import DeleteOrphansBox
from subwindows.delete_orphans.delete_orphans_media import DeleteOrphansMedia

from subwindows.search.search_movie_title import SearchMovieTitle
from subwindows.search.search_series_title import SearchSeriesTitle
from subwindows.search.view_select_title import ViewSelectTitle

from subwindows.search.search_category import SearchCategory
from subwindows.search.search_director_creator import SearchDirectorCreator
from subwindows.search.search_actor_character import SearchActorCharacter
from subwindows.search.search_movie_box_keyword import SearchBoxKeyword
from subwindows.search.search_movie_media_year import SearchMovieMediaYear
from subwindows.search.search_series_key_media_year import \
    SearchSeriesKeyMediaYear
from subwindows.search.search_episodes import SearchEpisodes

from subwindows.search.views_help import ViewsHelp


class MSCollection(QMainWindow):
    """
    Class of the main window and that also manages the display of all other
    windows.
    """
    def __init__(self):
        super(MSCollection, self).__init__()

        css = 'styles/style.qss'
        with open(css, 'r') as fh:
            self.setStyleSheet(fh.read())

        self.setWindowTitle(texts.main_widow)
        screen = QDesktopWidget().screenGeometry()
        s_width = screen.width()
        s_heigth = screen.height()
        x = int(0.10 * s_width)
        y = int(0.10 * s_heigth)
        width = int(0.8 * s_width)
        height = int(0.8 * s_heigth)

        self.setGeometry(x, y, width, height)

        self.mdi_area = QMdiArea()
        # self.mdi_area.setGeometry(0, 0, 1022, 722)
        brush = QBrush(QColor(232, 232, 232))
        brush.setStyle(Qt.SolidPattern)
        self.mdi_area.setBackground(brush)

        self.setCentralWidget(self.mdi_area)
        self.menubar = QMenuBar(self)

        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        # Menu and Submenu
        self.menu_insert = QMenu(self.menubar)
        self.menu_insert.setTitle(texts.insert)

        self.menu_edit = QMenu(self.menubar)
        self.menu_edit.setTitle(texts.edit)
        self.menu_edit_movie_others = QMenu(self.menu_edit)
        self.menu_edit_movie_others.setTitle(texts.menu_movie_others)
        self.menu_edit_series_others = QMenu(self.menu_edit)
        self.menu_edit_series_others.setTitle(texts.menu_series_others)
        self.menu_edit_season = QMenu(self.menu_edit)
        self.menu_edit_season.setTitle(texts.season_p)
        self.menu_edit_general = QMenu(self.menu_insert)
        self.menu_edit_general.setTitle(texts.general)
        self.menu_delete_orphans = QMenu(texts.delete_orphans)

        self.menu_search = QMenu(self.menubar)
        self.menu_search.setTitle(texts.search)
        self.menu_search_movies = QMenu(self.menu_search)
        self.menu_search_movies.setTitle(texts.movie_p)
        self.menu_search_series = QMenu(self.menu_search)
        self.menu_search_series.setTitle(texts.series_p)

        # Actions Insert
        self.action_insert_movie = QAction(
            texts.movie_p, self, triggered=self.insert_movie)
        self.action_insert_series = QAction(
            texts.series_p, self, triggered=self.insert_series)
        self.action_insert_season = QAction(
            texts.season_p, self, triggered=self.insert_season)

        # AddAction Insert
        self.menu_insert.addAction(self.action_insert_movie)
        self.menu_insert.addAction(self.action_insert_series)
        self.menu_insert.addAction(self.action_insert_season)

        # Actions Edit
        self.action_edit_movie = QAction(
            texts.movie_p, self, triggered=self.edit_movie)
        self.action_edit_series = QAction(
            texts.series_p, self, triggered=self.edit_series)
        text = texts.season_p + '/' + texts.episode_p
        self.action_edit_season = QAction(
            text, self, triggered=self.edit_season)
        self.action_edit_movie_cast = QAction(
            texts.cast_s, self, triggered=self.edit_movie_cast)
        self.action_edit_series_cast = QAction(
            texts.cast_s, self, triggered=self.edit_series_cast)
        self.action_edit_season_cast = QAction(
            texts.cast_s, self, triggered=self.edit_season_cast)
        self.action_edit_director = QAction(texts.director_s, self,
                                            triggered=self.edit_director)
        self.action_edit_creator = QAction(texts.creator_s, self,
                                           triggered=self.edit_creator)
        self.action_edit_box = QAction(texts.box, self)
        self.action_edit_box.triggered.connect(lambda: self.edit_others('box'))
        self.action_edit_category = QAction(texts.category_p, self)
        self.action_edit_category.triggered.connect(
            lambda: self.edit_others('category'))
        self.action_edit_media = QAction(texts.media_s, self)
        self.action_edit_media.triggered.connect(
            lambda: self.edit_others('media'))
        self.action_edit_actor = QAction(texts.actor_s, self)
        self.action_edit_actor.triggered.connect(
            lambda: self.edit_others('actor'))
        self.action_edit_character = QAction(texts.character_s, self)
        self.action_edit_character.triggered.connect(
            lambda: self.edit_others('character'))
        self.action_edit_keyword = QAction(texts.keyword, self)
        self.action_edit_keyword.triggered.connect(
            lambda: self.edit_others('keyword'))
        self.action_orphans_cast = QAction(
            texts.cast_s, self, triggered=self.delete_orphans_cast)
        self.action_orphans_actor = QAction(
            texts.actor_p, self, triggered=self.delete_orphans_actor)
        self.action_orphans_character = QAction(
            texts.character_p, self, triggered=self.delete_orphans_character)
        self.action_orphans_director = QAction(
            texts.director_p, self, triggered=self.delete_orphans_director)
        self.action_orphans_creator = QAction(
            texts.creator_p, self, triggered=self.delete_orphans_creator)
        self.action_orphans_category = QAction(
            texts.category_p, self, triggered=self.delete_orphans_category)
        self.action_orphans_box = QAction(
            texts.box, self, triggered=self.delete_orphans_box)
        self.action_orphans_media = QAction(
            texts.media_s, self, triggered=self.delete_orphans_media)

        # AddAction Edit
        self.menu_edit.addAction(self.action_edit_movie)
        self.menu_edit.addAction(self.action_edit_series)

        self.menu_edit_season.addAction(self.action_edit_season)
        self.menu_edit_season.addAction(self.action_edit_season_cast)

        self.menu_edit_movie_others.addAction(self.action_edit_movie_cast)
        self.menu_edit_movie_others.addAction(self.action_edit_director)
        self.menu_edit_movie_others.addAction(self.action_edit_box)
        self.menu_edit_series_others.addAction(self.action_edit_series_cast)
        self.menu_edit_series_others.addAction(self.action_edit_creator)

        self.menu_edit_general.addAction(self.action_edit_category)
        self.menu_edit_general.addAction(self.action_edit_media)
        self.menu_edit_general.addAction(self.action_edit_actor)
        self.menu_edit_general.addAction(self.action_edit_character)
        self.menu_edit_general.addAction(self.action_edit_keyword)

        self.menu_delete_orphans.addAction(self.action_orphans_cast)
        self.menu_delete_orphans.addAction(self.action_orphans_actor)
        self.menu_delete_orphans.addAction(self.action_orphans_character)
        self.menu_delete_orphans.addAction(self.action_orphans_director)
        self.menu_delete_orphans.addAction(self.action_orphans_creator)
        self.menu_delete_orphans.addAction(self.action_orphans_category)
        self.menu_delete_orphans.addAction(self.action_orphans_box)
        self.menu_delete_orphans.addAction(self.action_orphans_media)

        self.menu_edit.addAction(self.menu_edit_movie_others.menuAction())
        self.menu_edit.addAction(self.menu_edit_series_others.menuAction())
        self.menu_edit.addAction(self.menu_edit_season.menuAction())
        self.menu_edit.addAction(self.menu_edit_general.menuAction())
        self.menu_edit.addAction(self.menu_delete_orphans.menuAction())

        # Actions Search
        self.actions_search_movie_title = QAction(
            texts.title_s, self, triggered=self.search_movie_title)
        self.actions_search_movie_category = QAction(texts.category_s, self)
        self.actions_search_movie_category.triggered.\
            connect(lambda: self.search_category('movie'))
        self.actions_search_movie_director = QAction(texts.director_s, self)
        self.actions_search_movie_director.triggered.connect(
            lambda: self.search_dc('movie'))
        text = texts.box + '/' + texts.keyword
        self.actions_movie_box_key = QAction(
            text, self, triggered=self.search_movie_box_key)
        text = texts.media_s + '/' + texts.year_s
        self.actions_movie_media_year = QAction(
            text, self, triggered=self.search_movie_media_year)
        text = texts.actor_p + '/' + texts.character_p
        self.actions_search_movie_actor_character = QAction(text, self)
        self.actions_search_movie_actor_character.triggered.connect(
            lambda: self.search_actor_character('movie'))

        self.actions_search_series_title = QAction(
            texts.title_s, self, triggered=self.search_series_title)
        self.actions_search_series_category = QAction(texts.category_s, self)
        self.actions_search_series_category.triggered. \
            connect(lambda: self.search_category('series'))
        self.actions_search_series_creator = QAction(texts.creator_s, self)
        self.actions_search_series_creator.triggered.connect(
            lambda: self.search_dc('series'))
        text = texts.keyword + '/' + texts.media_s + '/' + texts.year_s
        self.actions_search_series_key_media_year = \
            QAction(text, self, triggered=self.search_series_key_media_year)
        text = texts.actor_p + '/' + texts.character_p
        self.actions_search_series_actor_character = QAction(text, self)
        self.actions_search_series_actor_character.triggered.connect(
            lambda: self.search_actor_character('series'))
        text = texts.season_p + '/' + texts.episode_p
        self.actions_search_episode = QAction(
            text, self, triggered=self.search_episode)

        # AddAction Search

        self.menu_search_movies.addAction(self.actions_search_movie_title)
        self.menu_search_movies.addAction(self.actions_search_movie_category)
        self.menu_search_movies.addAction(self.actions_search_movie_director)
        self.menu_search_movies.addAction(self.actions_movie_box_key)
        self.menu_search_movies.addAction(self.actions_movie_media_year)
        self.menu_search_movies.addAction(
            self.actions_search_movie_actor_character)

        self.menu_search_series.addAction(self.actions_search_series_title)
        self.menu_search_series.addAction(self.actions_search_series_category)
        self.menu_search_series.addAction(self.actions_search_series_creator)
        self.menu_search_series.addAction(
            self.actions_search_series_key_media_year)
        self.menu_search_series.addAction(
            self.actions_search_series_actor_character)
        self.menu_search_series.addAction(self.actions_search_episode)

        self.menu_search.addAction(self.menu_search_movies.menuAction())
        self.menu_search.addAction(self.menu_search_series.menuAction())

        # AddAction Menu
        self.menubar.addAction(self.menu_insert.menuAction())
        self.menubar.addAction(self.menu_edit.menuAction())
        self.menubar.addAction(self.menu_search.menuAction())

    """
    All methods below is for open subwindows
    """
    def insert_movie(self):
        subwindow = InsertMovie(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def insert_series(self):
        subwindow = InsertSeries(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def insert_season(self):
        subwindow = InsertSeason(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_movie(self):
        subwindow = EditMovie(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_series(self):
        subwindow = EditSeries(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_season(self):
        subwindow = EditSeason(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_movie_cast(self):
        subwindow = EditCast(self, 'movie')
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_series_cast(self):
        subwindow = EditCast(self, 'series')
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_season_cast(self):
        subwindow = EditSeasonCast(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_others(self, op):
        subwindow = EditOthers(self, op)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_director(self):
        subwindow = EditDirector(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def edit_creator(self):
        subwindow = EditCreator(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_cast(self):
        subwindow = DeleteOrphansCast(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_actor(self):
        subwindow = DeleteOrphansActor(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_character(self):
        subwindow = DeleteOrphansCharacter(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_director(self):
        subwindow = DeleteOrphansDirector(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_creator(self):
        subwindow = DeleteOrphansCreator(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_category(self):
        subwindow = DeleteOrphansCategory(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_box(self):
        subwindow = DeleteOrphansBox(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def delete_orphans_media(self):
        subwindow = DeleteOrphansMedia(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def views_help(self, url, title):
        subwindow = ViewsHelp(self, url, title)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def view_html(self, url, title):
        subwindow = ViewSelectTitle(url, title)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_movie_title(self):
        subwindow = SearchMovieTitle(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_series_title(self):
        subwindow = SearchSeriesTitle(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_category(self, type):
        subwindow = SearchCategory(self, type)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_dc(self, type):
        subwindow = SearchDirectorCreator(self, type)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_movie_box_key(self):
        subwindow = SearchBoxKeyword(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_movie_media_year(self):
        subwindow = SearchMovieMediaYear(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_series_key_media_year(self):
        subwindow = SearchSeriesKeyMediaYear(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_actor_character(self, type):
        subwindow = SearchActorCharacter(self, type)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def search_episode(self):
        subwindow = SearchEpisodes(self)
        self.mdi_area.addSubWindow(subwindow)
        subwindow.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MSCollection()
    main_window.show()
    sys.exit(app.exec_())