import os.path, os
import gdapi

class Cache:
    def __init__(self, cachedir, gdservice):
        self.cachedir = cachedir
        self.gdservice = gdservice
        print(f"Initialised cache at {self.cachedir}")

    def open(self, gfile, flags):
        fullpath = os.path.join(self.cachedir, gfile.path[1:])
        fulldir = os.path.dirname(fullpath)

        # make sure our target dir exists
        os.makedirs(fulldir, exist_ok = True)
        # print(f"{gfile.mtime} {os.path.getmtime(fullpath)}")
        # if gfile.mtime > os.path.getmtime(fullpath):
        #     print(f"Online file is newer, delete cache file {fullpath}")

        if not os.path.exists(fullpath):
            print(f"{fullpath} did not exist, download data")
            content = gdapi.get_file(self.gdservice, gfile.id, destination=fullpath)

            # with open(fullpath, "wb") as f:
            #     f.write(content)

            print(f"Downloaded {gfile.id} to {fullpath}")

        return os.open(fullpath, flags)
