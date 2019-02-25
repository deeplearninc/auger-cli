import contextlib
import errno
import logging
import os
import os.path
import shutil
import tempfile
import glob
import platform


class LocalFSClient:

    def __init__(self, config=None):
        self.config = config

    def removeFolder(self, path, remove_self=True):
        shutil.rmtree(path, True)
        if not remove_self:
            self.createFolder(path)

    def removeFile(self, path, wild=False):
        try:

            if wild:
                for fl in glob.glob(path):
                    os.remove(fl)
            else:
                os.remove(path)
        except OSError:
            pass

    def isFileExists(self, path):
        return os.path.isfile(path)

    def isDirExists(self, path):
        return os.path.exists(path)

    def saveSingleSCV(self, full_path, new_path):
        listFiles = os.listdir(full_path)

        for item in listFiles:
            if item.endswith(".csv"):
                os.rename(os.path.join(full_path, item), new_path)
                break

        self.removeFolder(full_path)

    def createFolder(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass
            #logging.exception("createFolder failed")
        self.listFolder(self.getParentFolder(path))

    def createParentFolder(self, path):
        parent = os.path.dirname(path)

        try:
            os.makedirs(parent)
        except OSError:
            pass
            #logging.exception("createParentFolder failed")
        self.listFolder(self.getParentFolder(parent))

    def getParentFolder(self, path):
        return os.path.dirname(path)

    def readTextFile(self, path):
        self.listFolder(self.getParentFolder(path))
        with open(path, "r") as file:
            return file.read()

    def writeTextFile(self, path, data, atomic=False):
        self.createParentFolder(path)
        if atomic:
            with self.open_atomic(path, "w") as file:
                file.write(data)
        else:
            with self.open(path, "w") as file:
                try:
                    file.write(data)
                finally:
                    file.flush()  # flush file buffers
                    os.fsync(file.fileno())

        self.readTextFile(path)

    def open(self, path, mode, num_tries=20):
        import time
        nTry = 0
        while nTry <= num_tries:
            try:
                return open(path, mode)
            except Exception as e:
                if nTry >= num_tries:
                    raise

            nTry = nTry + 1
            time.sleep(1)

    def listFolder(self, path, wild=False):
        try:
            if wild:
                return glob.glob(path)
            else:
                return os.listdir(path)
        except OSError:
            pass

        return []

    def getMTime(self, path):
        return os.path.getmtime(path)

    @contextlib.contextmanager
    def open_atomic(self, path, mode):
        parent = self.getParentFolder(os.path.abspath(path))
        temp_dir = tempfile.mkdtemp(dir=parent)
        self.listFolder(parent)
        try:
            temp_path = os.path.join(temp_dir, 'file')
            # logging.info('LocalFSClient.open_atomic: open {}'.format(repr(temp_path)))
            with open(temp_path, mode) as f:
                try:
                    yield f
                finally:
                    f.flush()  # flush file buffers
                    os.fsync(f.fileno())  # ensure all data are written to disk
            # logging.info('LocalFSClient.open_atomic: written {}'.format(repr(temp_path)))
            if platform.system() == "Windows":
                if os.path.exists(path):
                    os.remove(path)

            os.rename(temp_path, path)  # atomic move to target place
            # logging.info('LocalFSClient.open_atomic: renamed {} to {}'.format(repr(temp_path), repr(path)))
        finally:
            shutil.rmtree(temp_dir)
            # logging.info('LocalFSClient.open_atomic: removed {}'.format(repr(temp_dir)))

    @contextlib.contextmanager
    def save_atomic(self, path):
        parent_dir, filename = os.path.split(os.path.abspath(path))
        temp_dir = tempfile.mkdtemp(dir=parent_dir)
        self.listFolder(parent_dir)
        
        try:
            temp_path = os.path.join(temp_dir, filename)
            yield temp_path

            if platform.system() == "Windows":
                if os.path.exists(path):
                    os.remove(path)

            os.rename(temp_path, path)  # atomic move to target place
        finally:
            shutil.rmtree(temp_dir)

    def copyFile(self, path_src, path_dst):
        if self.isFileExists(path_dst):
            self.removeFile(path_dst)

        shutil.copy(path_src, path_dst)

    def copyFiles(self, path_src, path_dst):
        if self.isFileExists(path_dst):
            self.removeFile(path_dst)

        self.createFolder(path_dst)
            
        for fl in glob.glob(path_src):
            shutil.copy(fl, path_dst)

    def copyFolder(self, path_src, path_dst):
        if self.isDirExists(path_dst):
            self.removeFolder(path_dst)

        shutil.copytree(path_src, path_dst)

    def archiveDir(self, path_src, format):
        shutil.make_archive(path_src, format, path_src)
