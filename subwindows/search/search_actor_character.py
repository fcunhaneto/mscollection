from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship
import texts

from db.db_model import Actor, Character, Media, Cast, MovieCast, Movie, \
    SeriesCast, Series
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchActorCharacter(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie or series by actor or character.

        :param main: Reference for main windows.
        :param type: String if is "movie" then search for movie if not search
        by "series".
        """
        super(SearchActorCharacter, self).__init__()

        self.session = DB.get_session()
        self.type = type

        if self.type == 'movie':
            windows_title = texts.search + ' ' + texts.movie_p + ' ' + \
                            texts.for_ + ' ' + texts.actor_s + ', ' + \
                            texts.character_s
        else:
            windows_title = texts.search + ' ' + texts.series_p + ' ' + \
                            texts.for_ + ' ' + texts.actor_s + ', ' + \
                            texts.character_s

        self.main = main
        self.row_select = -1

        self.setWindowTitle(windows_title)
        self.width = int(0.8 * main.frameSize().width())
        self.height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, self.width, self.height)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        # Actor
        self.lb_actor = QLabel(texts.actor_s)
        self.lb_actor.setMaximumSize(QSize(100, 25))
        self.cb_actor = cb_create()

        if self.type == 'movie':
            query = self.session.\
                query(Movie, MovieCast.cast_id, Actor.id, Actor.name).\
                join(MovieCast).filter(MovieCast.movie_id == Movie.id).\
                join(Cast).filter(Cast.actor_id == Actor.id).\
                order_by(Actor.name).all()
        else:
            query = self.session.\
                query(Series, SeriesCast.cast_id, Actor.id, Actor.name).\
                join(SeriesCast).filter(SeriesCast.series_id == Series.id).\
                join(Cast).filter(Cast.actor_id == Actor.id).\
                order_by(Actor.name).all()

        for _, _, actor_id, actor in query:
            self.cb_actor.addItem(actor, actor_id)

        # Character
        self.lb_character = QLabel(texts.character_s)
        self.lb_character.setMaximumSize(QSize(100, 25))
        self.cb_character = cb_create()
        if self.type == 'movie':
            query = self.session. \
                query(Movie, MovieCast.cast_id, Character.id, Character.name). \
                join(MovieCast).filter(MovieCast.movie_id == Movie.id). \
                join(Cast).filter(Cast.character_id == Character.id).\
                order_by(Character.name).all()
        else:
            query = self.session. \
                query(Series, SeriesCast.cast_id, Character.id, Character.name). \
                join(SeriesCast).filter(SeriesCast.series_id == Series.id). \
                join(Cast).filter(Cast.character_id == Character.id).\
                order_by(Character.name).all()

        for _, _, actor_id, actor in query:
            self.cb_character.addItem(actor, actor_id)

        # total
        self.lb_total = QLabel(texts.lb_total)
        self.lb_total.setMaximumSize(QSize(100, 25))
        self.le_total = le_create(255)

        # Buttons
        self.pb_clear = pb_create(texts.pb_clear, 11, 30)
        self.pb_clear.setShortcut('Ctrl+L')
        self.pb_clear.clicked.connect(self.clear)
        self.pb_leave = pb_create(texts.pb_leave, 11, 30)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Hbox
        self.hbox = QHBoxLayout(self.subwindow)
        self.hbox.addWidget(self.lb_actor)
        self.hbox.addWidget(self.cb_actor)
        self.hbox.addWidget(self.lb_character)
        self.hbox.addWidget(self.cb_character)
        self.hbox.addWidget(self.lb_total)
        self.hbox.addWidget(self.le_total)
        self.hbox.addWidget(self.pb_clear)
        self.hbox.addWidget(self.pb_leave)
        self.hbox.addSpacerItem(spacer)
        self.vbox_main.addLayout(self.hbox)

        # Table
        self.table = QTableWidget()
        self.rows = 0
        self.init_table()

        self.vbox_main.addWidget(self.table)

        self.cb_actor.currentIndexChanged.connect(self.query_actor)
        self.cb_character.currentIndexChanged.connect(self.query_character)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(6)
        self.rows = 0

        headers = [
            texts.title_s,
            texts.actor_s,
            texts.character_s,
            texts.media_s,
            texts.year_s,
            'id'
        ]

        self.table.setHorizontalHeaderLabels(headers)

        col_width = self.width - 40
        self.table.setColumnWidth(0, 0.3 * col_width)
        self.table.setColumnWidth(1, 0.3 * col_width)
        self.table.setColumnWidth(2, 0.2 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.1 * col_width)
        self.table.setColumnWidth(5, 0)

        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

    # Init Table
    def init_table(self):
        """
        Get values from database to fill table.
        """
        if self.type == 'movie':
            query = self.session.query(Movie.id,
                                       Movie.name,
                                       Movie.year,
                                       Media.name,
                                       Cast.id,
                                       Actor.name,
                                       Character.name).\
                filter(and_(MovieCast.movie_id == Movie.id,
                            MovieCast.cast_id == Cast.id,
                            Cast.actor_id == Actor.id,
                            Cast.character_id == Character.id,
                            Movie.media_id == Media.id)).\
                all()
        else:
            query = self.session.query(Series.id,
                                       Series.name,
                                       Series.year,
                                       Media.name,
                                       Cast.id,
                                       Actor.name,
                                       Character.name). \
                filter(and_(SeriesCast.series_id == Series.id,
                            SeriesCast.cast_id == Cast.id,
                            Cast.actor_id == Actor.id,
                            Cast.character_id == Character.id,
                            Series.media_id == Media.id)). \
                all()

        self.set_table(query)

    # View Movie
    def view(self, row, col):
        """
        When clicked a cell table who has title show the html view of movie or
        series.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            id = self.table.item(row, 5).text()
            if self.type == 'movie':
                query = self.session.query(Movie).get(id)
            else:
                query = self.session.query(Series).get(id)

            self.main.view_html(query.view_url, query.name)

            self.row_select = row


    # Set Table
    def set_table(self, query):
        """
        Inserts the values in the table.

        :param query: List containing the values to insert.
        """
        self.clear_table()
        title = ''
        flag = False

        for id, name, year, media, cast_id, actor, character in query:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            self.table.setItem(self.rows, 1, QTableWidgetItem(actor))
            self.table.setItem(self.rows, 2, QTableWidgetItem(character))
            self.table.setItem(self.rows, 3, QTableWidgetItem(media))
            self.table.setItem(self.rows, 4, QTableWidgetItem(year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(id)))

            if not flag and title != name:
                title = name
                flag = True
                color = QColor(240, 250, 228)
            elif flag and title != name:
                title = name
                flag = False
                color = QColor(255, 230, 245)

            for i in range(6):
                self.table.item(self.rows, i).setBackground(color)
                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled )

            self.table.cellClicked.connect(self.view)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    def query_actor(self):
        """
        When an actor is selected searches for all corresponding movies or
        series and than fill table with it find values.
        """
        self.cb_character.currentIndexChanged.disconnect()
        self.cb_character.setCurrentIndex(0)

        id, name = get_combobox_info(self.cb_actor)

        if self.type == 'movie':
            cast = self.session.query(MovieCast.movie_id, Cast.id).filter(
                Cast.actor_id == id, MovieCast.cast_id == Cast.id).all()
            movie_cast = [x[0] for x in cast]
            movie_actor = [x[1] for x in cast]
            query = self.session.\
                query( Movie.id, Movie.name, Movie.year, Media.name,
                       MovieCast.cast_id, Actor.name, Character.name).\
                filter(Movie.id.in_(movie_cast), Movie.media_id == Media.id, ).\
                join(MovieCast).filter(MovieCast.cast_id.in_(movie_actor),
                                       MovieCast.movie_id == Movie.id).\
                join(Cast).filter(Cast.id.in_(movie_actor),
                                  Cast.actor_id == Actor.id,
                                  Cast.character_id == Character.id).\
                all()
        else:
            cast = self.session.query(SeriesCast.series_id, Cast.id).filter(
                Cast.actor_id == id, SeriesCast.cast_id == Cast.id).all()
            series_cast = [x[0] for x in cast]
            series_actor = [x[1] for x in cast]
            query = self.session.\
                query(Series.id, Series.name, Series.year, Media.name,
                      SeriesCast.cast_id, Actor.name, Character.name). \
                filter(Series.id.in_(series_cast), Series.media_id == Media.id, ). \
                join(SeriesCast).filter(SeriesCast.cast_id.in_(series_actor),
                                        SeriesCast.series_id == Series.id). \
                join(Cast).filter(Cast.id.in_(series_actor),
                                  Cast.actor_id == Actor.id,
                                  Cast.character_id == Character.id). \
                all()

        self.set_table(query)

        self.cb_character.currentIndexChanged.connect(self.query_character)

    def query_character(self):
        """
        When an cahracter is selected searches for all corresponding movies or
        series and than fill table with it find values.
        """
        self.cb_actor.currentIndexChanged.disconnect()
        self.cb_actor.setCurrentIndex(0)

        id, name = get_combobox_info(self.cb_character)
        if self.type == 'movie':
            cast = self.session.query(MovieCast.movie_id, Cast.id).filter(
                Cast.character_id == id, MovieCast.cast_id == Cast.id).all()
            movie_cast = [x[0] for x in cast]
            movie_character = [x[1] for x in cast]
            query = self.session. \
                query(Movie.id, Movie.name, Movie.year, Media.name,
                      MovieCast.cast_id, Actor.name, Character.name). \
                filter(Movie.id.in_(movie_cast), Movie.media_id == Media.id, ). \
                join(MovieCast).filter(MovieCast.cast_id.in_(movie_character),
                                       MovieCast.movie_id == Movie.id). \
                join(Cast).filter(Cast.id.in_(movie_character),
                                  Cast.actor_id == Actor.id,
                                  Cast.character_id == Character.id). \
                all()
        else:
            cast = self.session.query(SeriesCast.series_id, Cast.id).filter(
                Cast.character_id == id, SeriesCast.cast_id == Cast.id).all()
            series_cast = [x[0] for x in cast]
            series_character = [x[1] for x in cast]
            query = self.session. \
                query(Series.id, Series.name, Series.year, Media.name,
                      SeriesCast.cast_id, Actor.name, Character.name). \
                filter(Series.id.in_(series_cast),
                       Series.media_id == Media.id, ). \
                join(SeriesCast).filter(SeriesCast.cast_id.in_(series_character),
                                        SeriesCast.series_id == Series.id). \
                join(Cast).filter(Cast.id.in_(series_character),
                                  Cast.actor_id == Actor.id,
                                  Cast.character_id == Character.id). \
                all()

        self.set_table(query)

        self.cb_actor.currentIndexChanged.connect(self.query_actor)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_actor.currentIndexChanged.disconnect()
        self.cb_character.currentIndexChanged.disconnect()
        self.cb_actor.setCurrentIndex(0)
        self.cb_character.setCurrentIndex(0)
        self.le_total.setText('')
        self.clear_table()
        self.cb_actor.currentIndexChanged.connect(self.query_actor)
        self.cb_character.currentIndexChanged.connect(self.query_character)
        self.init_table()

    # Close Event
    def closeEvent(self, event):
        self.session.close()

