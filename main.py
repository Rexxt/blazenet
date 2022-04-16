# light, reliable, extensible web browser

BN_VERSION = "0.0.1"

import sys, os, json, requests, zipfile, io
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from settings import SettingsWindow

conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
conf = json.load(open(conf_path))

def formatUrl(url):
	if url.startswith("http://") or url.startswith("https://"):
		return url
	else:
		return "http://" + url

def deepcopy(obj):
	new_obj = {}
	for key, value in obj.items():
		if isinstance(value, dict):
			new_obj[key] = deepcopy(value)
		else:
			new_obj[key] = value
	return new_obj

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Blazenet")
		self.setGeometry(100, 100, 800, 600)

		self.browser = QWebEngineView()
		# Open DuckDuckGo
		self.browser.setUrl(QUrl(conf["homepage"]))
		self.setCentralWidget(self.browser)

		# navbar
		self.navbar = QToolBar()
		self.navbar.setMovable(False)
		# make it 50px high
		self.navbar.setIconSize(QSize(50, 50))
		self.addToolBar(self.navbar)

		# back button		
		back_btn = QAction("🠔", self)
		back_btn.triggered.connect(self.backProcess)
		self.navbar.addAction(back_btn)

		# forward button
		forward_btn = QAction("🠖", self)
		forward_btn.triggered.connect(self.forwardProcess)
		self.navbar.addAction(forward_btn)

		# reload button
		self.reload_btn = QAction("⭮", self)
		self.reload_btn.triggered.connect(self.reloadProcess)
		self.navbar.addAction(self.reload_btn)

		# home button
		home_btn = QAction("⌂", self)
		home_btn.triggered.connect(self.homeProcess)
		self.navbar.addAction(home_btn)

		# address bar
		self.address_bar = QLineEdit()
		self.address_bar.setPlaceholderText("Enter URL")
		self.address_bar.returnPressed.connect(lambda: self.browser.setUrl(QUrl(formatUrl(self.address_bar.text()))))
		self.navbar.addWidget(self.address_bar)

		# search bar
		self.search_bar = QLineEdit()
		self.search_bar.setPlaceholderText("Search")
		self.search_bar.returnPressed.connect(lambda: self.browser.setUrl(QUrl(conf["search_engine"].format(query = self.search_bar.text()))))
		self.navbar.addWidget(self.search_bar)

		# load extensions
		self.extensions = []
		self.found_extensions = []
		for ext_fldr in os.listdir(os.path.join(os.path.dirname(__file__), "ext")):
			ext_path = os.path.join(os.path.dirname(__file__), "ext", ext_fldr)
			if os.path.isdir(ext_path):
				self.found_extensions.append(__import__("ext." + ext_fldr + ".main", fromlist=["ext"]))
				# if the extension folder is in config["extensions"]["blacklist"], skip it
				if ext_fldr in conf["extensions"]["blacklist"]:
					print("Skipped extension: " + ext_fldr)
					continue
				self.extensions.append(__import__("ext." + ext_fldr + ".main", fromlist=["ext"]))
				print("Loaded extension: " + ext_fldr)
		# for each extension, call blazeOnApplicationLoad(app, browser, name)
		for ext in self.extensions:
			# check if the extension has the function blazeOnApplicationLoad()
			if hasattr(ext, "blazeOnApplicationLoad"):
				ext.blazeOnApplicationLoad(self, self.browser, ext.__name__.lstrip("ext.").rstrip(".main"))

		# Blazenet menu
		# will have options like quit, about, etc.
		blazenet_menu = self.menuBar().addMenu("Blazenet")
		# about
		about_action = QAction("About", self)
		about_action.triggered.connect(self.aboutProcess)
		blazenet_menu.addAction(about_action)
		# settings
		settings_action = QAction("Settings", self)
		settings_action.triggered.connect(self.settingsProcess)
		blazenet_menu.addAction(settings_action)
		# quit
		quit_action = QAction("Quit", self)
		quit_action.triggered.connect(self.quitProcess)
		blazenet_menu.addAction(quit_action)

		# favourites menu
		self.favourites_menu = self.menuBar().addMenu("Favourites")
		# add favourite
		add_favourite_action = QAction("Add", self)
		add_favourite_action.triggered.connect(self.addFavouriteProcess)
		self.favourites_menu.addAction(add_favourite_action)
		# remove favourite
		remove_favourite_action = QAction("Remove", self)
		remove_favourite_action.triggered.connect(self.removeFavouriteProcess)
		self.favourites_menu.addAction(remove_favourite_action)
		# separator
		self.favourites_menu.addSeparator()
		# favourites
		for favourite in conf["favourites"]:
			fav_action = QAction(favourite["name"], self)
			fav_action.triggered.connect(lambda: self.browser.setUrl(QUrl(favourite["url"])))
			self.favourites_menu.addAction(fav_action)

		# when the page changes, call onPageChangedProcess()
		self.browser.urlChanged.connect(self.onPageChangedProcess)
		# when the browser loads a page, call onPageLoadProcess()
		self.browser.loadFinished.connect(self.onPageLoadProcess)

		self.showMaximized()
	
	def onPageChangedProcess(self):
		# if the url is special (starting with "http://localhost/BLAZECMD/"), call the function associated with the url
		if self.browser.url().toString().startswith("http://localhost/BLAZECMD/"):
			print("Executing command: " + self.browser.url().toString().replace("http://localhost/BLAZECMD/", ""))
			# get the function name
			func_name = self.browser.url().toString().lstrip("http://localhost/BLAZECMD/").split("/")[0]
			args = self.browser.url().toString().lstrip("http://localhost/BLAZECMD/").split("/")[1:]
			# if name = "install-extension", install the extension
			if func_name == "install-extension" and conf["blaze_commands"]["install-extension"]:
				print("Installing extension: " + args[0])
				self.browser.load(QUrl("https://rexxt.github.io/blazenet/ext/installing"))
				# edit window title
				self.setWindowTitle("Blazenet • Installing extension " + args[0] + "...")
				# make url
				url = f"https://github.com/Rexxt/blazenet/raw/gh-pages/ext/{args[0]}/package.zip"
				# download the zip file
				r = requests.get(url, stream = True)
				# extract the zip file to ext/args[0]
				with zipfile.ZipFile(io.BytesIO(r.content)) as zip_file:
					zip_file.extractall(os.path.join(os.path.dirname(__file__), "ext", args[0]))
				# load the single extension
				self.extensions.append(__import__("ext." + args[0] + ".main", fromlist=["ext"]))
				self.found_extensions.append(self.extensions[-1])
				# call blazeOnApplicationLoad()
				if hasattr(self.extensions[-1], "blazeOnApplicationLoad"):
					self.extensions[-1].blazeOnApplicationLoad(self, self.browser, args[0])
				# show info dialog
				QMessageBox.information(self, "Extension installed", f"Extension {args[0]} installed successfully.")
				self.browser.back()
			self.browser.back()

		# for each extension, call blazeOnPageChanged(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnPageChanged()
			if hasattr(ext, "blazeOnPageChanged"):
				ext.blazeOnPageChanged(self, self.browser, self.browser.url().toString(), self.browser.page())

		# set the window title to "Blazenet • " + page title + " • " + url
		self.setWindowTitle("Blazenet • " + self.browser.page().title() + " • " + self.browser.url().toString())

		# set the reload button text to ✖
		self.reload_btn.setText("✖")

		# set the address bar to the url
		self.address_bar.setText(self.browser.url().toString())

	def onPageLoadProcess(self):
		# for each extension, call blazeOnPageLoad(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnPageLoad()
			if hasattr(ext, "blazeOnPageLoad"):
				ext.blazeOnPageLoad(self, self.browser, self.browser.url().toString(), self.browser.page())

		# set the reload button text to ⭮
		self.reload_btn.setText("⭮")
		
		# set the window title to "Blazenet • " + page title + " • " + url
		self.setWindowTitle("Blazenet • " + self.browser.page().title() + " • " + self.browser.url().toString())

	def backProcess(self):
		self.browser.back()
		# for each extension, call blazeOnBack(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnBack()
			if hasattr(ext, "blazeOnBack"):
				ext.blazeOnBack(self, self.browser, self.browser.url().toString(), self.browser.page())
	
	def forwardProcess(self):
		self.browser.forward()
		# for each extension, call blazeOnForward(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnForward()
			if hasattr(ext, "blazeOnForward"):
				ext.blazeOnForward(self, self.browser, self.browser.url().toString(), self.browser.page())
	
	def reloadProcess(self):
		self.browser.reload()
		# for each extension, call blazeOnReload(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnReload()
			if hasattr(ext, "blazeOnReload"):
				ext.blazeOnReload(self, self.browser, self.browser.url().toString(), self.browser.page())
	
	def homeProcess(self):
		self.browser.setUrl(QUrl(conf["homepage"]))
		# for each extension, call blazeOnHome(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnHome()
			if hasattr(ext, "blazeOnHome"):
				ext.blazeOnHome(self, self.browser, self.browser.url().toString(), self.browser.page())
	
	def aboutProcess(self):
		# display the about dialog
		# aka information message box
		QMessageBox.about(self, "About Blazenet", "Blazenet is a light, reliable, extensible and free web browser.\n\nBlazenet is open source software, licensed under the GNU General Public License v3.0.\n\nBlazenet is developed by Mizu.\n\nYou are running version " + BN_VERSION + ".")
	
	def settingsProcess(self):
		# display the settings dialog
		# aka settings window
		self.settings_window = SettingsWindow(self, self.browser, self.found_extensions)
		self.settings_window.show()

	def quitProcess(self):
		# for each extension, call blazeOnQuit(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnQuit()
			if hasattr(ext, "blazeOnQuit"):
				ext.blazeOnQuit(self, self.browser, self.browser.url().toString(), self.browser.page())
		self.close()

	def reloadFavourites(self):
		# remove all favourites
		self.favourites_menu.clear()
		# add favourite
		add_favourite_action = QAction("Add", self)
		add_favourite_action.triggered.connect(self.addFavouriteProcess)
		self.favourites_menu.addAction(add_favourite_action)
		# remove favourite
		remove_favourite_action = QAction("Remove", self)
		remove_favourite_action.triggered.connect(self.removeFavouriteProcess)
		self.favourites_menu.addAction(remove_favourite_action)
		# separator
		self.favourites_menu.addSeparator()
		# favourites
		for favourite in conf["favourites"]:
			fav_action = QAction(favourite["name"], self)
			fav_action.triggered.connect(lambda: self.browser.setUrl(QUrl(favourite["url"])))
			self.favourites_menu.addAction(fav_action)

	def addFavouriteProcess(self):
		# get the name and url from the user
		name, ok = QInputDialog.getText(self, "Add Favourite", "Name:")
		if ok:
			url, ok = QInputDialog.getText(self, "Add Favourite", "URL:")
			if ok:
				# add the favourite to the config
				conf["favourites"].append({"name": name, "url": formatUrl(url)})
				# save the config
				with open(conf_path, "w") as f:
					json.dump(conf, f, indent=4)
				# reload the favourites
				self.reloadFavourites()
				# for each extension, call blazeOnAddFavourite(app, browser, url, page)
				for ext in self.extensions:
					# check if the extension has the function blazeOnAddFavourite()
					if hasattr(ext, "blazeOnAddFavourite"):
						ext.blazeOnAddFavourite(self, self.browser, url, name)
	
	def removeFavouriteProcess(self):
		# get the name and url from the user
		name, ok = QInputDialog.getText(self, "Remove Favourite", "Name:")
		if ok:
			# remove the favourite from the config
			for favourite in conf["favourites"]:
				if favourite["name"] == name:
					conf["favourites"].remove(favourite)
					break
			# save the config
			with open(conf_path, "w") as f:
				json.dump(conf, f, indent=4)
			# reload the favourites
			self.reloadFavourites()
			# for each extension, call blazeOnRemoveFavourite(app, browser, url, page)
			for ext in self.extensions:
				# check if the extension has the function blazeOnRemoveFavourite()
				if hasattr(ext, "blazeOnRemoveFavourite"):
					ext.blazeOnRemoveFavourite(self, self.browser, name)

app = QApplication(sys.argv)
QApplication.setApplicationName("Blazenet")
window = MainWindow()
app.exec_()