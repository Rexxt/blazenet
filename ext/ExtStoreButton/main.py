# adds a button to the navigation bar to open the extension store
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import QUrl

url = "https://rexxt.github.io/blazenet/extensions"

def blazeOnApplicationLoad(app, browser, name):
    # create the action
    action = QAction('Extension Store', app)
    # connect the action to the extension store
    action.triggered.connect(lambda: browser.setUrl(QUrl(url)))
    # add the action to the navigation bar
    app.navbar.addAction(action)