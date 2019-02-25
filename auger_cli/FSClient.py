from .LocalFSClient import *


class FSClient:

    def __init__(self, config=None):
        if config is not None and config.awsAccessKeyId:
            from .S3FSClient import S3FSClient
            self.s3fsClient = S3FSClient(config)

        self.localfsClient = LocalFSClient(config)
        if config is not None and hasattr(config, 'dbfsClient'):
            self.dbfsClient = config.dbfsClient

    def _getFSClientByPath(self, path):
        if path.startswith("s3"):
            return self.s3fsClient
        elif path.startswith("dbfs:/"):
            return self.dbfsClient
        else:
            return self.localfsClient

    def createFolder(self, path):
        client = self._getFSClientByPath(path)
        client.createFolder(path)

    def createParentFolder(self, path):
        client = self._getFSClientByPath(path)
        client.createParentFolder(path)

    def getParentFolder(self, path):
        client = self._getFSClientByPath(path)
        return client.getParentFolder(path)

    def removeFolder(self, path, remove_self=True):
        client = self._getFSClientByPath(path)
        client.removeFolder(path, remove_self)

    def removeFile(self, path, wild=False):
        client = self._getFSClientByPath(path)
        client.removeFile(path, wild)

    def saveSingleSCV(self, path, new_path):
        client = self._getFSClientByPath(path)
        client.saveSingleSCV(path, new_path)

    def open(self, path, mode):
        client = self._getFSClientByPath(path)
        return client.open(path, mode)

    def listFolder(self, path, wild=False):
        client = self._getFSClientByPath(path)
        return client.listFolder(path, wild)

    def getMTime(self, path):
        client = self._getFSClientByPath(path)
        return client.getMTime(path)

    @classmethod
    def openFile(cls, config, path, mode):
        if path.startswith("s3"):
            return S3FSClient.openFile(config, path, mode)
        else:
            return open(path, mode)

    def isFileExists(self, path):
        client = self._getFSClientByPath(path)
        return client.isFileExists(path)

    def isDirExists(self, path):
        client = self._getFSClientByPath(path)
        return client.isDirExists(path)

    def readTextFile(self, path):
        client = self._getFSClientByPath(path)
        return client.readTextFile(path)

    def writeTextFile(self, path, data, atomic=False):
        client = self._getFSClientByPath(path)
        client.writeTextFile(path, data, atomic=atomic)

    def writeJSONFile(self, path, data, atomic=False):
        import json
        self.writeTextFile(path, json.dumps(data, allow_nan=False), atomic=atomic)

    def updateJSONFile(self, path, data, atomic=False):
        import json
        fileData = self.readJSONFile(path)
        fileData.update(data)
        self.writeTextFile(path, json.dumps(fileData, allow_nan=False), atomic=atomic)

    def readJSONFile(self, path, check_if_exist=True, wait_for_file=False):
        self.listFolder(self.getParentFolder(path))
        self.waitForFile(path, wait_for_file=wait_for_file)
        if check_if_exist and not self.isFileExists(path):
            return {}

        import json
        return json.loads(self.readTextFile(path))

    def waitForFile(self, path, wait_for_file, num_tries=30, interval_sec=1):
        import time
        if wait_for_file:
            nTry = 0
            while nTry <= num_tries:
                if self.isFileExists(path):
                    break

                nTry = nTry + 1
                time.sleep(interval_sec)

        return self.isFileExists(path)

    def loadJSONFiles(self, paths):
        result = []
        for path in paths:
            try:
                result.append(self.readJSONFile(path))
            except Exception as e:
                print(e)

        return result

    def copyFile(self, path_src, path_dst, check_if_exist=True):
        client = self._getFSClientByPath(path_src)
        if check_if_exist and not client.isFileExists(path_src):
            return

        client.copyFile(path_src, path_dst)

    def copyFiles(self, path_src, path_dst):
        client = self._getFSClientByPath(path_src)
        client.copyFiles(path_src, path_dst)

    def archiveDir(self, path_src, format='zip'):
        client = self._getFSClientByPath(path_src)
        client.archiveDir(path_src,format)

    def copyFolder(self, path_src, path_dst):
        client = self._getFSClientByPath(path_src)
        client.copyFolder(path_src, path_dst)

    def saveObjectToFile(self, obj, path):
        import joblib
        self.removeFile(path)
        self.createParentFolder(path)
        try:
            compress = 0
            if path.endswith('.gz'):
                compress = ('gzip', 3)

            joblib.dump(obj, path, compress=compress)
        except:
            self.removeFile(path)
            raise

    def loadObjectFromFile(self, path):
        import joblib
        return joblib.load(path)


