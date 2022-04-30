# Bookmarks bar port
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

bookmarks = []

_app = None

def formatUrl(url):
	if url.startswith("http://") or url.startswith("https://"):
		return url
	else:
		return "http://" + url

def blazeOnApplicationLoad(app, browser, name):
	# bookmark rack
	# where you can store websites for later use in the session
	app.bookmark_bar = QToolBar()
	# move and lock the bookmark bar to the bottom
	app.bookmark_bar.setAllowedAreas(Qt.BottomToolBarArea)
	#app.bookmark_bar.setMovable(False)
	app.bookmark_bar.setFloatable(False)
	app.addToolBar(app.bookmark_bar)

	# bookmark save button
	bookmark_save_btn = QAction("📁", app)
	bookmark_save_btn.triggered.connect(bookmarkSaveProcess)
	app.bookmark_bar.addAction(bookmark_save_btn)

	# bookmark remove button
	bookmark_remove_btn = QAction("🗑", app)
	bookmark_remove_btn.triggered.connect(bookmarkRemoveProcess)
	app.bookmark_bar.addAction(bookmark_remove_btn)

	# separator
	app.bookmark_bar.addSeparator()


	global _app
	_app = app

def blazeOnPageChange(app, browser, url, page):
	global _app
	_app = app

def bookmarkSaveProcess(event):
	global bookmarks, _app
	# get the url from the user
	url, ok = QInputDialog.getText(_app, "Save Bookmark", "URL:")
	if ok:
		url = formatUrl(url)
		# add bookmark to the bar
		bookmark_action = QAction(url, _app)
		bookmark_action.triggered.connect(lambda: _app.browser.setUrl(QUrl(url)))
		_app.bookmark_bar.addAction(bookmark_action)
		# add bookmark to var
		bookmarks.append(url)
	
def bookmarkRemoveProcess(event):
	global bookmarks, _app
	# if user is on a bookmark, remove it
	if _app.browser.url().toString() in bookmarks:
		# remove bookmark from bar
		for action in _app.bookmark_bar.actions():
			if action.text() == _app.browser.url().toString():
				_app.bookmark_bar.removeAction(action)
				break
		# remove bookmark from var
		bookmarks.remove(_app.browser.url().toString())
	# else, ask for url
	else:
		url, ok = QInputDialog.getText(_app, "Remove Bookmark", "URL:")
		if ok:
			url = formatUrl(url)
			# remove bookmark from bar
			for action in _app.bookmark_bar.actions():
				if action.text() == url:
					_app.bookmark_bar.removeAction(action)
					break
			# remove bookmark from var
			bookmarks.remove(url)