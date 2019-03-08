import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, QVBoxLayout, \
    QHBoxLayout, QLabel, QComboBox, QSpacerItem, QSizePolicy, QTableWidget, \
    QTableWidgetItem, QMessageBox, QProgressBar

from sqlalchemy.exc import IntegrityError, DBAPIError

import texts

from db.db_model import Media, Series
from db.db_model import Season, Episode
from db.db_settings import Database as DB

from lib.episodes_scraping import episodes_scraping_imdb, episodes_scraping_ms
from lib.function_lib import populate_combobox, hbox_create, \
    get_combobox_info, show_msg, db_select_all, line_h_create, line_v_create, \
    le_create, pb_create


class EditSeason(QMdiSubWindow):
    """
    Class to provide all methods to insert seasons and episodes in database.
    """
    def __init__(self, main):
        super(EditSeason, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.season = None
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

        self.hbox_search = hbox_create([self.lb_series, self.cb_series,
                                   self.lb_season_num, self.cb_season_num,
                                   self.lb_year, self.cb_year])
        self.hbox_search.setContentsMargins(0, 0, 0, 10)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_search.addItem(spacer_item)

        self.vbox_main.addLayout(self.hbox_search)

        line_h_1 = line_h_create('2px', '#000000')
        self.vbox_main.addWidget(line_h_1)

        # Series Left Side
        self.fm_left = QFormLayout()
        self.fm_left.setSpacing(10)
        self.fm_left.setContentsMargins(0, 0, 5, 0)

        # Season Num Year
        text = texts.season_s + '/' + texts.year_s
        self.lb_season = QLabel(text)
        self.le_season_num = le_create(tooltip=texts.season_num_tt)
        self.le_season_num.setPlaceholderText(texts.season_num)

        self.le_year = le_create(4)
        self.le_year.setPlaceholderText(texts.year_s)

        self.fm_left.setWidget(0, QFormLayout.LabelRole,
                               self.lb_season)
        self.hbox_ny = hbox_create([self.le_season_num, self.le_year])
        self.fm_left.setLayout(0, QFormLayout.FieldRole, self.hbox_ny)

        # Media
        self.lb_media = QLabel(texts.media_s)
        media = db_select_all(self.session, Media)
        self.cb_media = QComboBox()
        populate_combobox(self.cb_media, media)

        self.fm_left.setWidget(1, QFormLayout.LabelRole, self.lb_media)
        self.fm_left.setWidget(1, QFormLayout.FieldRole, self.cb_media)

        # IMDB URL
        self.lb_url_imdb = QLabel('IMDB Url')
        self.le_url_imdb = le_create()

        self.fm_left.setWidget(2, QFormLayout.LabelRole, self.lb_url_imdb)
        self.fm_left.setWidget(2, QFormLayout.FieldRole, self.le_url_imdb)

        # Minha Série URL
        self.lb_urL_ms = QLabel('MS Url')
        self.le_url_ms = le_create(tooltip=texts.ms_episode_search)

        self.fm_left.setWidget(3, QFormLayout.LabelRole, self.lb_urL_ms)
        self.fm_left.setWidget(3, QFormLayout.FieldRole, self.le_url_ms)

        # PB Search
        self.lb_episode_search = QLabel(texts.lb_episode_search)
        self.fm_left.setWidget(4, QFormLayout.LabelRole, self.lb_episode_search)

        self.hbox_url_pb = QHBoxLayout()
        self.hbox_url_pb.setSpacing(10)

        self.pb_search_imdb = pb_create(texts.imdb)
        self.pb_search_imdb.clicked.connect(lambda site:
                                            self.scraping_episodes('imdb'))
        self.pb_search_ms = pb_create(texts.pb_ms_search)
        self.pb_search_ms.clicked.connect(lambda site:
                                          self.scraping_episodes('ms'))

        self.hbox_url_pb.addWidget(self.pb_search_imdb)
        self.hbox_url_pb.addWidget(self.pb_search_ms)
        self.fm_left.setLayout(4, QFormLayout.FieldRole, self.hbox_url_pb)

        # PB Main
        line_h_2 = line_h_create('2px', '#7777FF')
        line_h_3 = line_h_create('2px', '#7777FF')
        self.fm_left.setWidget(5, QFormLayout.FieldRole, line_h_2)
        self.fm_left.setWidget(6, QFormLayout.FieldRole, line_h_3)
        self.hbox_pb_main = QHBoxLayout()

        self.pb_save = pb_create(texts.pb_save)
        self.pb_save.clicked.connect(self.start_save)
        self.pb_save.setShortcut('Ctrl+S')

        self.pb_clear = pb_create(texts.pb_clear)
        self.pb_clear.clicked.connect(self.clear)
        self.pb_clear.setShortcut('Ctrl+L')

        self.pb_help = pb_create(texts.pb_help)
        self.pb_help.clicked.connect(self.help)
        self.pb_help.setShortcut('Ctrl+H')

        self.pb_delete = pb_create(texts.pb_delete)
        self.pb_delete.clicked.connect(self.delete_season)
        self.pb_clear.setShortcut('Ctrl+D')

        self.pb_leave = pb_create(texts.pb_leave)
        self.pb_leave.clicked.connect(self.close)
        self.pb_leave.setShortcut('Ctrl+Q')

        self.hbox_pb_main.addWidget(self.pb_save)
        self.hbox_pb_main.addWidget(self.pb_clear)
        self.hbox_pb_main.addWidget(self.pb_help)
        self.hbox_pb_main.addWidget(self.pb_delete)
        self.hbox_pb_main.addWidget(self.pb_leave)

        self.fm_left.setLayout(7, QFormLayout.FieldRole, self.hbox_pb_main)

        # Series Right Size
        self.vbox_right = QVBoxLayout(self.subwindow)
        self.vbox_right.setContentsMargins(5, 0, 0, 0)

        # Cast Table
        self.table_cast = QTableWidget(self.subwindow)
        self.table_cast.setColumnCount(4)

        self.headers_cast = [
            texts.actor_s,
            texts.character_s,
            texts.order,
            texts.star.capitalize(),
        ]
        self.table_cast.setHorizontalHeaderLabels(self.headers_cast)

        self.table_cast.setColumnWidth(0, 0.30 * self.tb_witdh_cast)
        self.table_cast.setColumnWidth(1, 0.40 * self.tb_witdh_cast)
        self.table_cast.setColumnWidth(2, 0.15 * self.tb_witdh_cast)
        self.table_cast.setColumnWidth(3, 0.15 * self.tb_witdh_cast)

        self.rows_cast = 0

        self.vbox_right.addWidget(self.table_cast)

        self.hbox_2.addLayout(self.fm_left)

        line_v = line_v_create('2px', '#000000')

        self.hbox_2.addWidget(line_v)
        self.hbox_2.addLayout(self.vbox_right)
        self.vbox_main.addLayout(self.hbox_2)

        # Episode
        self.vbox_episode = QVBoxLayout(self.subwindow)

        # Episode Add Row
        self.hbox_episode = QHBoxLayout()

        self.lb_episode = QLabel(texts.episode_s)
        self.pb_add_row_episode = pb_create('+', 12, 30, 50)
        self.pb_add_row_episode.clicked.connect(self.table_episode_add_row)

        self.p_bar = QProgressBar(self.subwindow)
        self.p_bar.setValue(0)

        self.hbox_episode.addWidget(self.lb_episode)
        self.hbox_episode.addWidget(self.pb_add_row_episode)
        self.hbox_episode.addWidget(self.p_bar)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_episode.addItem(spacer_item)

        # Episode Table
        self.table_episode = QTableWidget(self.subwindow)

        self.table_episode.setColumnCount(3)

        self.headers_episode = [
            texts.episode_cod,
            texts.title_s,
            texts.summary_s,
        ]
        self.table_episode.setHorizontalHeaderLabels(self.headers_episode)

        self.table_episode.setColumnWidth(0, 0.20 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(1, 0.20 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(2, 0.60 * self.tb_witdh_episode)

        self.rows_episode = 0
        self.result_episode = []
        self.table_episode.itemChanged.connect(self.item_changed)

        line_h_4 = line_h_create('2px', '#000000')

        self.vbox_episode.addLayout(self.hbox_episode)
        self.vbox_episode.addWidget(self.table_episode)
        self.vbox_main.addWidget(line_h_4)
        self.vbox_main.addLayout(self.vbox_episode)

        self.errors = {
            'no error': 1,
            'no series': 2,
            'no season': 3,
            'db error': 4,
        }

        self.cb_series.setFocus()

        self.cb_series.currentIndexChanged.connect(self.selected_series)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character QComboBox in table cast and Table episode
        columns  if windows resize.

        :param event: Window.
        """
        width = event.size().width()
        height = event.size().height()
        self.tb_witdh = (0.5 * width) - 50
        self.tb_witdh_episode = width - 50

        for i in range(self.rows_cast):
            self.cb_actor[i].setMaximumWidth(0.4 * self.tb_witdh)
            self.cb_character[i].setMaximumWidth(0.4 * self.tb_witdh)

        self.table_episode.setColumnWidth(0, 0.05 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(1, 0.20 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(2, 0.70 * self.tb_witdh_episode)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character combobox in table cast if windows resize.

        :param event: Window.
        """
        width = event.size().width()
        self.tb_width = (0.5 * width) - 50

        for i in range(self.rows_cast):
            self.cb_actor[i].setMaximumWidth(0.4 * self.tb_width)
            self.cb_character[i].setMaximumWidth(0.4 * self.tb_width)

        self.table_episode.setColumnWidth(0, 0.05 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(1, 0.20 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(2, 0.70 * self.tb_witdh_episode)

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Save Season Episodes
    def save_season_episodes(self):
        """
        Saved season and episodes in database.

        :return: Errors when inserting into the database or ok if not errors.
        """
        self.season.season_num = self.le_season_num.text()
        self.season.year = self.le_year.text()
        id_m, name_m = get_combobox_info(self.cb_media)
        self.season.media_id = id_m

        _, name_s = get_combobox_info(self.cb_series)

        try:
            self.session.add(self.season)
            self.session.commit()
        except (IntegrityError, DBAPIError) as error:
            self.session.rollback()
            self.session.commit()

            return self.errors['db error'], name_s

        episodes = []
        i = 0
        for name, summary, code in self.result_episode:
            self.episodes_all[i].name = name
            self.episodes_all[i].summary = summary
            self.episodes_all[i].code = code

            episodes.append(self.episodes_all[i])
            i += 1

        try:
            self.session.add_all(episodes)
            self.session.commit()
        except (IntegrityError, DBAPIError) as error:
            self.session.rollback()
            self.session.commit()
            print(str(error))
            return self.errors['db error'], name_s

        return self.errors['no error'], name_s

    # Start Save
    def start_save(self):
        """
        Start function save and show messages if errors happen.
        """
        error, name = self.save_season_episodes()
        if error == self.errors['db error']:
            text = texts.msg_insert_season_error(name,
                                                 self.le_season_num.text())
            show_msg(texts.insert_error, text, QMessageBox.Critical,
                     QMessageBox.Close, str(error))
        elif error == self.errors['no error']:
            text = texts.msg_insert_season_ok(name, self.le_season_num.text())
            show_msg(texts.insert_ok, text, QMessageBox.Information,
                     QMessageBox.Close)

        self.clear()

    # Delete
    def delete_season(self):
        result = 0
        name = texts.season_s + ' ' + str(self.season.season_num)
        text = texts.msg_before_delete(name)

        answer = QMessageBox.information(
            self, texts.warning,
            text, QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            self.series = self.session.query(Season).get(self.season.id)
            result = self.session.query(Season).\
                filter(Season.id == self.season.id).delete()

        if result == 1:
            self.session.commit()
            text = texts.msg_delete_ok(name)
            show_msg(texts.delete_ok, text, QMessageBox.Information,
                     QMessageBox.Close)

    # Selected Series
    def selected_series(self):
        """
        Get values in SeriesCast to fill table cast.
        """
        id, name = get_combobox_info(self.cb_series)
        season = self.session.query(Season).\
            filter(Season.series_id == id).all()

        self.cb_season_num.addItem('', 0)
        self.cb_year.addItem('', 0)

        for s in season:
            self.cb_season_num.addItem(str(s.season_num), s.id)
            self.cb_year.addItem(s.year, s.id)

        self.cb_season_num.currentIndexChanged.connect(self.selected_season)
        self.cb_year.currentIndexChanged.connect(self.selected_season)

    def selected_season(self):
        id_n, name_n = get_combobox_info(self.cb_season_num)
        id_y, name_y = get_combobox_info(self.cb_year)

        if id_n != 0:
            self.season = self.session.query(Season).get(id_n)
        elif id_y != 0:
            self.season = self.session.query(Season).get(id_y)
        else:
            return

        self.le_season_num.setText(str(self.season.season_num))
        self.le_year.setText(self.season.year)
        id_m = self.season.media_id
        self.set_combobox_value(self.cb_media, Media, id_m)
        self.episodes_all = self.session.query(Episode).\
            filter(Episode.season_id == self.season.id).all()
        self.populated_table_cast()
        self.populated_table_episode()

    # Populate Cast Table
    def populated_table_cast(self):
        """
        Populate table cast.
        :param ac_name: Actor name.
        :param ch_name: Character name.
        """
        for ac in self.season.cast:
            self.table_cast.insertRow(self.rows_cast)
            self.table_cast.setItem(self.rows_cast, 0,
                                    QTableWidgetItem(ac.cast.actors.name))
            self.table_cast.setItem(self.rows_cast, 1,
                                    QTableWidgetItem(ac.cast.characters.name))
            if ac.star:
                icon = QIcon()
                icon.addPixmap(
                    QPixmap('images/star_yellow_16.png'), QIcon.Normal,
                    QIcon.Off
                )
                star = QTableWidgetItem()
                star.setIcon(icon)
                self.table_cast.setItem(self.rows_cast, 2, star)

            self.rows_cast += 1

    # Table Episode Add Rows
    def table_episode_add_row(self):
        """
        Add rows in table episode.
        """
        self.table_episode.insertRow(self.rows_episode)
        self.table_episode.setRowHeight(self.rows_episode, 150)
        if self.result_episode:
            self.result_episode.append(['', '', ''])
        else:
            self.result_episode = list()
            self.result_episode.append(['', '', ''])

        for i in range(3):
            if self.rows_episode % 2 == 0:
                self.table_episode.setItem(self.rows_episode, i,
                                           QTableWidgetItem(''))
                self.table_episode.item(self.rows_episode, i).setBackground(
                    QColor(240, 250, 228))
            else:
                self.table_episode.setItem(self.rows_episode, i,
                                           QTableWidgetItem(''))
                self.table_episode.item(self.rows_episode, i).setBackground(
                    QColor(255, 230, 245))

        self.table_episode.itemChanged.connect(self.item_changed)

        self.rows_episode += 1

    def populated_table_episode(self):
        self.table_episode.itemChanged.disconnect()
        for episode in self.episodes_all:
            self.table_episode.insertRow(self.rows_episode)
            self.table_episode.setRowHeight(self.rows_episode, 150)
            self.table_episode.setItem(self.rows_episode, 0,
                                       QTableWidgetItem(episode.code))
            self.table_episode.setItem(self.rows_episode, 1,
                                       QTableWidgetItem(episode.name))
            self.table_episode.setItem(self.rows_episode, 2,
                                       QTableWidgetItem(episode.summary))

            self.result_episode.append([episode.name, episode.summary,
                                        episode.code])

            for i in range(3):
                if self.rows_episode % 2 == 0:
                    self.table_episode.item(self.rows_episode, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table_episode.item(self.rows_episode, i).setBackground(
                        QColor(255, 230, 245))

            self.rows_episode += 1

        self.table_episode.itemChanged.connect(self.item_changed)

    # Search Episode
    def scraping_episodes(self, site):
        """
        Get episodes title and summary in IMDB or Minha Séries site.

        :param site: If value is "ms" site is "Minha Série" else site is IMDB.
        """
        self.clear_table_episode()
        self.table_episode.itemChanged.disconnect()
        if site == 'ms':
            self.result_episode = episodes_scraping_ms(self.le_url_ms.text(),
                                                       self.p_bar)
        else:
            self.result_episode = episodes_scraping_imdb(
                self.le_url_imdb.Text())

        for result in self.result_episode:
            self.table_episode.insertRow(self.rows_episode)
            ep_num = self.rows_episode + 1
            code = '{0}.{1}'.format(self.le_season_num.text(), ep_num)

            self.table_episode.setItem(self.rows_episode, 0,
                                       QTableWidgetItem(code))
            self.table_episode.setItem(self.rows_episode, 1,
                                       QTableWidgetItem(result[0]))
            self.table_episode.setItem(self.rows_episode, 2,
                                       QTableWidgetItem(result[1]))

            for i in range(3):
                if self.rows_episode % 2 == 0:
                    self.table_episode.item(self.rows_episode, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table_episode.item(self.rows_episode, i).setBackground(
                        QColor(255, 230, 245))

            result.append(code)

            self.rows_episode += 1

        self.table_episode.itemChanged.connect(self.item_changed)

    # Item Change
    def item_changed(self, item):
        """
        If code, title or summary is edited in  episode table change its
        values in list self.result_episode.

        :param item: A cell in table who is changed.
        """
        r = item.row()
        c = item.column() - 1
        self.result_episode[r][c] = self.table_episode. \
            item(item.row(), item.column()).text()

    # Star Changed
    def chbox_star_changed(self, ch):
        """
        Change the icon on chbox_stars on checkbox change.

        :param ch: QCheckBox from table who is in a list according rows.
        """
        ch_id = int(ch.text())

        icon = QIcon()
        if self.chbox_star[ch_id].isChecked():
            icon.addPixmap(
                QPixmap('images/star_yellow_16.png'), QIcon.Normal,
                QIcon.Off
            )
        else:
            icon.addPixmap(
                QPixmap('images/star_withe_16.png'), QIcon.Normal, QIcon.Off
            )

        self.chbox_star[ch_id].setIcon(icon)

    # Set combobox values
    def set_combobox_value(self, cb, obj, id):
        """
        Put the value corresponding to the series found in the QComboBox.

        :param cb: The QComboBox who need set value.
        :param obj: The object that name needs to be set in the QComboBox.
        :param id: The id to find object in database.
                """
        result = self.session.query(obj).filter(obj.id == id).one()
        index = cb.findText(result.name, Qt.MatchFixedString)
        cb.setCurrentIndex(index)

    # Clear Table Cast
    def clear_table_cast(self):
        """
        Clear table cast after insert season.
        """
        self.table_cast.clear()
        self.table_cast.setRowCount(0)
        self.table_cast.setColumnCount(4)
        self.table_cast.setHorizontalHeaderLabels(self.headers_cast)
        self.rows_cast = 0

    # Clear Table Episode
    def clear_table_episode(self):
        """
        Clear table episode.
        """
        self.table_episode.clear()
        self.table_episode.setRowCount(0)
        self.table_episode.setColumnCount(3)
        self.table_episode.setHorizontalHeaderLabels(self.headers_episode)
        self.rows_episode = 0

    # Clear All
    def clear(self):
        """
        Clear all input values after saving series in database or clear button
        is clicked.
        """
        self.cb_series.currentIndexChanged.disconnect()
        self.cb_season_num.currentIndexChanged.disconnect()
        self.cb_year.currentIndexChanged.disconnect()
        self.le_season_num.setText('')
        self.le_year.setText('')
        self.le_url_imdb.setText('')
        self.le_url_ms.setText('')
        self.cb_series.setCurrentIndex(0)
        self.cb_media.setCurrentIndex(0)
        self.cb_season_num.clear()
        self.cb_year.clear()
        self.clear_table_cast()
        self.clear_table_episode()
        self.season = None
        self.episodes_all = None
        self.result_episode = []
        self.cb_series.currentIndexChanged.connect(self.selected_series)

    # Help
    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_insert_edit_season.html'
        self.main.views_help(url, texts.help_insert_movie)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
