# blazenet
Light, reliable, extensible and free web browser.

## Features
### Implemented
- Config file
- Settings menu
- Favourites
- Extension system with 10 events as of version 0.0.1a-0
- Navigation bar with controls including a home button redirecting to a user-set homepage, URL bar with automatic prefix addition (adds `http://` if prefix is left out) and search bar with customizable search engine
### Previewed
- Website Hold Rack to store links for later use in the current session
- Preinstalled adblocking extension

## Extension framework
### Getting started
Writing an extension for blazenet is very easy.

First, in `ext/`, create a folder with the name of your choice. This will be the name of the extension. Your folder name may not contain spaces or slashes.
Then, in that folder, create a `main.py` file. This is the core of the extension, that will be loaded by the browser when it starts.

You will be able to use numerous event handlers in your extension.

### Events
An event is a function starting with `blaze` that will be called when an event in the browser is triggered. Here are the available ones
#### `blazeOnApplicationLoad(app: QMainWindow, browser: QWebEngineView, name: str)`
Called when the application loads the extension. For clarification, `name` is the name of the extension.

#### `blazeOnPageChanged(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the browser switches to a different page.

#### `blazeOnPageLoad(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when a page loads.

#### `blazeOnBack(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the back button is pressed.

#### `blazeOnForward(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the forward button is pressed.

#### `blazeOnReload(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the reload button is pressed.

#### `blazeOnHome(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the home button is pressed.

#### `blazeOnQuit(app: QMainWindow, browser: QWebEngineView, url: str, page: QWebEnginePage)`
Called when the browser is closed via the Blazenet menu.

#### `blazeOnAddFavourite(app: QMainWindow, browser: QWebEngineView, url: str, name: str)`
Called when a favourite is added.

#### `blazeOnRemoveFavourite(app: QMainWindow, browser: QWebEngineView, url: str, name: str)`
Called when a favourite is removed.

#### `blazeOnSettingChanged(app: QMainWindow)`
Called when the settings change.
