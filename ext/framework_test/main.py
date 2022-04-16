def blazeOnApplicationLoad(app, browser, name):
    print("Extension framework: blazeOnApplicationLoad()")

def blazeOnPageLoad(app, browser, url, page):
    print("Extension framework: blazeOnPageLoad() called")

def blazeOnBack(app, browser, url, page):
    print("Extension framework: blazeOnBack() called")

def blazeOnForward(app, browser, url, page):
    print("Extension framework: blazeOnForward() called")

def blazeOnReload(app, browser, url, page):
    print("Extension framework: blazeOnReload() called")

def blazeOnHome(app, browser, url, page):
    print("Extension framework: blazeOnHome() called")

def blazeOnQuit(app, browser, url, page):
    print("Extension framework: blazeOnQuit() called")

def blazeOnAddFavourite(app, browser, url, page):
    print("Extension framework: blazeOnAddFavourite() called")

def blazeOnRemoveFavourite(app, browser, url, page):
    print("Extension framework: blazeOnRemoveFavourite() called")

def blazeOnSettingChanged(app):
    print("Extension framework: blazeOnSettingChanged() called")