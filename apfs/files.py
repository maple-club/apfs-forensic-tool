from .keydata import *
from .datatype import *

from apfs.apfs import Apfs

class File:

    def __init__(
            self,
            apfs: Apfs,
            volume_info,
            node_id_offset
    ):
        kdl = KeyDataLen(apfs, volume_info[2])
        self.node_id = []
        self.set_file_id_offset(apfs, kdl, volume_info)

        node_id = []
        self.file_info = []
        for nio in node_id_offset:
            if nio[0] == volume_info[3]:
                continue
            kdl = KeyDataLen(apfs, apfs.msb + (nio[1]*apfs.block_size))
            self.set_file_info(apfs, kdl, nio, node_id)


        # must not be set because of IndexError
        self.file_id_lst = []
        dup = []
        for i in range(len(self.file_info)):
            if self.file_info[i][1] in self.file_id_lst:
                dup.append(i)
            else:
                self.file_id_lst.append(self.file_info[i][1])
        dup.reverse()
        for i in dup:
            del self.file_info[i]

    def set_file_id_offset(
            self,
            apfs: Apfs,
            kdl: KeyDataLen,
            volume_info
    ):
        file_id_offset = []
        for i in kdl.key_data_len:
            apfs.f.seek(volume_info[2] + 0x38 + kdl.size + i[0])
            offset = int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            apfs.f.seek(volume_info[2] + apfs.block_size - 0x28 - i[2])
            apfs.f.read(8)  #unknown
            file_id = int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            apfs.f.read(4)  #unknown
            file_id_offset.append((file_id, offset))

        self.file_id_offset = file_id_offset

    def set_file_info(
            self,
            apfs: Apfs,
            kdl: KeyDataLen,
            node_id_offset,
            node_id: List
    ):
        if node_id_offset[0] in node_id:
            return
        else:
            node_id.append(node_id_offset[0])
        apfs.f.seek(apfs.msb + (node_id_offset[1]*apfs.block_size) + 0x38 + kdl.size + kdl.key_data_len[0][0])
        tmp_file_id = int.from_bytes(apfs.f.read(7)[::-1], byteorder='big')
        type30_data = None
        type40_data = None
        type60_data = None
        type80_data = None
        type90_data = None
        for i in kdl.key_data_len:
            apfs.f.seek(apfs.msb + (node_id_offset[1]*apfs.block_size) + 0x38 + kdl.size + i[0])
            file_id = int.from_bytes(apfs.f.read(7)[::-1], byteorder='big')
            file_type = int.from_bytes(apfs.f.read(1)[::-1], byteorder='big')
            if i == kdl.key_data_len[-1] or file_id != tmp_file_id:
                tmp_file_id = file_id

                if type30_data is None:
                    type30_data = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                if type30_data[12] == '':
                    continue
                if type40_data is None:
                    type40_data = [None]
                if type60_data is None:
                    type60_data = [None]
                if type80_data is None:
                    type80_data = [None, None]
                if type90_data is None:
                    type90_data = [None, None]

                self.file_info.append(type30_data + type40_data + type60_data + type80_data + type90_data)
                type30_data = None
                type40_data = None
                type60_data = None
                type80_data = None
                type90_data = None
            
            if file_type == 0x30:
                file_data = Type30()
                file_data.set_data(apfs, apfs.msb + (node_id_offset[1]*apfs.block_size) + apfs.block_size - i[2])
                type30_data = file_data.get_data()
            elif file_type == 0x40:
                file_data = Type40()
                file_data.set_data(apfs, apfs.msb + (node_id_offset[1]*apfs.block_size) + apfs.block_size - i[2])
                type40_data = file_data.get_data()
            elif file_type == 0x60:
                file_data = Type60()
                file_data.set_data(apfs, apfs.msb + (node_id_offset[1]*apfs.block_size) + apfs.block_size - i[2])
                type60_data = file_data.get_data()
            elif file_type == 0x80:
                file_data = Type80()
                file_data.set_data(apfs, apfs.msb + (node_id_offset[1]*apfs.block_size) + apfs.block_size - i[2])
                type80_data = file_data.get_data()
            elif file_type == 0x90:
                file_data = Type90()
                file_data.set_data(apfs, apfs.msb + (node_id_offset[1]*apfs.block_size) + apfs.block_size - i[2])
                type90_data = file_data.get_data()
