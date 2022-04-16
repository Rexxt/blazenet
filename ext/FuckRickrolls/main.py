# simple extension that redirects the user to the youtube home page when they are being rickrolled
# because let's be honest, fuck rickrolls
from PyQt5.QtCore import QUrl

rickrolls_this_session = 0

def blazeOnPageLoad(app, browser, url, page):
    global rickrolls_this_session
    if url.startswith("https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        # the user is being rickrolled
        rickrolls_this_session += 1
        print('Saved {} rickrolls this session'.format(rickrolls_this_session))
        # redirect to the youtube home page
        browser.setUrl(QUrl("https://www.youtube.com"))