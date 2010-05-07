import os


def open(url):
    os.system('dbus-send --system --type=method_call --dest="com.nokia.osso_browser" /com/nokia/osso_browser/request com.nokia.osso_browser.load_url string:"%s"' % url)
