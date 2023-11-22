from apfs.apfs import *

from PyQt5.QtCore import pyqtSignal, QObject

from datetime import datetime
from typing import Dict
import hashlib
import pytz
import os


class SignalEmitter(QObject):
    finished_signal = pyqtSignal(str)


class FileAnalyzer:
    BUFSIZ = (2**10)*(2**10)*16

    def __init__(self, file_path):
        super().__init__()        
        self.algorithms = ('md5', 'sha256', 'sha512')
        self.file_path = file_path
        self.basic_information = {}
        self.file = None
        self.apfs_data = None


    def analyze(self):
        self.file = open(self.file_path, 'rb')
        self.apfs_data = Apfs(self.file)
        for vi in self.apfs_data.volume_info:
            print(f'volume_info: {vi}')
        
    def generate_basic_information(self):
        self.basic_information.update(self.get_hash())
        self.basic_information['timestamp'] = datetime.now(pytz.utc)
        self.basic_information['filepath'] = self.file_path
        self.basic_information['filename'] = os.path.basename(self.file_path)
        self.basic_information['size'] = os.path.getsize(self.file_path)
        
    def get_hash(self) -> Dict[str, str]:
        result = dict()

        for algorithm in self.algorithms:
            result[algorithm] = hashlib.new(algorithm)

        with open(self.file_path, 'rb') as f:
            while data := f.read(self.BUFSIZ):
                for key in result:
                    result[key].update(data)

        for key in result:
            result[key] = result[key].hexdigest()

        return result

    def calculate_file_hash(self, hash_algorithm) -> str:
        with open(self.file_path, 'rb') as f:
            hash_obj = hashlib.new(hash_algorithm)

            while data := f.read(self.BUFSIZ):
                hash_obj.update(data)

        return hash_obj.hexdigest()

    def close(self):
        self.file.close()