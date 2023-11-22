class InvalidApfsFileException(Exception):
    def __init__(self, name, signature):
        super().__init__(f'\'{name}\' is not APFS File: {signature}')
        self.file_name = name
        self.signature = signature

class InvalidVcsbSignatureException(Exception):
    def __init__(self, name, signature):
        super().__init__(f'\'{name}\' has wrong VCSB Signature: {signature}')
        self.file_name = name
        self.signature = signature