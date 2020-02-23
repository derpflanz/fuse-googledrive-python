# this gdfile module has all the classes and functionality
# for processing what comes from the API

import sys, datetime, time
import stat
import os.path, os

# the File class abstracts the metadata from the GD API
# it also has some handy methods to define stuff

# {'kind': 'drive#file', 
# 'id': '1GvwvfgHdWm6BCamunwU8hXgwjeCU3LpS', 
# 'name': 'einsteins-logic-puzzle.ods', 
# 'mimeType': 'application/vnd.oasis.opendocument.spreadsheet', 
# 'parents': ['0ADZoyBWeSfDNUk9PVA'], 
# 'spaces': ['drive'], 
# 'viewedByMeTime': '2019-03-21T08:03:34.750Z', 
# 'createdTime': '2019-03-21T08:03:13.074Z', 
# 'modifiedByMeTime': '2009-10-19T15:30:40.000Z', 
# 'size': '42274'}


class File:
    mimeType = None
    size = 0

    # make a timestamp to be used in atime, ctime, mtime
    def make_timestamp(self, name):
        t = None
        if name in self.gdinfo:
            t = datetime.datetime.strptime(self.gdinfo[name], "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            t = datetime.datetime.now()

        return int(time.mktime(t.timetuple()))

    def is_directory(self):
        r = False
        try:
            if self.gdinfo['kind'] == "drive#file" and self.gdinfo['mimeType'] == 'application/vnd.google-apps.folder':
                r = True
        except:
            r = False

        return r

    def open(self, cachedir):
        fullpath = os.path.join(cachedir, self.path)

        print(f"Cached file should be at {fullpath}")
        fulldir = os.path.dirname(fullpath)
        os.mkdirs(fulldir, exist_ok = True)

    def __init__(self, path, gdinfo):
        self.gdinfo = gdinfo

        self.mimeType = gdinfo['mimeType']
        self.size = 0 if 'size' not in gdinfo else int(gdinfo['size'])
        self.atime = self.make_timestamp('viewedByMeTime')
        self.ctime = self.make_timestamp('createdTime')
        self.mtime = self.make_timestamp('modifiedByMeTime')
        self.parents = gdinfo['parents']
        self.id = gdinfo['id']
        self.path = path

        if self.is_directory():
            self.mode = stat.S_IFDIR
        else:
            self.mode = stat.S_IFREG

        self.mode |= 0o000644