import os.path, os
import gdapi
import datetime
import gdfile

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

        if not os.path.exists(fullpath):
            print(f"{fullpath} did not exist in cache, download data")

            # get_file will download the file to 'fullpath'
            gdapi.get_file(self.gdservice, gfile.id, destination=fullpath)

            print(f"Downloaded {gfile.id} to {fullpath}")
        else:
            metadata = gdapi.get_metadata(self.gdservice, gfile.id)
            meta_gfile = gdfile.File(fullpath, metadata)

            # GD gives timestamps in UTC, so we need to calc back
            cache_mtime = datetime.datetime.utcfromtimestamp(os.path.getmtime(fullpath))
            gd_mtime = datetime.datetime.fromtimestamp(meta_gfile.mtime)

            if gd_mtime > cache_mtime:
                print(f"{fullpath} exists in cache, but is older than online version; redownloading; cache mtime={cache_mtime}, gd mtime={gd_mtime}")
                gdapi.get_file(self.gdservice, gfile.id, destination=fullpath)
            else:
                print(f"{fullpath} exists in cache; cache mtime={cache_mtime}, gd mtime={gd_mtime}")

        fd = os.open(fullpath, flags)
        print(f"{fullpath} got fd {fd}")
        return fd
