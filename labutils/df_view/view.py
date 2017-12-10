import os
import tempfile
import webbrowser

import threading
import subprocess as sub

import pandas
from labutils import clip_df
from chromote import Chromote


# TODO: Use named temporary files instead of janky package subdir
# TODO: Read https://docs.python.org/3/library/tempfile.html


class DFView(object):
    def __init__(self, df: pandas.DataFrame):
        self.name = NotImplemented
        self.file = tempfile.NamedTemporaryFile(suffix='.html')
        self.df = df
        sub.call(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '-remote-debugging-port=9222'])
        self.chrome = Chromote()
        self.tab = self.chrome.tabs[0]
        self.tab.set_url('file:' + self.file.name)

    def refresh(self):
        self.file.write(clip_df(self.df, 'material').encode())
        self.file.seek(0)
        self.tab.reload()

