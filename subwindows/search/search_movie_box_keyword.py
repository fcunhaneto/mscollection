from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

import texts

from db.db_model import Keyword, Box, Movie
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchBoxKeyword(QMdiSubWindow):
    def __init__(self, main):
        """
        Search movie by box title or keyword.

        :param main: Reference for main windows.
        """
        super(SearchBoxKeyword, self).__init__()

        self.session = DB.get_session()
        self.movie = self.session.query(Movie)
        self.main = main
        self.row_select = -1

        windows_title = texts.search + ' ' + texts.movie_p + ' ' + \
                        texts.for_ + ' ' + texts.box + ', ' + texts.keyword
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

        # Box
        self.lb_box = QLabel(texts.box)
        self.lb_box.setMaximumSize(QSize(100, 25))
        box = db_select_all(self.session, Box)
        self.cb_box = cb_create()
        populate_combobox(self.cb_box, box)

        # Words
        text = texts.or_s + ' ' + texts.with_the_p + ' ' + texts.term_p
        self.lb_term = QLabel(text)
        self.le_term = le_create(20, texts.with_term_tt)
        self.le_term.setPlaceholderText('pressione enter')
        self.le_term.editingFinished.connect(self.query_term)

        # Keyword
        text = texts.or_s + ' ' + texts.keyword
        self.lb_key = QLabel(text)
        self.lb_key.setMaximumSize(QSize(100, 25))
        key = db_select_all(self.session, Keyword)
        self.cb_key = cb_create()
        populate_combobox(self.cb_key, key)

        # total
        self.lb_total = QLabel(texts.lb_total)
        self.lb_total.setMaximumSize(QSize(100, 25))
        self.le_total = le_create(255)
        self.le_total.setMaximumWidth(100)

        # Buttons
        self.pb_clear = pb_create(texts.pb_clear, 11, 30)
        self.pb_clear.setMaximumWidth(100)
        self.pb_clear.setShortcut('Ctrl+L')
        self.pb_clear.clicked.connect(self.clear)
        self.pb_leave = pb_create(texts.pb_leave, 11, 30)
        self.pb_leave.setMaximumWidth(100)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        # Hbox
        self.hbox = QHBoxLayout(self.subwindow)
        self.hbox.addWidget(self.lb_box)
        self.hbox.addWidget(self.cb_box)
        self.hbox.addWidget(self.lb_term)
        self.hbox.addWidget(self.le_term)
        self.hbox.addWidget(self.lb_key)
        self.hbox.addWidget(self.cb_key)
        self.hbox.addWidget(self.lb_total)
        self.hbox.addWidget(self.le_total)
        self.hbox.addWidget(self.pb_clear)
        self.hbox.addWidget(self.pb_leave)

        self.vbox_main.addLayout(self.hbox)

        # Table
        self.table = QTableWidget()
        self.table.horizontalHeader().sectionClicked.connect(self.repaint_cells)
        self.rows = 0
        self.set_table(self.movie.order_by(Movie.name).all())

        self.vbox_main.addWidget(self.table)

        self.cb_box.currentIndexChanged.connect(self.query_box)
        self.cb_key.currentIndexChanged.connect(self.query_keyword)

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
            texts.box,
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

    # View Movie
    def view(self, row, col):
        """
        When clicked a cell table who has title show the html view of movie.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            movie_id = self.table.item(row, 5).text()
            movie = self.movie.get(movie_id)
            self.main.view_html(movie.view_url, movie.name)

            self.row_select = row

    # Set Table
    def set_table(self, query):
        """
        Set table with values from database search.

        :param query: The movie values search in database.
        """
        self.clear_table()

        for movie in query:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(movie.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            if movie.box:
                self.table.setItem(self.rows, 1,
                                   QTableWidgetItem(movie.box.name))
            else:
                self.table.setItem(self.rows, 1, QTableWidgetItem(''))

            if movie.keyword:
                self.table.setItem(self.rows, 2,
                                   QTableWidgetItem(movie.keyword.name))
            else:
                self.table.setItem(self.rows, 2, QTableWidgetItem(''))

            if movie.media:
                self.table.setItem(self.rows, 3,
                                   QTableWidgetItem(movie.media.name))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(''))

            self.table.setItem(self.rows, 4, QTableWidgetItem(movie.year))

            self.table.setItem(self.rows, 5, QTableWidgetItem(str(movie.id)))

            for i in range(6):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellClicked.connect(self.view)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    def query_box(self):
        """
        Search for movie with box value selected in ComboBox.
        """
        self.cb_key.currentIndexChanged.disconnect()
        self.cb_key.setCurrentIndex(0)

        id, name =get_combobox_info(self.cb_box)
        query = self.movie.filter(Movie.box_id == id)

        self.set_table(query)

        self.cb_key.currentIndexChanged.connect(self.query_keyword)

    def query_keyword(self):
        """
        Search for movie with keyword value selected in ComboBox.
        """
        self.cb_box.currentIndexChanged.disconnect()
        self.cb_box.setCurrentIndex(0)

        id, name = get_combobox_info(self.cb_key)
        query = self.movie.filter(Movie.keyword_id == id)

        self.set_table(query)

        self.cb_box.currentIndexChanged.connect(self.query_box)

    def query_term(self):
        """
        Search for movie by terms found within the title "box".
        """
        self.cb_box.currentIndexChanged.disconnect()
        self.cb_box.setCurrentIndex(0)
        words = self.le_term.text().split()
        queries = []
        for word in words:
            word = '%{0}%'.format(word)
            query = self.session.query(Movie) \
                .filter(Box.name.ilike(word), Movie.box_id == Box.id).all()
            queries += query

        self.set_table(queries)

        self.cb_box.currentIndexChanged.connect(self.query_box)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_box.currentIndexChanged.disconnect()
        self.cb_key.currentIndexChanged.disconnect()
        self.cb_box.setCurrentIndex(0)
        self.cb_key.setCurrentIndex(0)
        self.le_total.setText('')
        self.clear_table()
        self.set_table(self.movie.order_by(Movie.name).all())
        self.cb_box.currentIndexChanged.connect(self.query_box)
        self.cb_key.currentIndexChanged.connect(self.query_keyword)

    # Close Event
    def closeEvent(self, event):
        self.session.close()

