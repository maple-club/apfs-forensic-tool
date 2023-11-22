from .signature import *
from .gpt import *
from .keydata import *
from .exceptions import *

from typing import BinaryIO

class Apfs:
    def __init__(self, f):
        self.f: BinaryIO = f
        self.fname = str(self.f)[26:-2].split('\\')[-1]
        self.root_id: str = None
        self.volume_name: str = None
        self.volume_info = [] # VCSB, BTOM, EBT, root_id, volume_name

        self.apfs_signature: str = None
        self.vcsb_signature: str = None

        self.msb: int = None
        self.vs: int = None
        self.vcsb: int = None
        self.btom: int = None
        self.ebt: int = None

        self.set_addr()


    def set_addr(self):
        self.set_msb_addr()
        self.print_info()


    def set_msb_addr(self):
        # self.msb = 0xC805000
        self.msb = get_part(self.f)
        self.f.seek(self.msb)

        data = self.f.read(0xB0)
        self.apfs_signature = struct.unpack_from('>I', data, 0x0 + 0x20)[0]
        if not apfs_check_signature(self.apfs_signature):
            raise InvalidApfsFileException(self.fname, self.apfs_signature)

        self.block_size = struct.unpack_from('<I', data, 0x0 + 0x24)[0]
        self.set_vs_addr()

    def set_vs_addr(self):
        self.f.seek(self.msb)

        data = self.f.read(0xB0)
        offset = struct.unpack_from('<I', data, 0x0 + 0xA0)[0]
        self.f.seek(self.msb + (offset*self.block_size))

        data = self.f.read(self.block_size)
        offset = struct.unpack_from('<I', data, 0x0 + 0x30)[0]

        self.vs = self.msb + (self.block_size*offset)

        self.set_vcsb_addr()

    def set_vcsb_addr(self):
        self.f.seek(self.vs)
        # data = self.f.read(self.block_size)
        kd = KeyData(self, self.vs)
        tmp_kd = kd.key_data
        tmp_kd = list(set([tuple(set(tmp)) for tmp in tmp_kd]))

        for i in tmp_kd:
            if len(i) < 2:
                continue
            self.f.seek(self.vs + self.block_size - 0x28 - i[1] + 8)
            # self.f.read(8)
            offset = int.from_bytes(self.f.read(8)[::-1], byteorder='big')
            self.vcsb = self.msb + (self.block_size*offset)
            self.set_btom_ebt_addr()
            self.volume_info.append([self.vcsb, self.btom, self.ebt, self.root_id, self.volume_name])

    def set_btom_ebt_addr(self):
        self.f.seek(self.vcsb)
        data = self.f.read(self.block_size)
        self.vcsb_signature = struct.unpack_from('>I', data, 0x0 + 0x20)[0]
        if not vcsb_check_signature(self.vcsb_signature):
            raise InvalidVcsbSignatureException(self.fname, self.vcsb_signature)

        btom_offset = struct.unpack_from('<I', data, 0x0 + 0x80)[0]
        self.root_id = struct.unpack_from('<I', data, 0x0 + 0x88)[0]
        ebt_offset = struct.unpack_from('<I', data, 0x0 + 0x90)[0]

        self.f.seek(self.msb + self.block_size*btom_offset)

        data = self.f.read(self.block_size)
        btom_offset = struct.unpack_from('<I', data, 0x0 + 0x30)[0]
        self.btom = self.msb + self.block_size*btom_offset
        self.ebt = self.msb + self.block_size*ebt_offset
        self.f.seek(self.vcsb + 0x2C0)
        self.volume_name = str(self.f.read(self.block_size - 0x2C0)).split('\\x00')[0][2:]


    def print_info(self):
        print('-----------------------------------------------')
        print(f'File name:\t{self.fname}')
        print(f'Block size:\t{hex(self.block_size)}')
        print(f'MSB addr:\t{hex(self.msb)}')
        print(f'VS addr:\t{hex(self.vs)}')
        print('-----------------------------------------------')
        for vi in self.volume_info:
            print(f'Volume name:\t{str(vi[4])}')
            print(f'Root ID:\t{hex(vi[3])}')
            print(f'VCSB addr:\t{hex(vi[0])}')
            print(f'BTOM addr:\t{hex(vi[1])}')
            print(f'EBT addr:\t{hex(vi[2])}')
            print('-----------------------------------------------')