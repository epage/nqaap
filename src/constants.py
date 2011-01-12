import os

__pretty_app_name__ = "nQaap"
__app_name__ = "nqaap"
__version__ = "0.8.8"
__build__ = 0
__app_magic__ = 0xdeadbeef
_data_path_ = os.path.join(os.path.expanduser("~"), ".%s" % __app_name__)
_user_settings_ = "%s/settings.ini" % _data_path_
_user_logpath_ = "%s/%s.log" % (_data_path_, __app_name__)
_default_book_path_ = os.path.join(os.path.expanduser("~"), "MyDocs/Audiobooks/")
