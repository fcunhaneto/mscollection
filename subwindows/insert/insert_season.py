import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, QVBoxLayout, \
    QHBoxLayout, QLabel, QComboBox, QSpacerItem, QSizePolicy, QTableWidget, \
    QCheckBox, QTableWidgetItem, QMessageBox, QProgressBar
from sqlalchemy.exc import IntegrityError, DBAPIError

import texts

from db.db_model import Actor, Character, Cast, Media, Series, SeriesCast
from db.db_model import Season, SeasonCast, Episode
from db.db_settings import Database as DB

from lib.episodes_scraping import episodes_scraping_imdb, episodes_scraping_ms
from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    get_combobox_info, show_msg, db_select_all, line_h_create, line_v_create, \
    le_create, db_get_id, pb_create


class InsertSeason(QMdiSubWindow):
    """
    Class to provide all methods to insert seasons and episodes in database
    """
    def __init__(self, main):
        super(InsertSeason, self).__init__()

        self.session = DB.get_session()
        self.cb_categories = []
        self.main = main

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

        # Series Left
        self.hbox_2 = QHBoxLayout()
        self.hbox_2.setSpacing(10)

        # Series Left Side
        self.fm_left = QFormLayout()
        self.fm_left.setSpacing(10)
        self.fm_left.setContentsMargins(0, 0, 5, 0)

        # Series
        self.lb_series = QLabel(texts.series_s)
        series = db_select_all(self.session, Series)
        self.cb_series = QComboBox()
        populate_combobox(self.cb_series, series)

        self.fm_left.setWidget(0, QFormLayout.LabelRole,
                               self.lb_series)
        self.fm_left.setWidget(0, QFormLayout.FieldRole,
                               self.cb_series)

        # Season Num Year
        text = texts.season_s + '/' + texts.year_s
        self.lb_season = QLabel(text)
        self.le_season_num = le_create(tooltip=texts.season_num_tt)
        self.le_season_num.setPlaceholderText(texts.season_num)

        self.le_year = le_create(4)
        self.le_year.setPlaceholderText(texts.year_s)

        self.fm_left.setWidget(1, QFormLayout.LabelRole,
                               self.lb_season)
        self.hbox_ny = hbox_create([self.le_season_num, self.le_year])
        self.fm_left.setLayout(1, QFormLayout.FieldRole, self.hbox_ny)

        # Media
        self.lb_media = QLabel(texts.media_s)
        media = db_select_all(self.session, Media)
        self.cb_media = QComboBox()
        populate_combobox(self.cb_media, media)

        self.fm_left.setWidget(2, QFormLayout.LabelRole,
                               self.lb_media)
        self.fm_left.setWidget(2, QFormLayout.FieldRole,
                               self.cb_media)

        # IMDB URL
        self.lb_url_imdb = QLabel(texts.lb_search_season_imdb)
        self.le_url_imdb = le_create()
        self.le_url_imdb.returnPressed.connect(lambda site='imdb':
                                               self.scraping_episodes(site))

        self.fm_left.setWidget(3, QFormLayout.LabelRole, self.lb_url_imdb)
        self.fm_left.setWidget(3, QFormLayout.FieldRole, self.le_url_imdb)

        # Minha Série URL
        self.lb_urL_ms = QLabel(texts.lb_search_season_ms)
        self.le_url_ms = le_create(tooltip=texts.ms_episode_search)
        self.le_url_ms.returnPressed.connect(lambda site='ms':
                                             self.scraping_episodes(site))

        self.fm_left.setWidget(4, QFormLayout.LabelRole, self.lb_urL_ms)
        self.fm_left.setWidget(4, QFormLayout.FieldRole, self.le_url_ms)

        # PB Search
        self.lb_episode_search = QLabel(texts.lb_episode_search)
        self.fm_left.setWidget(5, QFormLayout.LabelRole, self.lb_episode_search)

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
        self.fm_left.setLayout(5, QFormLayout.FieldRole,
                               self.hbox_url_pb)

        # PB Main
        line_h_1 = line_h_create('2px', '#7777FF')
        line_h_2 = line_h_create('2px', '#7777FF')
        self.fm_left.setWidget(6, QFormLayout.FieldRole, line_h_1)
        self.fm_left.setWidget(7, QFormLayout.FieldRole, line_h_2)
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

        self.pb_leave = pb_create(texts.pb_leave)
        self.pb_leave.clicked.connect(self.close)
        self.pb_leave.setShortcut('Ctrl+Q')

        self.hbox_pb_main.addWidget(self.pb_save)
        self.hbox_pb_main.addWidget(self.pb_clear)
        self.hbox_pb_main.addWidget(self.pb_help)
        self.hbox_pb_main.addWidget(self.pb_leave)

        self.fm_left.setLayout(8, QFormLayout.FieldRole, self.hbox_pb_main)

        # Series Right Size
        self.vbox_right = QVBoxLayout(self.subwindow)
        self.vbox_right.setContentsMargins(5, 0, 0, 0)

        # Cast Add Row
        self.hbox_cast = QHBoxLayout()

        self.lb_cast = QLabel(texts.cast_s)
        self.pb_add_row_cast = pb_create('+', 12, 30, 50)
        self.pb_add_row_cast.setShortcut('CTRL+T')
        self.pb_add_row_cast.clicked.connect(self.table_cast_add_rows)

        self.hbox_cast.addWidget(self.lb_cast)
        self.hbox_cast.addWidget(self.pb_add_row_cast)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_cast.addItem(spacer_item)

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
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []
        self.table_cast_add_rows()

        self.vbox_right.addLayout(self.hbox_cast)
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
            texts.code,
            texts.title_s,
            texts.summary_s,
        ]
        self.table_episode.setHorizontalHeaderLabels(self.headers_episode)

        self.table_episode.setColumnWidth(0, 0.05 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(1, 0.20 * self.tb_witdh_episode)
        self.table_episode.setColumnWidth(2, 0.70 * self.tb_witdh_episode)

        self.table_episode.setAlternatingRowColors(True)
        self.table_episode.setStyleSheet('alternate-background-color: #E6E6E6;')
        
        self.rows_episode = 0
        self.result_episode = None
        self.table_episode.itemChanged.connect(self.item_changed)

        line_h_2 = line_h_create('2px', '#000000')

        self.vbox_episode.addLayout(self.hbox_episode)
        self.vbox_episode.addWidget(self.table_episode)
        self.vbox_main.addWidget(line_h_2)
        self.vbox_main.addLayout(self.vbox_episode)

        self.cb_series.currentIndexChanged.connect(self.selected_series)

        self.errors = {
            'no error': 1,
            'no cast': 2,
            'db error': 3,
        }

        self.cb_series.setFocus()

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

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Save Season Episodes
    def save_season_episodes(self):
        """
        Saved season and episodes in database.

        :return: errors when inserting into the database or ok if not errors
        """
        id_s, name_s = get_combobox_info(self.cb_series)
        id_m, name_m = get_combobox_info(self.cb_media)
        if id_m != 0:
            season = Season(series_id=id_s,
                            season_num=self.le_season_num.text(),
                            year=self.le_year.text(), media_id=id_m)
        else:
            season = Season(series_id=id_s,
                            season_num=self.le_season_num.text(),
                            year=self.le_year.text())
        try:
            self.session.add(season)
            self.session.commit()
        except (IntegrityError, DBAPIError) as error:
            self.session.rollback()
            self.session.commit()

            return self.errors['db error'], name_s

        episodes = []
        for result in self.result_episode:
            episode = Episode(season_id=season.id, code=result[2],
                              name=result[0], summary=result[1])
            episodes.append(episode)

        try:
            self.session.add_all(episodes)
            self.session.commit()
        except (IntegrityError, DBAPIError) as error:
            self.session.rollback()
            self.session.commit()

            return self.errors['db error'], name_s

        i = 0
        old_order = 0
        seasons_cast = []
        for cb in self.cb_actor:
            id, name = get_combobox_info(cb)
            actor_id = db_get_id(self.session, id, name, Actor(name=name))

            id, name = get_combobox_info(self.cb_character[i])
            character_id = db_get_id(
                self.session, id, name, Character(name=name)
            )

            if actor_id and character_id:
                cast = Cast(actor_id=actor_id, character_id=character_id)
                try:
                    self.session.add(cast)
                    self.session.commit()
                # If except most probably is because cast exist so we try to get it
                except IntegrityError:
                    self.session.rollback()
                    self.session.commit()
                    cast = self.session.query(Cast).filter(
                        Cast.actor_id == actor_id,
                        Cast.character_id == character_id).first()

                if cast:
                    order = int(self.le_order[i].text())
                    if order == old_order:
                        order += 1
                        old_order = order
                    else:
                        old_order = order

                    season_cast = SeasonCast(
                        season_id=season.id,
                        cast_id=cast.id,
                        order=order,
                        star=self.chbox_star[i].isChecked()
                    )
                    seasons_cast.append(season_cast)

            i += 1

        try:
            self.session.add_all(seasons_cast)
            self.session.commit()
        except (IntegrityError, DBAPIError) as error:
            self.session.rollback()
            self.session.commit()

            return self.errors['no cast'], name_s

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
        elif error == self.errors['no cast']:
            text = texts.msg_edit_erro(texts.cast_s)
            show_msg(texts.insert_error, text, QMessageBox.Critical,
                     QMessageBox.Close, str(error))
            text = texts.msg_edit_erro(texts.season_s)
            show_msg(texts.insert_ok, text, QMessageBox.Information,
                     QMessageBox.Close)
        elif error == self.errors['no error']:
            text = texts.msg_insert_season_ok(name, self.le_season_num.text())
            show_msg(texts.insert_ok, text, QMessageBox.Information,
                     QMessageBox.Close)

        self.clear()

    # Selected Series
    def selected_series(self):
        """
        Get values in SeriesCast to fill table cast.
        """
        id, name = get_combobox_info(self.cb_series)
        query = self.session.query(SeriesCast). \
            filter(SeriesCast.series_id == id).all()
        for q in query:
            self.populated_table_cast(q.cast.actors.name,
                                      q.cast.characters.name)

    # Populate Cast Table
    def populated_table_cast(self, ac_name, ch_name):
        """
        Populate table cast.

        :param ac_name: Actor name.
        :param ch_name: Character name.
        """
        cb = cb_create()
        actor = self.session.query(Actor).order_by(Actor.name).all()
        populate_combobox(cb, actor)
        self.cb_actor.append(cb)
        index = cb.findText(ac_name, Qt.MatchFixedString)
        self.cb_actor[self.rows_cast - 1].setCurrentIndex(index)

        cb = cb_create()
        character = self.session.query(Character). \
            order_by(Character.name).all()
        populate_combobox(cb, character)
        self.cb_character.append(cb)
        index = cb.findText(ch_name, Qt.MatchFixedString)
        self.cb_character[self.rows_cast - 1].setCurrentIndex(index)

        le = le_create(5)
        le.setStyleSheet('padding: 10px;')
        self.le_order.append(le)
        self.le_order[self.rows_cast].setText(str(self.rows_cast + 1))

        ch = QCheckBox(str(self.rows_cast))
        icon = QIcon()
        icon.addPixmap(
            QPixmap('images/star_withe_16.png'), QIcon.Normal, QIcon.Off
        )
        ch.setIcon(icon)
        ch.setToolTip(texts.rb_star_tt)
        self.chbox_star.append(ch)
        i = self.rows_cast
        self.chbox_star[i].stateChanged. \
            connect(lambda: self.chbox_star_changed(self.chbox_star[i]))

        i = self.rows_cast
        hb = hbox_create([self.chbox_star[i]], 0)
        hb.setAlignment(Qt.AlignCenter)
        cell = QWidget()
        cell.setLayout(hb)

        self.table_cast.insertRow(self.rows_cast)
        self.table_cast.setCellWidget(self.rows_cast, 0,
                                      self.cb_actor[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 1,
                                      self.cb_character[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 2,
                                      self.le_order[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 3, cell)

        if self.rows_cast % 2 != 0:
            self.table_cast.cellWidget(self.rows_cast, 0).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table_cast.cellWidget(self.rows_cast, 1).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table_cast.cellWidget(self.rows_cast, 2).setStyleSheet(
                'background-color: #E6E6E6; padding-left:10px;'
            )
            self.table_cast.cellWidget(self.rows_cast, 3).setStyleSheet(
                'background-color: #E6E6E6;'
                'color: #E6E6E6;'
            )
        else:
            self.table_cast.cellWidget(self.rows_cast, 3).setStyleSheet(
                'color: #FFFFFF;'
            )

        self.table_cast.setRowHeight(self.rows_cast, 35)

        self.rows_cast += 1

    # Table Cast Add Rows
    def table_cast_add_rows(self):
        """
        Add rows in table cast.
        """
        cb = cb_create()
        actor = self.session.query(Actor).order_by(Actor.name).all()
        populate_combobox(cb, actor)
        self.cb_actor.append(cb)

        cb = cb_create()
        character = self.session.query(Character). \
            order_by(Character.name).all()
        populate_combobox(cb, character)
        self.cb_character.append(cb)

        le = le_create(5)
        le.setStyleSheet('padding: 10px;')
        self.le_order.append(le)
        self.le_order[self.rows_cast].setText(str(self.rows_cast + 1))

        ch = QCheckBox(str(self.rows_cast))
        icon = QIcon()
        icon.addPixmap(
            QPixmap('images/star_withe_16.png'), QIcon.Normal, QIcon.Off
        )
        ch.setIcon(icon)
        ch.setToolTip(texts.rb_star_tt)
        self.chbox_star.append(ch)
        i = self.rows_cast
        self.chbox_star[i].stateChanged. \
            connect(lambda: self.chbox_star_changed(self.chbox_star[i]))

        i = self.rows_cast
        hb = hbox_create([self.chbox_star[i]], 0)
        hb.setAlignment(Qt.AlignCenter)
        cell = QWidget()
        cell.setLayout(hb)

        self.table_cast.insertRow(self.rows_cast)
        self.table_cast.setCellWidget(self.rows_cast, 0,
                                      self.cb_actor[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 1,
                                      self.cb_character[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 2,
                                      self.le_order[self.rows_cast])
        self.table_cast.setCellWidget(self.rows_cast, 3, cell)

        if self.rows_cast % 2 != 0:
            self.table_cast.cellWidget(self.rows_cast, 0).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table_cast.cellWidget(self.rows_cast, 1).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table_cast.cellWidget(self.rows_cast, 2).setStyleSheet(
                'background-color: #E6E6E6; padding-left:10px;'
            )
            self.table_cast.cellWidget(self.rows_cast, 3).setStyleSheet(
                'background-color: #E6E6E6;'
                'color: #E6E6E6;'
            )
        else:
            self.table_cast.cellWidget(self.rows_cast, 3).setStyleSheet(
                'color: #FFFFFF;'
            )

        self.table_cast.setRowHeight(self.rows_cast, 35)

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

    # Search Episode and Set Table
    def scraping_episodes(self, site):
        """
        Get episodes title and summary in IMDB or Minha Séries site.

        :param site: If value is "ms" scrapping from "Minha Série" else
        scrapping from "IMDB".
        """
        self.table_episode.itemChanged.disconnect()

        if site == 'ms':
            self.result_episode = episodes_scraping_ms(self.le_url_ms.text(),
                                                       self.p_bar)
        else:
            self.result_episode = episodes_scraping_imdb(
                self.le_url_imdb.text(), self.p_bar)

        for result in self.result_episode:
            self.table_episode.insertRow(self.rows_episode)
            self.table_episode.setRowHeight(self.rows_episode, 150)

            ep_num = self.rows_episode + 1
            code = '{0:0>2d}.{1:0>2d}'.format(int(self.le_season_num.text()),
                                              ep_num)

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
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []

        self.table_cast_add_rows()

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
        self.le_season_num.setText('')
        self.le_year.setText('')
        self.le_url_imdb.setText('')
        self.le_url_ms.setText('')
        self.cb_series.setCurrentIndex(0)
        self.cb_media.setCurrentIndex(0)
        self.p_bar.setValue(0)
        self.clear_table_cast()
        self.clear_table_episode()

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
