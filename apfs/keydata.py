#from .apfs import Apfs
from typing import List, Tuple

# BTOM
class KeyData:
    # global key_data  # list
    # global size
    def __init__(
            self,
            apfs,
            addr: int
    ):
        self.size = None
        self.key_data = None
        self.set_key_data(apfs, addr)

    def set_key_data(
            self,
            apfs,
            addr: int
    ):
        apfs.f.seek(addr + 0x2A)
        self.size = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')

        apfs.f.seek(addr + 0x38)
        key_data = []
        for _ in range(self.size//4):
            key_offset = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            data_offset = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            key_data.append((key_offset, data_offset))
    
        self.key_data = key_data

# EBT, node
class KeyDataLen:
    # global key_data_len  # list
    # global size
    def __init__(
            self,
            apfs,
            addr: int
    ):
        self.size: int = None
        self.key_data_len: List[Tuple] = None
        self.set_key_data_len_offset(apfs, addr)

    def set_key_data_len_offset(
            self,
            apfs,
            addr: int
    ):
        apfs.f.seek(addr + 0x2A)
        self.size = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')

        apfs.f.seek(addr + 0x38)
        key_data_len = []
        for _ in range(self.size//8):
            key_offset = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            key_len = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')

            data_offset = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            data_len = int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')

            key_data_len.append((key_offset, key_len, data_offset, data_len))

        self.key_data_len = key_data_len

