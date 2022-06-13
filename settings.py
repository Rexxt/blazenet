import sys, os, json, requests, zipfile, io
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

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

# settings window
# tab view:
# - general
# - extensions
# create window
class SettingsWindow(QDialog):
	def __init__(self, app, browser, extensions):
		super().__init__()
		self.app = app
		self.browser = browser
		self.extensions = extensions
		self.did_extensions_change = False
		self.conf_copy = deepcopy(conf)
		self.initUI()

	def initUI(self):
		# set window title
		self.setWindowTitle("Settings")

		# create tab view
		self.tab_view = QTabWidget()

		# create general tab
		self.general_tab = QWidget()

		# create general layout
		self.general_layout = QVBoxLayout()

		# we'll need a label "Homepage" and a line edit for the homepage
		self.general_homepage_label = QLabel("Homepage:")
		self.general_homepage_line_edit = QLineEdit(conf["homepage"])

		# add the label and line edit to the general layout
		self.general_layout.addWidget(self.general_homepage_label)
		self.general_layout.addWidget(self.general_homepage_line_edit)

		# and now, a label "Search engine with {query}" and a line edit for the search engine
		self.general_search_engine_label = QLabel("Search engine with {query}:")
		self.general_search_engine_line_edit = QLineEdit(conf["search_engine"])

		self.general_layout.addWidget(self.general_search_engine_label)
		self.general_layout.addWidget(self.general_search_engine_line_edit)

		# add the general layout to the general tab
		self.general_tab.setLayout(self.general_layout)

		# add the general tab to the tab view
		self.tab_view.addTab(self.general_tab, "General")


		# create extensions tab
		self.extensions_tab = QWidget()

		# create extensions layout
		self.extensions_layout = QVBoxLayout()

		# create label "Extensions"
		self.extensions_label = QLabel("Extensions:")

		# create a list view with checkboxes for each extension
		self.extensions_list_view = QListWidget()

		# fill the list view with the extensions
		for ext in self.extensions:
			ext_name = ext.__name__.split(".")[1]
			ext_item = QListWidgetItem(ext_name)
			ext_item.setCheckState(Qt.Unchecked if ext_name in conf["extensions"]["blacklist"] else Qt.Checked)
			ext_item._name = ext_name
			self.extensions_list_view.addItem(ext_item)
		
		# add the label and list view to the extensions layout
		self.extensions_layout.addWidget(self.extensions_label)
		self.extensions_layout.addWidget(self.extensions_list_view)

		# make a checkbox with label "Enable live installation of extensions"
		self.extensions_live_install_checkbox = QCheckBox("Enable live installation of extensions")
		self.extensions_live_install_checkbox.setChecked(conf["blaze_commands"]["install-extension"])

		# connect the checkbox to the live installation function
		self.extensions_live_install_checkbox.stateChanged.connect(self.extensionsLiveInstallChanged)

		# add the checkbox to the extensions layout
		self.extensions_layout.addWidget(self.extensions_live_install_checkbox)

		# add the extensions layout to the extensions tab
		self.extensions_tab.setLayout(self.extensions_layout)

		# add the extensions tab to the tab view
		self.tab_view.addTab(self.extensions_tab, "Extensions")

		# create buttons
		self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		# add the buttons to the layout
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.tab_view)
		self.layout.addWidget(self.buttons)
		# add the layout to the window
		self.setLayout(self.layout)
		# connect the buttons to the slots
		self.buttons.accepted.connect(self.accept)
		self.buttons.rejected.connect(self.reject)
		# connect the list view to the slot
		self.extensions_list_view.itemChanged.connect(self.extensionsListViewItemChanged)
		# connect the line edits to the slots
		self.general_homepage_line_edit.textChanged.connect(self.generalHomepageLineEditTextChanged)
		self.general_search_engine_line_edit.textChanged.connect(self.generalSearchEngineLineEditTextChanged)
		# show the window
		self.show()
	
	def extensionsListViewItemChanged(self, item):
		# get the name of the extension
		ext_name = item._name
		# if the extension is in the blacklist, remove it
		if ext_name in self.conf_copy["extensions"]["blacklist"]:
			self.conf_copy["extensions"]["blacklist"].remove(ext_name)
		# if the extension is not in the blacklist, add it
		else:
			self.conf_copy["extensions"]["blacklist"].append(ext_name)
		self.did_extensions_change = True
	
	def generalHomepageLineEditTextChanged(self, text):
		self.conf_copy["homepage"] = text
	
	def generalSearchEngineLineEditTextChanged(self, text):
		self.conf_copy["search_engine"] = text
	
	def extensionsLiveInstallChanged(self, state):
		self.conf_copy["blaze_commands"]["install-extension"] = bool(state)

	def accept(self):
		# save the config
		with open(conf_path, "w") as f:
			json.dump(self.conf_copy, f, indent=4)
		# copy the config to the global conf
		global conf
		conf = deepcopy(self.conf_copy)
		# if the extensions changed, restart the browser
		if self.did_extensions_change:
			os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
		# for each extension, call blazeOnSettingsChanged(app, browser, url, page)
		for ext in self.extensions:
			# check if the extension has the function blazeOnSettingsChanged()
			if hasattr(ext, "blazeOnSettingsChanged"):
				ext.blazeOnSettingsChanged(self.app)
		# close the window
		self.close()