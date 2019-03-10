from PyQt5.QtCore import QRect, QUrl
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView


# TODO Passar isso para uma janela simples sem uso do QWebEngineView
# porque quando do upgrade da placa de vídeo erros podem ocorrer
class ViewSelectTitle(QMdiSubWindow):
    def __init__(self, url, title):
        """
        Show html view movie or series by given view url.
        :param url: The view url.
        :param title: The windows title.
        """
        super(ViewSelectTitle, self).__init__()

        self.setWindowTitle(title)
        self.setGeometry(QRect(0, 0, 750, 620))

        self.webView = QWebEngineView()
        self.setWidget(self.webView)
        self.webView.setUrl(QUrl(url))
        self.webView.show()



