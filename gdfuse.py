#!/usr/bin/env python

from __future__ import with_statement

import os, time
import sys, stat
import errno
from fuse import FUSE, FuseOSError, Operations
import gdapi, gdfile, gdcache

class GoogleDriveFuse(Operations):
    def __init__(self, mountpoint, cachedir, gdroot):
        self.timestamp = int(time.time())
        self.gid = os.getgid()
        self.uid = os.getuid()
        self.cachedir = cachedir
        st = os.stat(mountpoint)
        self.mountpoint_stat = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        self.gd_service = gdapi.get_drive_service()
        self.file_list = {}
        self.gdroot = gdroot
        self.cache = gdcache.Cache(cachedir, self.gd_service)

    def readdir(self, path, fh):
        dirents = ['.', '..']

        if path == "/":
            parent = self.gdroot
        else:
            gfile = self.file_list[path]
            parent = gfile.id

        items = gdapi.get_files(self.gd_service, 100, parent=parent)

        for item in items:
            p = os.path.join(path, item['name'])
            self.file_list[p] = gdfile.File(p, item)
            dirents.append(item['name'])

        for r in dirents:
            yield r

    # this decides access, for now, we allow everything
    # raise EPERM when it fails
    def access(self, path, mode):
        print(f"Accessing file {path}, mode {mode}")

    def getattr(self, path, fh=None):
        # When the root is asked, just return the mountpoint's stats
        if path == '/':
            r = self.mountpoint_stat
        else:
            if path not in self.file_list:
                raise FuseOSError(errno.ENOENT)

            fullpath = os.path.join(self.cachedir, path[1:])
            if os.path.exists(fullpath):
                # file was in cache, fetch actual stat
                stat = os.stat(fullpath)
                r = {
                    'st_atime': stat.st_atime,
                    'st_ctime': stat.st_ctime,
                    'st_gid': self.gid,
                    'st_uid': self.uid,
                    'st_mode': stat.st_mode,
                    'st_mtime': stat.st_mtime,
                    'st_nlink': 1,
                    'st_size': stat.st_size
                }
            else:
                # fetch stats from our file_list 
                gfile = self.file_list[path]

                r = {
                    'st_atime': gfile.atime,
                    'st_ctime': gfile.ctime,
                    'st_gid': self.gid,
                    'st_uid': self.uid,
                    'st_mode': gfile.mode,
                    'st_mtime': gfile.mtime,
                    'st_nlink': 1,
                    'st_size': gfile.size
                }

        return r

    def statfs(self, path):
        # we just make up some stuff, until we run into an issue
        return {
            'f_bsize': 4096,    # system block size
            'f_frsize': 4096,   # fragment size
            'f_blocks': 100,    # size in frsize units
            'f_bfree': 100,     # free blocks
            'f_bavail': 100,    # available for unpriv users
            'f_files': 10,      # number of inodes
            'f_free': 10,       # free inodes
            'f_favail': 10,     # free inodes for unpriv users
            'f_flag': 0,        # mount flags
            'f_namemax': 255    # max length name
        }

    # Helpers
    # =======
    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================
    def chmod(self, path, mode):
        raise FuseOSError(errno.ENOSYS)

    def chown(self, path, uid, gid):
        raise FuseOSError(errno.ENOSYS)

    def readlink(self, path):
        raise FuseOSError(errno.ENOSYS)

    def mknod(self, path, mode, dev):
        raise FuseOSError(errno.ENOSYS)

    def rmdir(self, path):
        raise FuseOSError(errno.ENOSYS)

    def mkdir(self, path, mode):
        raise FuseOSError(errno.ENOSYS)

    def unlink(self, path):
        raise FuseOSError(errno.ENOSYS)

    def symlink(self, name, target):
        raise FuseOSError(errno.ENOSYS)

    def rename(self, old, new):
        raise FuseOSError(errno.ENOSYS)

    def link(self, target, name):
        raise FuseOSError(errno.ENOSYS)

    def utimens(self, path, times=None):
        raise FuseOSError(errno.ENOSYS)

    # File methods
    # ============
    def open(self, path, flags):
        gfile = self.file_list[path]
        return self.cache.open(gfile, flags)

    def create(self, path, mode, fi=None):
        raise FuseOSError(errno.ENOSYS)

    def read(self, path, length, offset, fh):
        # because our actual data reading and writing is done on a temp
        # file, we can just use the file handle
        print(f"Reading {length} bytes from offset {offset} of {path}; fh={fh}")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        # because our actual data reading and writing is done on a temp
        # file, we can just use the file handle
        print(f"Writing {len(buf)} bytes to offset {offset} of {path}; fh={fh}")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        raise FuseOSError(errno.ENOSYS)

    # https://stackoverflow.com/questions/2340610/difference-between-fflush-and-fsync
    # figure this out, it might not be necessary, as we auto-sync on release()
    def flush(self, path, fh):
        # flush would sync the file back to Google Drive, 
        # if not done yet
        return 
    def fsync(self, path, fdatasync, fh):
        return

    def release(self, path, fh):
        # TODO on release (close), we sync back to Google Drive
        print(f"Releasing {path}: {fh}")
        os.close(fh)
        return



def main(mountpoint, cachedir):
    public = '0AEiFbfoNsaBzUk9PVA'
    mydrive = '0ADZoyBWeSfDNUk9PVA'
    FUSE(GoogleDriveFuse(mountpoint, cachedir, gdroot = mydrive), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])