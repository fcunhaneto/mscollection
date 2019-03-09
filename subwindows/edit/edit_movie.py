import datetime
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QLabel, QMessageBox, \
    QSpacerItem, QSizePolicy, QTableWidgetItem

import texts

from db.db_model import Keyword, Director, Box, Movie, MovieCategory, \
    MovieDirector
from db.db_model import Media, Category
from db.db_settings import Database as DB

from lib.function_lib import le_create, cb_create, populate_combobox, \
    hbox_create, pb_create, table_cast_create, get_combobox_info, show_msg, \
    db_insert_obj, db_select_all, line_h_create, db_get_id, db_get_obj
from lib.write_ms_html import write_html


class EditMovie(QMdiSubWindow):
    def __init__(self, main):
        """
        Class for edit movie.

        :param main: Reference for main windows.
        """
        super(EditMovie, self).__init__()

        self.session = DB.get_session()
        self.movie = None
        self.cb_categories = []
        self.cast_values = []
        self.main = main

        windows_title = texts.edit + ' ' + texts.movie_p
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
        movies = db_select_all(self.session, Movie)
        self.lb_select = QLabel(texts.lb_edit_select_movie)
        self.cb_select = cb_create('')

        populate_combobox(self.cb_select, movies)

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

        # Year
        self.lb_year = QLabel(texts.year_s)
        self.le_year = le_create(4)
        self.fm_1.setWidget(1, QFormLayout.LabelRole, self.lb_year)
        self.fm_1.setWidget(1, QFormLayout.FieldRole, self.le_year)

        # Media
        self.lb_media = QLabel(texts.media_s)
        media = db_select_all(self.session, Media)
        self.cb_media = cb_create()
        populate_combobox(self.cb_media, media)
        self.fm_1.setWidget(2, QFormLayout.LabelRole, self.lb_media)
        self.fm_1.setWidget(2, QFormLayout.FieldRole, self.cb_media)

        # Category 1
        category = db_select_all(self.session, Category)
        self.lb_category_1 = QLabel(texts.category_1)
        cb_category_1 = cb_create()
        populate_combobox(cb_category_1, category)
        self.fm_1.setWidget(3, QFormLayout.LabelRole, self.lb_category_1)
        self.fm_1.setWidget(3, QFormLayout.FieldRole, cb_category_1)
        self.cb_categories.append(cb_category_1)

        # Box
        box = db_select_all(self.session, Box)
        self.lb_box = QLabel(texts.box)
        self.cb_box = cb_create()
        populate_combobox(self.cb_box, box)
        self.fm_1.setWidget(4, QFormLayout.LabelRole, self.lb_box)
        self.fm_1.setWidget(4, QFormLayout.FieldRole, self.cb_box)

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

        # Director
        director = db_select_all(self.session, Director)
        self.lb_director = QLabel(texts.director_s)
        self.cb_director = cb_create()
        populate_combobox(self.cb_director, director)
        self.fm_2.setWidget(1, QFormLayout.LabelRole, self.lb_director)
        self.fm_2.setWidget(1, QFormLayout.FieldRole, self.cb_director)

        self.lb_time = QLabel(texts.lb_time)
        self.le_time = le_create(10, texts.time_tt)
        self.le_time.setPlaceholderText(texts.time_tt)
        self.fm_2.setWidget(2, QFormLayout.LabelRole, self.lb_time)
        self.fm_2.setWidget(2, QFormLayout.FieldRole, self.le_time)

        # Category 2
        self.lb_category_2 = QLabel(texts.category_2)
        cb_category_2 = cb_create()
        populate_combobox(cb_category_2, category)
        self.fm_2.setWidget(3, QFormLayout.LabelRole, self.lb_category_2)
        self.fm_2.setWidget(3, QFormLayout.FieldRole, cb_category_2)
        self.cb_categories.append(cb_category_2)

        # KeyWord
        keyword = db_select_all(self.session, Keyword)
        self.lb_keyword = QLabel(texts.keyword)
        self.cb_keyword = cb_create()
        populate_combobox(self.cb_keyword, keyword)
        self.fm_2.setWidget(4, QFormLayout.LabelRole, self.lb_keyword)
        self.fm_2.setWidget(4, QFormLayout.FieldRole, self.cb_keyword)

        # Poster
        self.lb_poster = QLabel(texts.poster)
        self.le_poster = le_create(255)
        self.fm_2.setWidget(5, QFormLayout.LabelRole, self.lb_poster)
        self.fm_2.setWidget(5, QFormLayout.FieldRole, self.le_poster)

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
        self.pb_save.clicked.connect(self.edit_movie)
        self.pb_save.setShortcut('Ctrl+S')
        self.grid_layout.addWidget(self.pb_save, 0, 0, 1, 1)

        self.pb_delete = pb_create(texts.pb_delete, height=40)
        self.pb_delete.clicked.connect(self.delete_movie)
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
        self.setTabOrder(self.cb_categories[1], self.cb_box)
        self.setTabOrder(self.cb_box, self.cb_keyword)
        self.setTabOrder(self.cb_keyword, self.cb_director)
        self.setTabOrder(self.cb_director, self.le_poster)
        self.setTabOrder(self.le_poster, self.le_url)

        self.cb_select.currentIndexChanged.connect(self.fill_movie)

    # Edit Movie
    def edit_movie(self):
        """
        Save the edit to the database.
        """
        self.movie.name = self.le_title.text()
        if not self.movie.name:
            show_msg(texts.edit_error, texts.no_title, QMessageBox.Warning,
                     QMessageBox.Close)
            return

        self.movie.original_name = self.le_original_title.text()
        self.movie.year = self.le_year.text()
        self.movie.time = self.le_time.text()

        if self.le_poster.text():
            self.movie.poster = self.le_poster.text()
        else:
            path = os.getcwd()
            self.movie.poster = path + '/images/poster_placeholder.png'

        self.movie.url = self.le_url.text()
        self.movie.summary = self.le_summary.toPlainText()

        id, name = get_combobox_info(self.cb_media)
        self.movie.media_id = db_get_id(self.session, id, name,
                                        Media(name=name))

        id, name = get_combobox_info(self.cb_box)
        self.movie.box_id = db_get_id(self.session, id, name, Box(name=name))

        id, name = get_combobox_info(self.cb_keyword)
        self.movie.keyword_id = db_get_id(
            self.session, id, name, Keyword(name=name))

        for i in range(2):
            id, name = get_combobox_info(self.cb_categories[i])
            category = db_get_obj(self.session, id, name, Category)

            if category:
                self.session.query(MovieCategory). \
                    filter(MovieCategory.id == self.movie.categories[i].id). \
                    update({MovieCategory.category_id: category.id})

        id, name = get_combobox_info(self.cb_director)
        director = db_get_obj(self.session, id, name, Director)
        if director:
            self.session.query(MovieDirector). \
                filter(MovieDirector.id == self.movie.directors[0].id). \
                update({MovieDirector.director_id: director.id})

        self.movie.last_edit = self.movie.new_edit
        self.movie.new_edit = datetime.datetime.utcnow()

        result = db_insert_obj(self.session, self.movie)

        if result:
            text = texts.msg_edit_ok(self.movie.name)
            show_msg(texts.edit_ok, text, QMessageBox.Information,
                     QMessageBox.Close)
            self.clear()
            write_html(self.session, self.movie, 'movie')
        else:
            text = texts.msg_edit_erro(self.movie.name)
            show_msg(texts.edit_error, text, QMessageBox.Warning,
                     QMessageBox.Close)

    # Delete Movie
    def delete_movie(self):
        """
        Delete the movie in the database.
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
            self.movie = self.session.query(Movie).get(id)
            poster = self.movie.poster
            result = self.session.query(Movie).filter(Movie.id == id).delete()

        if result == 1:
            self.session.commit()
            text = texts.msg_delete_ok(name)
            show_msg(texts.delete_ok, text, QMessageBox.Information,
                     QMessageBox.Close)
            if os.path.exists(poster):
                os.remove(poster)
            self.clear()

    # Movie Selected
    def fill_movie(self):
        """
         After selecting the movie, fill in all the fields with values
         referring to the same.
         """
        self.cb_select.currentIndexChanged.disconnect()
        id, name = get_combobox_info(self.cb_select)

        self.movie = self.session.query(Movie).get(id)

        self.le_title.setText(self.movie.name)
        self.le_original_title.setText(self.movie.original_name)
        self.le_year.setText(self.movie.year)
        self.le_time.setText(self.movie.time)
        self.le_poster.setText(self.movie.poster)
        self.le_url.setText(self.movie.url)
        self.le_summary.setText(self.movie.summary)

        if self.movie.media_id:
            self.set_combobox_value(self.cb_media, Media, self.movie.media_id)
        else:
            self.cb_media.setItemText(0, '')

        if self.movie.box_id:
            self.set_combobox_value(self.cb_box, Box, self.movie.box_id)
        else:
            self.cb_box.setItemText(0, '')

        if self.movie.keyword_id:
            self.set_combobox_value(
                self.cb_keyword, Keyword, self.movie.keyword_id)
        else:
            self.cb_keyword.setItemText(0, '')

        if self.movie.categories:
            total = len(self.movie.categories)
            if total > 2:
                total = 2

            for i in range(total):
                id = self.movie.categories[i].category_id
                self.set_combobox_value(self.cb_categories[i], Category, id)

        if self.movie.directors:
            id = self.movie.directors[0].director_id
            if id:
                self.set_combobox_value(self.cb_director, Director, id)

        if self.movie.movie_cast:
            total = len(self.movie.movie_cast)
            for i in range(total):
                actor = self.movie.movie_cast[i].cast.actors.name
                character = self.movie.movie_cast[i].cast.characters.name
                self.table_add_rows(actor, character,
                                    self.movie.movie_cast[i].star)

        self.combo_flag = True

    # Clear
    def clear(self):
        """
        Clears all values in the fields and also in the table.
        """
        self.le_title.setText('')
        self.le_original_title.setText('')
        self.le_year.setText('')
        self.le_poster.setText('')
        self.le_url.setText('')
        self.le_summary.setText('')
        movie = db_select_all(self.session, Movie)
        populate_combobox(self.cb_select, movie)
        media = db_select_all(self.session, Media)
        populate_combobox(self.cb_media, media)
        box = db_select_all(self.session, Box)
        populate_combobox(self.cb_box, box)
        keyword = db_select_all(self.session, Keyword)
        populate_combobox(self.cb_keyword, keyword)
        category = db_select_all(self.session, Category)
        populate_combobox(self.cb_categories[0], category)
        populate_combobox(self.cb_categories[1], category)
        director = db_select_all(self.session, Director)
        populate_combobox(self.cb_director, director)
        self.clear_table()
        self.cb_select.currentIndexChanged.connect(self.fill_movie)

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
    def table_add_rows(self, actor, character, movie_star):
        """
        Add new row in table.

        :param actor: actor name
        :param character: character name
        :param movie_star: start bool value
        """
        self.table.insertRow(self.rows)

        self.table.setItem(self.rows, 0, QTableWidgetItem(actor))
        self.table.setItem(self.rows, 1, QTableWidgetItem(character))
        if movie_star:
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
        Put the value corresponding to the movie found in the QComboBox.

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
        self.main.views_help(url, texts.help_edit_movie)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
