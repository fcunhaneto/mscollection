from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QComboBox, QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem

import texts

from db.db_model import Series, Season, Episode
from db.db_settings import Database as DB

from lib.function_lib import populate_combobox, hbox_create, pb_create, \
    get_combobox_info, db_select_all, line_h_create, le_create


class SearchEpisodes(QMdiSubWindow):
    def __init__(self, main):
        """
        Search for episodes of series by seasons.

        :param main: Reference for main windows.
        """
        super(SearchEpisodes, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.episodes_all = None

        windows_title = texts.insert + ' ' + texts.series_p
        self.setWindowTitle(windows_title)
        width = int(0.95 * main.frameSize().width())
        height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, width, height)
        self.tb_witdh_cast = (0.5 * width) - 50
        self.tb_witdh_episode = width - 50

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        self.hbox_2 = QHBoxLayout()
        self.hbox_2.setSpacing(10)

        # Series Season Num Year
        self.lb_series = QLabel(texts.lb_select_series)
        series = db_select_all(self.session, Series)
        self.cb_series = QComboBox()
        populate_combobox(self.cb_series, series)

        text = texts.now + ' ' + texts.selected + ' ' + texts.season_num
        self.lb_season_num = QLabel(text)
        self.cb_season_num = QComboBox()

        text = ' ' + texts.or_s + ' ' + texts.year_s.lower()
        self.lb_year = QLabel(text)
        self.cb_year = QComboBox()

        self.hbox_search = hbox_create([
            self.lb_series, self.cb_series,
            self.lb_season_num, self.cb_season_num,
            self.lb_year, self.cb_year])

        self.hbox_search.setContentsMargins(0, 0, 0, 10)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_search.addItem(spacer_item)

        self.vbox_main.addLayout(self.hbox_search)

        # Words Title
        self.lb_term_title = QLabel(texts.with_title_term_tt)
        self.le_term_title = le_create(30, texts.with_term_tt)
        self.le_term_title.setPlaceholderText('pressione enter')
        self.le_term_title.editingFinished.connect(self.search_term_title)

        # Words Episode
        self.lb_term_episode = QLabel(texts.with_episode_term_tt)
        self.le_term_episode = le_create(30, texts.with_term_tt)
        self.le_term_episode.setPlaceholderText('pressione enter')
        self.le_term_episode.editingFinished.connect(self.search_term_episode)

        # Buttons
        self.pb_clear = pb_create(texts.pb_clear, 11, 30)
        self.pb_clear.setShortcut('Ctrl+L')
        self.pb_clear.clicked.connect(self.clear)
        self.pb_leave = pb_create(texts.pb_leave, 11, 30)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        self.hbox_term = hbox_create([
            self.lb_term_title,
            self.le_term_title,
            self.lb_term_episode,
            self.le_term_episode,
            self.pb_clear,
            self.pb_leave
        ])

        self.vbox_main.addLayout(self.hbox_term)

        line_h_1 = line_h_create('2px', '#000000')
        self.vbox_main.addWidget(line_h_1)

        # Episode Table
        self.table = QTableWidget(self.subwindow)

        self.table.setColumnCount(3)

        self.headers_episode = [
            texts.episode_cod,
            texts.title_s,
            texts.summary_s,
        ]
        self.table.setHorizontalHeaderLabels(self.headers_episode)

        self.table.setColumnWidth(0, 0.20 * self.tb_witdh_episode)
        self.table.setColumnWidth(1, 0.20 * self.tb_witdh_episode)
        self.table.setColumnWidth(2, 0.60 * self.tb_witdh_episode)

        self.rows = 0

        self.vbox_main.addWidget(self.table)

        self.cb_series.currentIndexChanged.connect(self.selected_series)

    # Selected Series
    def selected_series(self):
        """
        The series was selected so start filling the QComboBox season and year.
        """
        id, name = get_combobox_info(self.cb_series)
        print(id, name)

        season = self.session.query(Season). \
            filter(Season.series_id == id).all()

        self.cb_season_num.addItem('', 0)
        self.cb_year.addItem('', 0)

        for s in season:
            text = texts.season_s + ' ' + str(s.season_num)
            self.cb_season_num.addItem(text, s.id)
            self.cb_year.addItem(s.year, s.id)

        self.cb_season_num.currentIndexChanged.connect(self.selected_season)
        self.cb_year.currentIndexChanged.connect(self.selected_season)

    def selected_season(self):
        """
        Select the season or year now search for the corresponding episodes in
        the database.
        :return:
        """
        id_n, name_n = get_combobox_info(self.cb_season_num)
        id_y, name_y = get_combobox_info(self.cb_year)

        if id_n != 0:
            self.season = self.session.query(Season).get(id_n)

        elif id_y != 0:
            self.season = self.session.query(Season).get(id_y)
        else:
            pass  # messagebox

        episodes_all = self.session.query(Episode).\
            filter(Episode.season_id == self.season.id).all()

        self.set_table_episode(episodes_all)

    def set_table_episode(self, episodes):
        """
        Fill table episode.
        """
        self.clear_table()
        for episode in episodes:
            self.table.insertRow(self.rows)
            self.table.setRowHeight(self.rows, 150)
            self.table.setItem(self.rows, 0,
                               QTableWidgetItem(episode.code))
            self.table.setItem(self.rows, 1,
                               QTableWidgetItem(episode.name))
            self.table.setItem(self.rows, 2,
                               QTableWidgetItem(episode.summary))

            for i in range(3):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.rows += 1

    # Query Title
    def search_term_title(self):
        """
        Search term in title.
        """
        words = self.le_term_title.text().split()
        queries = []
        for word in words:
            word = '%{0}%'.format(word)
            query = self.session.query(Episode) \
                .filter(Episode.name.ilike(word)).all()
            queries += query
        print(queries)
        for q in query:
            print(q)
        self.set_table_episode(queries)

    # Query Episode
    def search_term_episode(self):
        """
        Search term in title.
        """
        words = self.le_term_episode.text().split()
        queries = []
        for word in words:
            word = '%{0}%'.format(word)
            query = self.session.query(Episode) \
                .filter(Episode.summary.ilike(word)).all()
            queries += query

        self.set_table_episode(queries)

    def clear_table(self):
        """
        Clear table episode.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(self.headers_episode)
        self.rows = 0

    def clear(self):
        self.cb_series.currentIndexChanged.disconnect()
        self.cb_season_num.currentIndexChanged.disconnect()
        self.cb_year.currentIndexChanged.disconnect()
        self.cb_series.setCurrentIndex(0)
        self.cb_season_num.clear()
        self.cb_year.clear()
        self.clear_table()

        self.cb_series.currentIndexChanged.connect(self.selected_series)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
