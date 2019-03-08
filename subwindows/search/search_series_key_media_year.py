from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

import texts

from db.db_model import Keyword, Media, Series
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchSeriesKeyMediaYear(QMdiSubWindow):
    def __init__(self, main):
        """
        Search series by keyword, media or year.

        :param main: Reference for main windows.
        """
        super(SearchSeriesKeyMediaYear, self).__init__()

        self.session = DB.get_session()
        self.series = self.session.query(Series)
        self.main = main
        self.row_select = -1

        windows_title = texts.search + ' ' + texts.series_p + ' ' + \
                        texts.for_ + ' ' + texts.keyword + ', ' + \
                        texts.media_p + ', ' + texts.year_s

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

        # Key
        self.lb_key = QLabel(texts.keyword)
        self.lb_key.setMaximumSize(QSize(70, 25))
        key = db_select_all(self.session, Keyword)
        self.cb_key = cb_create()
        populate_combobox(self.cb_key, key)

        # Media
        self.lb_media = QLabel(texts.media_s)
        self.lb_media.setMaximumSize(QSize(70, 25))
        media = db_select_all(self.session, Media)
        self.cb_media = cb_create()
        populate_combobox(self.cb_media, media)

        # Year
        self.lb_year = QLabel(texts.year_s)
        self.lb_year.setMaximumSize(QSize(40, 25))
        self.le_year = le_create(4)
        self.le_year.setMaximumSize(QSize(70, 25))

        # total
        self.lb_total = QLabel(texts.lb_total)
        self.lb_total.setMaximumSize(QSize(70, 25))
        self.le_total = le_create(255)
        self.le_total.setMaximumSize(QSize(100, 25))

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
        self.hbox.addWidget(self.lb_key)
        self.hbox.addWidget(self.cb_key)
        self.hbox.addWidget(self.lb_media)
        self.hbox.addWidget(self.cb_media)
        self.hbox.addWidget(self.lb_year)
        self.hbox.addWidget(self.le_year)
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
        self.set_table(self.series.order_by(Series.name).all())

        self.vbox_main.addWidget(self.table)

        self.cb_key.currentIndexChanged.connect(self.query_key)
        self.cb_media.currentIndexChanged.connect(self.query_media)
        self.le_year.returnPressed.connect(self.query_year)

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
            texts.original_title_s,
            texts.keyword,
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

    # View Series
    def view_series(self, row, col):
        """
        When clicked a cell table who has title show the html view of series.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            series_id = self.table.item(row, 5).text()
            series = self.session.query(Series).get(series_id)
            self.main.view_html(series.view_url, series.name)

            self.row_select = row

    # Set Table
    def set_table(self, query):
        """
        Set table with values from database search.

        :param query: The series values search in database.
        """
        self.clear_table()

        for series in query:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(series.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            self.table.setItem(self.rows, 1,
                               QTableWidgetItem(series.original_name))

            if series.keyword:
                self.table.setItem(self.rows, 2,
                                   QTableWidgetItem(series.keyword.name))
            else:
                self.table.setItem(self.rows, 2, QTableWidgetItem(''))

            if series.media:
                self.table.setItem(self.rows, 3,
                                   QTableWidgetItem(series.media.name))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(''))

            self.table.setItem(self.rows, 4, QTableWidgetItem(series.year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(series.id)))

            for i in range(6):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellClicked.connect(self.view_series)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    # Query Key
    def query_key(self):
        """
        Search key from value in combobox in database.
        :return:
        """
        self.cb_media.currentIndexChanged.disconnect()
        self.cb_media.setCurrentIndex(0)
        id, name = get_combobox_info(self.cb_key)

        if id != 0:
            query_1 = self.series.filter(Series.keyword_id == id). \
                order_by(Series.name).all()
        else:
            query_1 = self.series.filter(Series.keyword_id == None). \
                order_by(Series.name).all()

        self.cb_media.currentIndexChanged.connect(self.query_media)

        self.set_table(query_1)

    # Query Media
    def query_media(self):
        """
        Search for movie with media value selected in ComboBox.
        """
        self.cb_key.currentIndexChanged.disconnect()
        self.cb_key.setCurrentIndex(0)
        id, name = get_combobox_info(self.cb_media)

        if id != 0:
            query_1= self.series.filter(Series.media_id == id).\
                order_by(Series.name).all()
        else:
            query_1 = self.series.filter(Series.media_id == None).\
                order_by(Series.name).all()

        self.cb_key.currentIndexChanged.connect(self.query_key)

        self.set_table(query_1)

    # Query Year
    def query_year(self):
        """
        Search for movie with year given value.
        """
        query_1 = []
        if self.le_year:
            query_1 = self.session.query(Series).\
                filter(Series.year == self.le_year.text()).\
                order_by(Series.name).all()

        self.set_table(query_1)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_key.currentIndexChanged.disconnect()
        self.cb_media.currentIndexChanged.disconnect()
        self.cb_key.setCurrentIndex(0)
        self.cb_media.setCurrentIndex(0)
        self.le_year.setText('')
        self.set_table(self.series.order_by(Series.name).all())
        self.cb_key.currentIndexChanged.connect(self.query_key)
        self.cb_media.currentIndexChanged.connect(self.query_media)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
