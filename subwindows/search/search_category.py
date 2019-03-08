from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont, QCursor
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

from sqlalchemy import and_

import texts

from db.db_model import Category, Movie, MovieCategory
from db.db_model import Series, SeriesCategory
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchCategory(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie or series by categories.

        :param main: Reference for main windows.
        :param type: String if is "movie" then search for movie if not search
        by "series".
        """
        super(SearchCategory, self).__init__()

        self.session = DB.get_session()
        self.type = type
        self.main = main
        self.row_select = -1

        if type == 'movie':
            self.obj = self.session.query(Movie).order_by(Movie.name)
            self.name = texts.movie_p
        else:
            self.obj = self.session.query(Series).order_by(Series.name)
            self.name = texts.series_p

        windows_title = texts.search + ' ' + self.name + ' ' + \
                        texts.for_ + ' ' + texts.category_p
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
        self.lb_category = QLabel(texts.category_s)
        self.lb_category.setMaximumSize(QSize(100, 25))
        categories = db_select_all(self.session, Category)
        self.cb_category = cb_create()
        populate_combobox(self.cb_category, categories)

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
        self.hbox.addWidget(self.lb_category)
        self.hbox.addWidget(self.cb_category)
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

        self.cb_category.currentIndexChanged.connect(self.query)

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
            texts.category_1,
            texts.category_2,
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
    def view_obj(self, row, col):
        """
        When clicked a cell table who has title show the html view of movie or
        series.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            if self.type == 'movie':
                obj_id = self.table.item(row, 5).text()
                obj = self.session.query(Movie).get(obj_id)
            else:
                obj_id = self.table.item(row, 5).text()
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

            if obj.categories:
                total = len(obj.categories)
                if total >= 2:
                    self.table.setItem(
                        self.rows, 1,
                        QTableWidgetItem(obj.categories[0].category.name)
                    )
                    self.table.setItem(
                        self.rows, 2,
                        QTableWidgetItem(obj.categories[1].category.name)
                    )
                else:
                    self.table.setItem(
                        self.rows, 1,
                        QTableWidgetItem(obj.categories[0].category.name)
                    )
                    self.table.setItem(self.rows, 2, QTableWidgetItem(''))
            else:
                self.table.setItem(self.rows, 1, QTableWidgetItem(''))
                self.table.setItem(self.rows, 2, QTableWidgetItem(''))

            if obj.media:
                self.table.setItem(self.rows, 3,
                                   QTableWidgetItem(obj.media.name))
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
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellClicked.connect(self.view_obj)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    # Set Query Table
    def set_table_query(self, obj_categories):
        """
        Set table with values from database search.

        :param obj_categories: The movie or series values search in database.
        """
        self.clear_table()
        for obj in obj_categories:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(obj.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            if obj.categories:
                total = len(obj.categories)
                if obj.categories:
                    if total >= 2:
                        self.table.setItem(
                            self.rows, 1,
                            QTableWidgetItem(obj.categories[0].category.name)
                        )
                        self.table.setItem(
                            self.rows, 2,
                            QTableWidgetItem(obj.categories[1].category.name)
                        )
                    elif obj.categories[0].category.name:
                            self.table.setItem(
                                self.rows, 1,
                                QTableWidgetItem(obj.categories[0].category.name)
                            )
                            self.table.setItem(self.rows, 2, QTableWidgetItem(''))
                    else:
                        self.table.setItem(self.rows, 1, QTableWidgetItem(''))
                        self.table.setItem(
                            self.rows, 2,
                            QTableWidgetItem(obj.categories[1].category.name)
                        )

                else:
                    self.table.setItem(self.rows, 1, QTableWidgetItem(''))
                    self.table.setItem(self.rows, 2, QTableWidgetItem(''))

            if obj.media:
                self.table.setItem(self.rows, 3,
                                   QTableWidgetItem(obj.media.name))
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

            self.table.cellClicked.connect(self.view_obj)

            self.row_select = -1

            self.rows += 1

        self.le_total.setText(str(self.rows))

    # Query
    def query(self):
        """
        Searching movie or series for selected value in QComboBox in database.
        """
        id, name = get_combobox_info(self.cb_category)
        if self.type == 'movie':
            if id != 0:
                obj_category = self.obj.filter(
                    and_(MovieCategory.category_id == id,
                         MovieCategory.movie_id == Movie.id)
                ).order_by(Movie.name).all()
            else:
                sub = self.session.query(Movie.id). \
                    filter(MovieCategory.movie_id == Movie.id)
                sub = sub.distinct()
                obj_category = self.obj.filter(Movie.id.notin_(sub)).\
                    order_by(Movie.name).all()
        else:
            if id != 0:
                obj_category = self.obj.filter(
                    and_(SeriesCategory.category_id == id,
                         SeriesCategory.series_id == Series.id)
                ).order_by(Series.name).all()
            else:
                sub = self.session.query(Series.id). \
                    filter(SeriesCategory.series_id == Series.id)
                sub = sub.distinct()
                obj_category = self.obj.filter(Series.id.notin_(sub)).\
                    order_by(Series.name).all()

        self.set_table_query(obj_category, id)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_category.setCurrentIndex(0)
        self.clear_table()
        self.set_table()

    # Close Event
    def closeEvent(self, event):
        self.session.close()
