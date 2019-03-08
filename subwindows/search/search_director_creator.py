from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

from sqlalchemy import and_

import texts

from db.db_model import Media, Director, Movie, MovieDirector
from db.db_model import Media, Creator, Series, SeriesCreator
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchDirectorCreator(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie or series by director or creator.

        :param main: Reference for main windows.
        :param type: String if is "movie" then search for movie by director if
        not search "series" by creator.
        """
        super(SearchDirectorCreator, self).__init__()

        self.session = DB.get_session()
        self.type = type
        self.main = main
        self.row_select = -1
        self.name = ''

        if self.type == 'movie':
            self.obj = self.session.query(Movie)
            self.name = texts.director_s
            dc = texts.director_p
            lb = texts.director_p
        else:
            self.obj = self.session.query(Series)
            self.name = texts.series_p
            dc = texts.creator_p
            lb = texts.creator_p

        windows_title = texts.search + ' ' + self.name + ' ' + texts.for_ + ' ' + dc

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

        # Category
        self.lb_dc = QLabel(lb)
        self.lb_dc.setMaximumSize(QSize(100, 25))
        if self.type == 'movie':
            dc = db_select_all(self.session, Director)
        else:
            dc = db_select_all(self.session, Creator)
        self.cb_dc = cb_create()
        populate_combobox(self.cb_dc, dc)

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
        self.hbox.addWidget(self.lb_dc)
        self.hbox.addWidget(self.cb_dc)
        self.hbox.addWidget(self.lb_total)
        self.hbox.addWidget(self.le_total)
        self.hbox.addWidget(self.pb_clear)
        self.hbox.addWidget(self.pb_leave)
        self.hbox.addSpacerItem(spacer)
        self.vbox_main.addLayout(self.hbox)

        # Table
        self.table = QTableWidget()
        self.table.horizontalHeader().sectionClicked.connect(self.repaint_cells)
        self.rows = 0
        self.clear_table()
        self.set_table()

        self.vbox_main.addWidget(self.table)

        self.cb_dc.currentIndexChanged.connect(self.query)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.setRowCount(0)
        self.table.setColumnCount(6)
        self.rows = 0

        headers = [
            texts.title_s,
            self.name,
            texts.status,
            texts.media_s,
            texts.year_s,
            'id'
        ]

        self.table.setHorizontalHeaderLabels(headers)

        col_width = self.width - 40
        self.table.setColumnWidth(0, 0.4 * col_width)
        self.table.setColumnWidth(1, 0.2 * col_width)
        self.table.setColumnWidth(2, 0.2 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.1 * col_width)
        self.table.setColumnWidth(5, 0)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet('background-color: #FFFFFF;')
        self.table.setSortingEnabled(True)

    # Repaint Cell
    def repaint_cells(self):
        """
        When the table is self-reclassified repaint it.
        """
        for r in range(self.rows):
            for i in range(6):
                if r % 2 == 0:
                    self.table.item(r, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(r, i).setBackground(
                        QColor(255, 230, 245))

    # View Movie
    def view_ms(self, row, col):
        """
        When clicked a cell table who has title show the html view of movie or
        series.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            obj_id = self.table.item(row, 5).text()

            if self.type == 'movie':
                obj = self.session.query(Movie).get(obj_id)
            else:
                obj = self.session.query(Series).get(obj_id)

            self.main.view_html(obj.view_url, obj.name)

            self.row_select = row

    # Set Table
    def set_table(self):
        """
        Inserts all values in the table.
        """
        for obj in self.obj.all():
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(obj.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            if self.type == 'movie':
                if obj.directors:
                    self.table.setItem(
                        self.rows, 1,
                        QTableWidgetItem(obj.directors[0].director.name)
                    )
                    self.table.setItem(
                        self.rows, 2,
                        QTableWidgetItem(obj.directors[0].order)
                    )
                else:
                    self.table.setItem(self.rows, 1, QTableWidgetItem(''))
                    self.table.setItem(self.rows, 2, QTableWidgetItem(''))
            else:
                if obj.creators:
                    self.table.setItem(
                        self.rows, 1,
                        QTableWidgetItem(obj.creators[0].creator.name)
                    )
                    self.table.setItem(
                        self.rows, 2,
                        QTableWidgetItem(obj.creators[0].order)
                    )
                else:
                    self.table.setItem(self.rows, 1, QTableWidgetItem(''))
                    self.table.setItem(self.rows, 2, QTableWidgetItem(''))

            if obj.media:
                self.table.setItem(self.rows, 3, QTableWidgetItem(
                    obj.media.name))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(''))

            self.table.setItem(self.rows, 4, QTableWidgetItem(obj.year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(obj.id)))

            for i in range(6):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled )

            self.table.cellClicked.connect(self.view_ms)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    # Set Query Table
    def set_table_query(self, result):
        """
        Set table with values from database search.

        :param result: The movie or series values search in database.
        """
        self.clear_table()

        for obj_id, name, year, media, dc, order in result:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            self.table.setItem(self.rows, 1, QTableWidgetItem(dc))
            self.table.setItem(self.rows, 2, QTableWidgetItem(order))
            self.table.setItem(self.rows, 3, QTableWidgetItem(media))
            self.table.setItem(self.rows, 4, QTableWidgetItem(year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(obj_id)))

            for i in range(6):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellClicked.connect(self.view_ms)

            self.row_select = -1

            self.rows += 1

        self.le_total.setText(str(self.rows))

    # Query
    def query(self):
        """
        Searching movie or series for selected value in QComboBox in database.
        """
        id, name = get_combobox_info(self.cb_dc)

        if self.type == 'movie':
            query_1 = self.session.query(Director.name).filter(Director.id == id).first()
            query_2 = self.session.\
                query(Movie, MovieDirector.movie_id, MovieDirector.order). \
                filter(and_(MovieDirector.director_id == id,
                            MovieDirector.movie_id == Movie.id)).\
                order_by(Movie.name).all()
        else:
            query_1 = self.session.query(Creator.name).filter(
                Creator.id == id).first()
            query_2 = self.session. \
                query(Series, SeriesCreator.series_id, SeriesCreator.order). \
                filter(and_(SeriesCreator.creator_id == id,
                            SeriesCreator.series_id == Series.id)). \
                order_by(Series.name).all()

        # id, name, year, media, dc, order
        result = []
        for obj, _, order in query_2:
            if not obj.media:
                media = ''
            else:
                media = obj.media.name
            result.append(
                [obj.id, obj.name, obj.year, media, query_1[0], order])

        self.set_table_query(result)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_dc.setCurrentIndex(0)
        self.clear_table()
        self.set_table()

    # Close Event
    def closeEvent(self, event):
        self.session.close()
