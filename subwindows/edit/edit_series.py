import datetime
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QLabel, QMessageBox, \
    QSpacerItem, QSizePolicy, QTableWidgetItem

import texts

from db.db_model import Creator, Series, SeriesCategory, SeriesCreator
from db.db_model import Keyword, Media, Category
from db.db_settings import Database as DB

from lib.function_lib import le_create, cb_create, \
    populate_combobox, hbox_create, pb_create, table_cast_create, \
    get_combobox_info, show_msg, db_insert_obj, db_select_all, line_h_create, \
    db_get_id, db_get_obj
from lib.write_ms_html import write_html


class EditSeries(QMdiSubWindow):
    def __init__(self, main):
        """
        Class for edit series.

        :param main: Reference for main windows.
        """
        super(EditSeries, self).__init__()

        self.session = DB.get_session()
        self.series = None
        self.cb_categories = []
        self.cast_values = []
        self.main = main

        windows_title = texts.edit + ' ' + texts.series_p
        self.setWindowTitle(windows_title)
        width = int(0.95 * main.frameSize().width())
        height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, width, height)
        col_default = int(width / 5)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)

        # Select Label and Combobox
        series = db_select_all(self.session, Series)
        self.lb_select = QLabel(texts.lb_edit_select_series)
        self.cb_select = cb_create('')

        populate_combobox(self.cb_select, series)

        self.hbox_select_widget = QWidget(self.subwindow)
        self.hbox_select = hbox_create([self.lb_select, self.cb_select])
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.hbox_select.addItem(spacer_item)

        self.hbox_select.setContentsMargins(20, 20, 20, 0)

        self.line = line_h_create('2px', '#000000')

        self.vbox_main.addLayout(self.hbox_select)
        self.vbox_main.addWidget(self.line)

        # Form Layout 1
        self.fm_1 = QFormLayout()
        self.fm_1.setContentsMargins(20, 20, 20, 20)
        self.fm_1.setSpacing(10)

        # Title
        self.lb_title = QLabel(texts.title_s)
        self.le_title = le_create()
        self.fm_1.setWidget(0, QFormLayout.LabelRole, self.lb_title)
        self.fm_1.setWidget(0, QFormLayout.FieldRole, self.le_title)

        # Year/Media
        self.lb_year = QLabel(texts.year_s)
        self.le_year = le_create(4)
        self.fm_1.setWidget(1, QFormLayout.LabelRole, self.lb_year)
        self.fm_1.setWidget(1, QFormLayout.FieldRole, self.le_year)

        # Category 1
        category = db_select_all(self.session, Category)
        self.lb_category_1 = QLabel(texts.category_1)
        cb_category_1 = cb_create()
        populate_combobox(cb_category_1, category)
        self.fm_1.setWidget(2, QFormLayout.LabelRole, self.lb_category_1)
        self.fm_1.setWidget(2, QFormLayout.FieldRole, cb_category_1)
        self.cb_categories.append(cb_category_1)

        # Seasons
        self.lb_season = QLabel(texts.season_p)
        self.le_season = le_create()
        self.fm_1.setWidget(3, QFormLayout.LabelRole, self.lb_season)
        self.fm_1.setWidget(3, QFormLayout.FieldRole, self.le_season)

        # Creator
        creator = db_select_all(self.session, Creator)
        self.lb_creator = QLabel(texts.creator_s)
        self.cb_creator = cb_create()
        populate_combobox(self.cb_creator, creator)
        self.fm_1.setWidget(4, QFormLayout.LabelRole, self.lb_creator)
        self.fm_1.setWidget(4, QFormLayout.FieldRole, self.cb_creator)

        # Web URL
        self.lb_url = QLabel(texts.lb_url)
        self.le_url = le_create(255)
        self.fm_1.setWidget(5, QFormLayout.LabelRole, self.lb_url)
        self.fm_1.setWidget(5, QFormLayout.FieldRole, self.le_url)

        # Form Layout 2
        self.fm_2 = QFormLayout()
        self.fm_2.setContentsMargins(20, 20, 20, 20)
        self.fm_2.setSpacing(10)

        # Original Title
        self.lb_original_title = QLabel(texts.original_title_s)
        self.le_original_title = le_create()
        self.fm_2.setWidget(0, QFormLayout.LabelRole, self.lb_original_title)
        self.fm_2.setWidget(0, QFormLayout.FieldRole, self.le_original_title)

        # Media
        self.lb_media = QLabel(texts.media_s)
        media = db_select_all(self.session, Media)
        self.cb_media = cb_create()
        populate_combobox(self.cb_media, media)
        self.fm_2.setWidget(1, QFormLayout.LabelRole, self.lb_media)
        self.fm_2.setWidget(1, QFormLayout.FieldRole, self.cb_media)

        # Category 2
        self.lb_category_2 = QLabel(texts.category_2)
        cb_category_2 = cb_create()
        populate_combobox(cb_category_2, category)
        self.fm_2.setWidget(2, QFormLayout.LabelRole, self.lb_category_2)
        self.fm_2.setWidget(2, QFormLayout.FieldRole, cb_category_2)
        self.cb_categories.append(cb_category_2)

        # KeyWord
        keyword = db_select_all(self.session, Keyword)
        self.lb_keyword = QLabel(texts.keyword)
        self.cb_keyword = cb_create()
        populate_combobox(self.cb_keyword, keyword)
        self.fm_2.setWidget(3, QFormLayout.LabelRole, self.lb_keyword)
        self.fm_2.setWidget(3, QFormLayout.FieldRole, self.cb_keyword)

        # Poster
        self.lb_poster = QLabel(texts.poster)
        self.le_poster = le_create(255)
        self.fm_2.setWidget(4, QFormLayout.LabelRole, self.lb_poster)
        self.fm_2.setWidget(4, QFormLayout.FieldRole, self.le_poster)

        # Horizontal Layout for Frame layout
        self.hbox_fms = QHBoxLayout()
        self.hbox_fms.addLayout(self.fm_1)
        self.hbox_fms.addLayout(self.fm_2)

        self.vbox_main.addLayout(self.hbox_fms)

        # Cast Summary
        self.hbox_summary_cast = hbox_create([], 0)
        self.hbox_summary_cast.setContentsMargins(20, 0, 20, 0)
        self.vbox_summary = QVBoxLayout()

        # Summary
        self.lb_summary = QLabel(texts.summary_s)
        self.le_summary = QTextEdit()
        self.vbox_summary.addWidget(self.lb_summary)
        self.vbox_summary.addWidget(self.le_summary)
        self.vbox_summary.setSpacing(20)
        self.hbox_summary_cast.addLayout(self.vbox_summary)
        self.hbox_summary_cast.setSpacing(20)

        # Cast Label Button
        self.vbox_cast = QVBoxLayout()

        self.lb_cast = QLabel()
        self.lb_cast.setText(texts.lb_no_edit_cast)

        self.hbox_cast = hbox_create([self.lb_cast])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_cast.addItem(spacer)

        self.vbox_cast.addLayout(self.hbox_cast)

        # Cast Table
        self.headers = [
            texts.actor_s.lower(),
            texts.character_s.lower(),
            texts.star.lower()
        ]
        self.table = table_cast_create(self.headers)
        self.table.setColumnWidth(0, col_default)
        self.table.setColumnWidth(1, col_default)
        self.table.setColumnWidth(2, 40)

        self.vbox_cast.addWidget(self.table)
        self.hbox_summary_cast.addLayout(self.vbox_cast)

        self.rows = 0

        self.vbox_main.addLayout(self.hbox_summary_cast)

        # Buttons Save Clear
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)

        self.pb_save = pb_create(texts.pb_save, height=40)
        self.pb_save.clicked.connect(self.edit_series)
        self.pb_save.setShortcut('Ctrl+S')
        self.grid_layout.addWidget(self.pb_save, 0, 0, 1, 1)

        self.pb_delete = pb_create(texts.pb_delete, height=40)
        self.pb_delete.clicked.connect(self.delete_series)
        self.pb_delete.setShortcut('Ctrl+Shift+D')
        self.grid_layout.addWidget(self.pb_delete, 0, 1, 1, 1)

        self.pb_clear = pb_create(texts.pb_clear, height=40)
        self.pb_clear.clicked.connect(self.clear)
        self.pb_clear.setShortcut('Ctrl+L')
        self.grid_layout.addWidget(self.pb_clear, 0, 2, 1, 1)

        self.pb_help = pb_create(texts.pb_help, height=40)
        self.pb_help.clicked.connect(self.help)
        self.pb_help.setShortcut('Ctrl+H')
        self.grid_layout.addWidget(self.pb_help, 0, 3, 1, 1)

        self.pb_leave = pb_create(texts.pb_leave, height=40)
        self.pb_leave.clicked.connect(self.close)
        self.pb_leave.setShortcut('Ctrl+E')
        self.grid_layout.addWidget(self.pb_leave, 0, 4, 1, 1)

        self.vbox_main.addLayout(self.grid_layout)

        # Tab Order
        self.le_title.setFocus()
        self.setTabOrder(self.le_title, self.le_original_title)
        self.setTabOrder(self.le_original_title, self.le_year)
        self.setTabOrder(self.le_year, self.cb_media)
        self.setTabOrder(self.cb_media, self.cb_categories[0])
        self.setTabOrder(self.cb_categories[0], self.cb_categories[1])
        self.setTabOrder(self.cb_categories[1], self.le_season)
        self.setTabOrder(self.le_season, self.cb_keyword)
        self.setTabOrder(self.cb_keyword, self.cb_creator)
        self.setTabOrder(self.cb_creator, self.le_poster)
        self.setTabOrder(self.le_poster, self.le_url)

        self.cb_select.currentIndexChanged.connect(self.fill_series)

    # Edit Series
    def edit_series(self):
        """
        Save the edit to the database.
        """
        self.series.name = self.le_title.text()
        if not self.series.name:
            show_msg(texts.edit_error, texts.no_title, QMessageBox.Warning,
                     QMessageBox.Close)
            return

        self.series.original_name = self.le_original_title.text()
        self.series.year = self.le_year.text()
        self.series.seasons = self.le_season.text()

        if self.le_poster.text():
            self.series.poster = self.le_poster.text()
        else:
            path = os.getcwd()
            self.movie.series = path + '/images/poster_placeholder.png'

        self.series.url = self.le_url.text()
        self.series.summary = self.le_summary.toPlainText()

        id, name = get_combobox_info(self.cb_media)
        self.series.media_id = db_get_id(self.session, id, name,
                                         Media(name=name))

        id, name = get_combobox_info(self.cb_keyword)
        self.series.keyword_id = db_get_id(self.session, id, name,
                                        Keyword(name=name))

        for i in range(2):
            id, name = get_combobox_info(self.cb_categories[i])
            category = db_get_obj(self.session, id, name, Category)

            if category:
                self.session.query(SeriesCategory). \
                    filter(SeriesCategory.id == self.series.categories[i].id). \
                    update({SeriesCategory.category_id: category.id},
                           synchronize_session=False)

        id, name = get_combobox_info(self.cb_creator)
        creator = db_get_obj(self.session, id, name, Creator)
        if creator:
            self.session.query(SeriesCreator). \
                filter(SeriesCreator.id == self.series.creators[0].id). \
                update({SeriesCreator.creator_id: creator.id},
                       synchronize_session=False)

        self.series.last_edit = self.series.new_edit
        self.series.new_edit = datetime.datetime.utcnow()

        result = db_insert_obj(self.session, self.series)

        if result:
            text = texts.msg_edit_ok(self.series.name)
            show_msg(texts.edit_ok, text, QMessageBox.Information,
                     QMessageBox.Close)
            self.clear()
            write_html(self.session, self.series, 'series')
        else:
            text = texts.msg_edit_erro(self.series.name)
            show_msg(texts.edit_error, text, QMessageBox.Warning,
                     QMessageBox.Close)

    # Delete Series
    def delete_series(self):
        """
        Delete the series in the database.
        """
        result = 0
        poster = ''
        id, name = get_combobox_info(self.cb_select)
        text = texts.msg_before_delete(name)
        answer = QMessageBox.information(
            self, texts.warning,
            text, QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if answer == QMessageBox.Yes:
            self.series = self.session.query(Series).get(id)
            poster = self.series.poster
            result = self.session.query(Series).filter(Series.id == id).delete()

        if result == 1:
            self.session.commit()
            text = texts.msg_delete_ok(name)
            show_msg(texts.delete_ok, text, QMessageBox.Information,
                     QMessageBox.Close)
            if os.path.exists(poster):
                os.remove(poster)
            self.clear()

    # Series Selected
    def fill_series(self):
        """
        After selecting the series, fill in all the fields with values
        referring to the same.
        """
        self.cb_select.currentIndexChanged.disconnect()
        id, name = get_combobox_info(self.cb_select)

        self.series = self.session.query(Series).get(id)

        self.le_title.setText(self.series.name)
        self.le_original_title.setText(self.series.original_name)
        self.le_year.setText(self.series.year)
        self.le_season.setText(self.series.seasons)
        self.le_poster.setText(self.series.poster)
        self.le_url.setText(self.series.url)
        self.le_summary.setText(self.series.summary)

        if self.series.media_id:
            self.set_combobox_value(self.cb_media, Media, self.series.media_id)
        else:
            self.cb_media.setItemText(0, '')

        if self.series.keyword_id:
            self.set_combobox_value(
                self.cb_keyword, Keyword, self.series.keyword_id)
        else:
            self.cb_keyword.setItemText(0, '')

        if self.series.categories:
            total = len(self.series.categories)
            if total > 2:
                total = 2
            for i in range(total):
                id = self.series.categories[i].category_id
                self.set_combobox_value(self.cb_categories[i], Category, id)

        if self.series.creators:
            id = self.series.creators[0].creator_id
            if id:
                self.set_combobox_value(self.cb_creator, Creator, id)

        if self.series.series_cast:
            total = len(self.series.series_cast)
            for i in range(total):
                actor = self.series.series_cast[i].cast.actors.name
                character = self.series.series_cast[i].cast.characters.name
                self.table_add_rows(
                    actor, character, self.series.series_cast[i].star
                )

        self.combo_flag = True

    # Clear
    def clear(self):
        """
        Clears all values in the fields and also in the table.
        """
        self.le_title.setText('')
        self.le_original_title.setText('')
        self.le_year.setText('')
        self.le_season.setText('')
        self.le_poster.setText('')
        self.le_url.setText('')
        self.le_summary.setText('')
        series = db_select_all(self.session, Series)
        populate_combobox(self.cb_select, series)
        media = db_select_all(self.session, Media)
        populate_combobox(self.cb_media, media)
        category = db_select_all(self.session, Category)
        populate_combobox(self.cb_categories[0], category)
        populate_combobox(self.cb_categories[1], category)
        creator = db_select_all(self.session, Creator)
        populate_combobox(self.cb_creator, creator)
        self.clear_table()
        self.cb_select.currentIndexChanged.connect(self.fill_series)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.rows = 0

    # Table add rows
    def table_add_rows(self, actor, character, series_star):
        """
        Add new row in table.

        :param actor: Actor name.
        :param character: Character name.
        :param movie_star: Start bool value.
        """
        self.table.insertRow(self.rows)

        self.table.setItem(self.rows, 0, QTableWidgetItem(actor))
        self.table.setItem(self.rows, 1, QTableWidgetItem(character))
        if series_star:
            icon = QIcon()
            icon.addPixmap(
                QPixmap('images/star_yellow_16.png'), QIcon.Normal, QIcon.Off
            )
            star = QTableWidgetItem()
            star.setIcon(icon)
            self.table.setItem(self.rows, 2, star)

        for i in range(2):
            self.table.item(self.rows, i).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.rows += 1

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

    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_edit_movie_series.html'
        self.main.views_help(url, texts.help_edit_series)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
